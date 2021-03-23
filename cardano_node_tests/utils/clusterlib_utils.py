import itertools
import json
import logging
from pathlib import Path
from typing import Any
from typing import List
from typing import NamedTuple
from typing import Optional
from typing import Union

from cardano_clusterlib import clusterlib

from cardano_node_tests.utils import helpers
from cardano_node_tests.utils.types import FileType

LOGGER = logging.getLogger(__name__)


class UpdateProposal(NamedTuple):
    arg: str
    value: Any
    name: str = ""


class TokenRecord(NamedTuple):
    token: str
    asset_name: str
    amount: int
    issuers_addrs: List[clusterlib.AddressRecord]
    token_mint_addr: clusterlib.AddressRecord
    script: Path


def deregister_stake_addr(
    cluster_obj: clusterlib.ClusterLib, pool_user: clusterlib.PoolUser, name_template: str
) -> clusterlib.TxRawOutput:
    """Deregister stake address."""
    # files for deregistering stake address
    stake_addr_dereg_cert = cluster_obj.gen_stake_addr_deregistration_cert(
        addr_name=f"{name_template}_addr0_dereg", stake_vkey_file=pool_user.stake.vkey_file
    )
    tx_files_deregister = clusterlib.TxFiles(
        certificate_files=[stake_addr_dereg_cert],
        signing_key_files=[pool_user.payment.skey_file, pool_user.stake.skey_file],
    )

    # withdraw rewards to payment address
    cluster_obj.withdraw_reward(
        stake_addr_record=pool_user.stake,
        dst_addr_record=pool_user.payment,
        tx_name=name_template,
    )

    tx_raw_output = cluster_obj.send_tx(
        src_address=pool_user.payment.address,
        tx_name=f"{name_template}_dereg_stake_addr",
        tx_files=tx_files_deregister,
    )
    cluster_obj.wait_for_new_block(new_blocks=2)
    return tx_raw_output


def fund_from_genesis(
    *dst_addrs: str,
    cluster_obj: clusterlib.ClusterLib,
    amount: int = 2_000_000,
    tx_name: Optional[str] = None,
    destination_dir: FileType = ".",
) -> None:
    """Send `amount` from genesis addr to all `dst_addrs`."""
    fund_dst = [
        clusterlib.TxOut(address=d, amount=amount)
        for d in dst_addrs
        if cluster_obj.get_address_balance(d) < amount
    ]
    if not fund_dst:
        return

    with helpers.FileLockIfXdist(f"{helpers.get_basetemp()}/{cluster_obj.genesis_utxo_addr}.lock"):
        tx_name = tx_name or helpers.get_timestamped_rand_str()
        tx_name = f"{tx_name}_genesis_funding"
        fund_tx_files = clusterlib.TxFiles(
            signing_key_files=[
                *cluster_obj.genesis_keys.delegate_skeys,
                cluster_obj.genesis_keys.genesis_utxo_skey,
            ]
        )

        cluster_obj.send_funds(
            src_address=cluster_obj.genesis_utxo_addr,
            destinations=fund_dst,
            tx_name=tx_name,
            tx_files=fund_tx_files,
            destination_dir=destination_dir,
        )
        cluster_obj.wait_for_new_block(new_blocks=2)


def return_funds_to_faucet(
    *src_addrs: clusterlib.AddressRecord,
    cluster_obj: clusterlib.ClusterLib,
    faucet_addr: str,
    amount: int = -1,
    tx_name: Optional[str] = None,
    destination_dir: FileType = ".",
) -> None:
    """Send `amount` from all `src_addrs` to `faucet_addr`.

    The amount of "-1" means all available funds.
    """
    tx_name = tx_name or helpers.get_timestamped_rand_str()
    tx_name = f"{tx_name}_return_funds"
    with helpers.FileLockIfXdist(f"{helpers.get_basetemp()}/{faucet_addr}.lock"):
        try:
            logging.disable(logging.ERROR)
            for src in src_addrs:
                fund_dst = [clusterlib.TxOut(address=faucet_addr, amount=amount)]
                fund_tx_files = clusterlib.TxFiles(signing_key_files=[src.skey_file])
                # try to return funds; don't mind if there's not enough funds for fees etc.
                try:
                    cluster_obj.send_funds(
                        src_address=src.address,
                        destinations=fund_dst,
                        tx_name=tx_name,
                        tx_files=fund_tx_files,
                        destination_dir=destination_dir,
                    )
                    cluster_obj.wait_for_new_block(new_blocks=2)
                except Exception:
                    pass
        finally:
            logging.disable(logging.NOTSET)


def fund_from_faucet(
    *dst_addrs: Union[clusterlib.AddressRecord, clusterlib.PoolUser],
    cluster_obj: clusterlib.ClusterLib,
    faucet_data: dict,
    amount: int = 3_000_000,
    tx_name: Optional[str] = None,
    destination_dir: FileType = ".",
    force: bool = False,
) -> None:
    """Send `amount` from faucet addr to all `dst_addrs`."""
    # get payment AddressRecord out of PoolUser
    dst_addr_records: List[clusterlib.AddressRecord] = [
        (r.payment if hasattr(r, "payment") else r) for r in dst_addrs  # type: ignore
    ]

    fund_dst = [
        clusterlib.TxOut(address=d.address, amount=amount)
        for d in dst_addr_records
        if force or cluster_obj.get_address_balance(d.address) < amount
    ]
    if not fund_dst:
        return

    src_address = faucet_data["payment"].address
    with helpers.FileLockIfXdist(f"{helpers.get_basetemp()}/{src_address}.lock"):
        tx_name = tx_name or helpers.get_timestamped_rand_str()
        tx_name = f"{tx_name}_funding"
        fund_tx_files = clusterlib.TxFiles(signing_key_files=[faucet_data["payment"].skey_file])

        cluster_obj.send_funds(
            src_address=src_address,
            destinations=fund_dst,
            tx_name=tx_name,
            tx_files=fund_tx_files,
            destination_dir=destination_dir,
        )
        cluster_obj.wait_for_new_block(new_blocks=2)


def create_payment_addr_records(
    *names: str,
    cluster_obj: clusterlib.ClusterLib,
    stake_vkey_file: Optional[FileType] = None,
    destination_dir: FileType = ".",
) -> List[clusterlib.AddressRecord]:
    """Create new payment address(es)."""
    addrs = [
        cluster_obj.gen_payment_addr_and_keys(
            name=name,
            stake_vkey_file=stake_vkey_file,
            destination_dir=destination_dir,
        )
        for name in names
    ]

    LOGGER.debug(f"Created {len(addrs)} payment address(es)")
    return addrs


def create_stake_addr_records(
    *names: str,
    cluster_obj: clusterlib.ClusterLib,
    destination_dir: FileType = ".",
) -> List[clusterlib.AddressRecord]:
    """Create new stake address(es)."""
    addrs = [
        cluster_obj.gen_stake_addr_and_keys(name=name, destination_dir=destination_dir)
        for name in names
    ]

    LOGGER.debug(f"Created {len(addrs)} stake address(es)")
    return addrs


def create_pool_users(
    cluster_obj: clusterlib.ClusterLib,
    name_template: str,
    no_of_addr: int = 1,
) -> List[clusterlib.PoolUser]:
    """Create PoolUsers."""
    pool_users = []
    payment_addrs = []
    for i in range(no_of_addr):
        # create key pairs and addresses
        stake_addr_rec = create_stake_addr_records(
            f"{name_template}_addr{i}", cluster_obj=cluster_obj
        )[0]
        payment_addr_rec = create_payment_addr_records(
            f"{name_template}_addr{i}",
            cluster_obj=cluster_obj,
            stake_vkey_file=stake_addr_rec.vkey_file,
        )[0]
        # create pool user struct
        pool_user = clusterlib.PoolUser(payment=payment_addr_rec, stake=stake_addr_rec)
        payment_addrs.append(payment_addr_rec)
        pool_users.append(pool_user)

    return pool_users


def wait_for_stake_distribution(cluster_obj: clusterlib.ClusterLib) -> dict:
    """Wait to 3rd epoch (if necessary) and return stake distribution info."""
    epoch = cluster_obj.get_epoch()
    if epoch < 3:
        new_epochs = 3 - epoch
        LOGGER.info(f"Waiting {new_epochs} epoch(s) to get stake distribution.")
        cluster_obj.wait_for_new_epoch(new_epochs)
    return cluster_obj.get_stake_distribution()


def load_registered_pool_data(
    cluster_obj: clusterlib.ClusterLib, pool_name: str, pool_id: str
) -> clusterlib.PoolData:
    """Load data of existing registered pool."""
    if pool_id.startswith("pool"):
        pool_id = helpers.decode_bech32(pool_id)

    pool_state: dict = cluster_obj.get_registered_stake_pools_ledger_state().get(pool_id) or {}
    metadata = pool_state.get("metadata") or {}

    # TODO: extend to handle more relays records
    relays_list = pool_state.get("relays") or []
    relay = relays_list[0] if relays_list else {}
    relay = relay.get("single host address") or {}

    pool_data = clusterlib.PoolData(
        pool_name=pool_name,
        pool_pledge=pool_state["pledge"],
        pool_cost=pool_state["cost"],
        pool_margin=pool_state["margin"],
        pool_metadata_url=metadata.get("url") or "",
        pool_metadata_hash=metadata.get("hash") or "",
        pool_relay_ipv4=relay.get("IPv4") or "",
        pool_relay_port=relay.get("port") or 0,
    )

    return pool_data


def check_pool_data(  # noqa: C901
    pool_ledger_state: dict, pool_creation_data: clusterlib.PoolData
) -> str:
    """Check that actual pool state corresponds with pool creation data."""
    errors_list = []

    if pool_ledger_state["cost"] != pool_creation_data.pool_cost:
        errors_list.append(
            "'cost' value is different than expected; "
            f"Expected: {pool_creation_data.pool_cost} vs Returned: {pool_ledger_state['cost']}"
        )

    if pool_ledger_state["margin"] != pool_creation_data.pool_margin:
        errors_list.append(
            "'margin' value is different than expected; "
            f"Expected: {pool_creation_data.pool_margin} vs Returned: {pool_ledger_state['margin']}"
        )

    if pool_ledger_state["pledge"] != pool_creation_data.pool_pledge:
        errors_list.append(
            "'pledge' value is different than expected; "
            f"Expected: {pool_creation_data.pool_pledge} vs Returned: {pool_ledger_state['pledge']}"
        )

    if pool_ledger_state["relays"] != (pool_creation_data.pool_relay_dns or []):
        errors_list.append(
            "'relays' value is different than expected; "
            f"Expected: {pool_creation_data.pool_relay_dns} vs "
            f"Returned: {pool_ledger_state['relays']}"
        )

    if pool_creation_data.pool_metadata_url and pool_creation_data.pool_metadata_hash:
        metadata = pool_ledger_state.get("metadata") or {}

        metadata_hash = metadata.get("hash")
        if metadata_hash != pool_creation_data.pool_metadata_hash:
            errors_list.append(
                "'metadata hash' value is different than expected; "
                f"Expected: {pool_creation_data.pool_metadata_hash} vs "
                f"Returned: {metadata_hash}"
            )

        metadata_url = metadata.get("url")
        if metadata_url != pool_creation_data.pool_metadata_url:
            errors_list.append(
                "'metadata url' value is different than expected; "
                f"Expected: {pool_creation_data.pool_metadata_url} vs "
                f"Returned: {metadata_url}"
            )
    elif pool_ledger_state["metadata"] is not None:
        errors_list.append(
            "'metadata' value is different than expected; "
            f"Expected: None vs Returned: {pool_ledger_state['metadata']}"
        )

    if errors_list:
        for err in errors_list:
            LOGGER.error(err)
        LOGGER.error(f"Stake Pool Details: \n{pool_ledger_state}")

    return "\n\n".join(errors_list)


def update_params(
    cluster_obj: clusterlib.ClusterLib,
    src_addr_record: clusterlib.AddressRecord,
    update_proposals: List[UpdateProposal],
) -> None:
    """Update params using update proposal."""
    _cli_args = [(u.arg, str(u.value)) for u in update_proposals]
    cli_args = list(itertools.chain.from_iterable(_cli_args))

    with helpers.FileLockIfXdist(f"{helpers.get_basetemp()}/update_params.lock"):
        LOGGER.info("Waiting for new epoch to submit proposal.")
        cluster_obj.wait_for_new_epoch()

        cluster_obj.submit_update_proposal(
            cli_args=cli_args,
            src_address=src_addr_record.address,
            src_skey_file=src_addr_record.skey_file,
            tx_name=helpers.get_timestamped_rand_str(),
        )

        LOGGER.info(f"Update Proposal submitted ({cli_args})")
        cluster_obj.wait_for_new_epoch()

        protocol_params = cluster_obj.get_protocol_params()
        for u in update_proposals:
            # TODO: handle nested dictionaries
            if not u.name:
                continue
            updated_value = protocol_params[u.name]
            if str(updated_value) != str(u.value):
                raise AssertionError(
                    f"Cluster update proposal failed! Param value for {u.name}: {updated_value}.\n"
                    f"Expected: {u.value}\n"
                    f"Tip: {cluster_obj.get_tip()}"
                )


def mint_or_burn_sign(
    cluster_obj: clusterlib.ClusterLib,
    new_tokens: List[TokenRecord],
    temp_template: str,
) -> None:
    """Mint or burn tokens, depending on the `amount` value. Sign using skeys.

    Positive `amount` value means minting, negative means burning.
    """
    _issuers_addrs = [n.issuers_addrs for n in new_tokens]
    issuers_addrs = list(itertools.chain.from_iterable(_issuers_addrs))
    issuers_skey_files = [p.skey_file for p in issuers_addrs]
    token_mint_addr_skey_files = [t.token_mint_addr.skey_file for t in new_tokens]
    src_address = new_tokens[0].token_mint_addr.address

    tx_files = clusterlib.TxFiles(
        signing_key_files=[*issuers_skey_files, *token_mint_addr_skey_files]
    )

    # build and sign a transaction
    ttl = cluster_obj.calculate_tx_ttl()
    fee = cluster_obj.calculate_tx_fee(
        src_address=src_address,
        tx_name=temp_template,
        tx_files=tx_files,
        ttl=ttl,
        # TODO: workaround for https://github.com/input-output-hk/cardano-node/issues/1892
        witness_count_add=len(issuers_skey_files) * 2,
    )
    tx_raw_output = cluster_obj.build_raw_tx(
        src_address=src_address,
        tx_name=temp_template,
        tx_files=tx_files,
        fee=fee,
        ttl=ttl,
        mint=[
            clusterlib.TxOut(address=n.token_mint_addr.address, amount=n.amount, coin=n.token)
            for n in new_tokens
        ],
    )
    out_file_signed = cluster_obj.sign_tx(
        tx_body_file=tx_raw_output.out_file,
        signing_key_files=tx_files.signing_key_files,
        tx_name=temp_template,
        script_files=[n.script for n in new_tokens],
    )

    # submit signed transaction
    cluster_obj.submit_tx(out_file_signed)
    cluster_obj.wait_for_new_block(new_blocks=2)


def new_tokens(
    *asset_names: str,
    cluster_obj: clusterlib.ClusterLib,
    temp_template: str,
    token_mint_addr: clusterlib.AddressRecord,
    issuer_addr: clusterlib.AddressRecord,
    amount: int,
) -> List[TokenRecord]:
    """Mint new token, sign using skeys."""
    # create simple script
    keyhash = cluster_obj.get_payment_vkey_hash(issuer_addr.vkey_file)
    script_content = {"keyHash": keyhash, "type": "sig"}
    script = Path(f"{temp_template}.script")
    with open(f"{temp_template}.script", "w") as out_json:
        json.dump(script_content, out_json)

    policyid = cluster_obj.get_policyid(script)

    tokens_to_mint = []
    for asset_name in asset_names:
        token = f"{policyid}.{asset_name}"

        if cluster_obj.get_utxo(token_mint_addr.address, coins=[token]):
            raise AssertionError("The token already exists")

        tokens_to_mint.append(
            TokenRecord(
                token=token,
                asset_name=asset_name,
                amount=amount,
                issuers_addrs=[issuer_addr],
                token_mint_addr=token_mint_addr,
                script=script,
            )
        )

    # token minting
    mint_or_burn_sign(
        cluster_obj=cluster_obj,
        new_tokens=tokens_to_mint,
        temp_template=f"{temp_template}_mint",
    )

    for token_rec in tokens_to_mint:
        token_utxo = cluster_obj.get_utxo(token_mint_addr.address, coins=[token_rec.token])
        if not (token_utxo and token_utxo[0].amount == amount):
            raise AssertionError("The token was not minted")

    return tokens_to_mint


def filtered_ledger_state(
    cluster_obj: clusterlib.ClusterLib,
) -> str:
    """Get filtered output of `query ledger-state`."""
    cardano_cmd = " ".join(
        [
            "cardano-cli",
            "query",
            "ledger-state",
            *cluster_obj.magic_args,
            *cluster_obj.era_arg,
            f"--{cluster_obj.protocol}-mode",
        ]
    )
    # get rid of a huge amount of data we don't have any use for
    cmd = (
        f"{cardano_cmd} | jq -n --stream -c "
        "'fromstream(inputs|select((length == 2 and .[0][1] == \"esLState\")|not))'"
    )

    return helpers.run_command(cmd, shell=True).decode("utf-8").strip()


def get_ledger_state(
    cluster_obj: clusterlib.ClusterLib,
) -> dict:
    """Return the current ledger state info."""
    f_ledger_state = filtered_ledger_state(cluster_obj)
    if not f_ledger_state:
        return {}
    ledger_state: dict = json.loads(f_ledger_state)
    return ledger_state


def save_ledger_state(
    cluster_obj: clusterlib.ClusterLib,
    state_name: str,
    ledger_state: Optional[dict] = None,
    destination_dir: FileType = ".",
) -> Path:
    """Save ledger state to file.

    Args:
        cluster_obj: An instance of `clusterlib.ClusterLib`.
        state_name: A name of the ledger state (can be epoch number, etc.).
        ledger_state: A dict with ledger state to save (optional).
        destination_dir: A path to directory for storing the state JSON file (optional).

    Returns:
        Path: A path to the generated state JSON file.
    """
    json_file = Path(destination_dir) / f"{state_name}_ledger_state.json"
    ledger_state = ledger_state or get_ledger_state(cluster_obj)
    with open(json_file, "w") as fp_out:
        json.dump(ledger_state, fp_out, indent=4)
    return json_file
