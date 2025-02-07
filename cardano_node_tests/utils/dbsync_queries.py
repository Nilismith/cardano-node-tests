"""SQL queries to db-sync database."""

import contextlib
import dataclasses
import decimal
import typing as tp

import psycopg2

from cardano_node_tests.utils import dbsync_conn


@dataclasses.dataclass(frozen=True)
class PoolDataDBRow:
    # pylint: disable-next=invalid-name
    id: int
    hash: memoryview
    view: str
    cert_index: int
    vrf_key_hash: memoryview
    pledge: int
    reward_addr: memoryview
    reward_addr_view: str
    active_epoch_no: int
    meta_id: int
    margin: decimal.Decimal
    fixed_cost: int
    registered_tx_id: int
    metadata_url: str
    metadata_hash: memoryview
    owner_stake_address_id: int
    owner: memoryview
    ipv4: str
    ipv6: str
    dns_name: str
    port: int
    retire_cert_index: int
    retire_announced_tx_id: int
    retiring_epoch: int


@dataclasses.dataclass(frozen=True)
class PoolOffChainDataDBRow:
    # pylint: disable-next=invalid-name
    id: int
    ticker_name: str
    hash: memoryview
    json: dict
    bytes: memoryview
    pmr_id: int


@dataclasses.dataclass(frozen=True)
class PoolOffChainFetchErrorDBRow:
    # pylint: disable-next=invalid-name
    id: int
    pmr_id: int
    fetch_error: str
    retry_count: int


@dataclasses.dataclass(frozen=True)
class EpochStakeDBRow:
    # pylint: disable-next=invalid-name
    id: int
    hash: memoryview
    view: str
    amount: int
    epoch_number: int


@dataclasses.dataclass(frozen=True)
class TxDBRow:
    # pylint: disable=too-many-instance-attributes
    tx_id: int
    tx_hash: memoryview
    block_id: int
    block_index: int
    out_sum: decimal.Decimal
    fee: decimal.Decimal
    deposit: int
    size: int
    invalid_before: tp.Optional[decimal.Decimal]
    invalid_hereafter: tp.Optional[decimal.Decimal]
    tx_out_id: int
    tx_out_tx_id: int
    utxo_ix: int
    tx_out_addr: str
    tx_out_addr_has_script: bool
    tx_out_value: decimal.Decimal
    tx_out_data_hash: tp.Optional[memoryview]
    tx_out_inline_datum_hash: tp.Optional[memoryview]
    tx_out_reference_script_hash: tp.Optional[memoryview]
    metadata_count: int
    reserve_count: int
    treasury_count: int
    pot_transfer_count: int
    stake_reg_count: int
    stake_dereg_count: int
    stake_deleg_count: int
    withdrawal_count: int
    collateral_count: int
    reference_input_count: int
    collateral_out_count: int
    script_count: int
    redeemer_count: int
    extra_key_witness_count: int
    ma_tx_out_id: tp.Optional[int]
    ma_tx_out_policy: tp.Optional[memoryview]
    ma_tx_out_name: tp.Optional[memoryview]
    ma_tx_out_quantity: tp.Optional[decimal.Decimal]
    ma_tx_mint_id: tp.Optional[int]
    ma_tx_mint_policy: tp.Optional[memoryview]
    ma_tx_mint_name: tp.Optional[memoryview]
    ma_tx_mint_quantity: tp.Optional[decimal.Decimal]


@dataclasses.dataclass(frozen=True)
class MetadataDBRow:
    # pylint: disable-next=invalid-name
    id: int
    key: decimal.Decimal
    json: tp.Any
    bytes: memoryview
    tx_id: int


@dataclasses.dataclass(frozen=True)
class ADAStashDBRow:
    # pylint: disable-next=invalid-name
    id: int
    addr_view: str
    cert_index: int
    amount: decimal.Decimal
    tx_id: int


@dataclasses.dataclass(frozen=True)
class PotTransferDBRow:
    # pylint: disable-next=invalid-name
    id: int
    cert_index: int
    treasury: decimal.Decimal
    reserves: decimal.Decimal
    tx_id: int


@dataclasses.dataclass(frozen=True)
class StakeAddrDBRow:
    # pylint: disable-next=invalid-name
    id: int
    view: str
    tx_id: int


@dataclasses.dataclass(frozen=True)
class StakeDelegDBRow:
    tx_id: int
    active_epoch_no: tp.Optional[int]
    pool_id: tp.Optional[str]
    address: tp.Optional[str]


@dataclasses.dataclass(frozen=True)
class WithdrawalDBRow:
    tx_id: int
    address: str
    amount: int


@dataclasses.dataclass(frozen=True)
class TxInDBRow:
    tx_out_id: int
    utxo_ix: int
    address: str
    value: decimal.Decimal
    tx_hash: memoryview
    reference_script_hash: tp.Optional[memoryview]
    reference_script_json: tp.Optional[dict]
    reference_script_bytes: tp.Optional[memoryview]
    reference_script_type: tp.Optional[str]
    ma_tx_out_id: tp.Optional[int]
    ma_tx_out_policy: tp.Optional[memoryview]
    ma_tx_out_name: tp.Optional[memoryview]
    ma_tx_out_quantity: tp.Optional[decimal.Decimal]


@dataclasses.dataclass(frozen=True)
class TxInNoMADBRow:
    tx_out_id: int
    utxo_ix: int
    address: str
    value: decimal.Decimal
    tx_hash: memoryview
    reference_script_hash: tp.Optional[memoryview]
    reference_script_json: tp.Optional[dict]
    reference_script_bytes: tp.Optional[memoryview]
    reference_script_type: tp.Optional[str]


@dataclasses.dataclass(frozen=True)
class CollateralTxOutDBRow:
    tx_out_id: int
    utxo_ix: int
    address: str
    value: decimal.Decimal
    tx_hash: memoryview


@dataclasses.dataclass(frozen=True)
class ScriptDBRow:
    # pylint: disable-next=invalid-name
    id: int
    tx_id: int
    hash: memoryview
    type: str
    serialised_size: tp.Optional[int]


@dataclasses.dataclass(frozen=True)
class RedeemerDBRow:
    # pylint: disable-next=invalid-name
    id: int
    tx_id: int
    unit_mem: int
    unit_steps: int
    fee: int
    purpose: str
    script_hash: memoryview
    value: dict


@dataclasses.dataclass(frozen=True)
class ADAPotsDBRow:
    # pylint: disable-next=invalid-name
    id: int
    slot_no: int
    epoch_no: int
    treasury: decimal.Decimal
    reserves: decimal.Decimal
    rewards: decimal.Decimal
    utxo: decimal.Decimal
    deposits: decimal.Decimal
    fees: decimal.Decimal
    block_id: int


@dataclasses.dataclass(frozen=True)
class RewardDBRow:
    address: str
    type: str
    amount: decimal.Decimal
    earned_epoch: int
    spendable_epoch: int
    pool_id: tp.Optional[str] = ""


@dataclasses.dataclass(frozen=True)
class UTxODBRow:
    tx_hash: memoryview
    utxo_ix: int
    payment_address: str
    stake_address: str
    has_script: bool
    value: int
    data_hash: tp.Optional[memoryview]


@dataclasses.dataclass(frozen=True)
class BlockDBRow:
    # pylint: disable-next=invalid-name
    id: int
    epoch_no: tp.Optional[int]
    slot_no: tp.Optional[int]
    epoch_slot_no: tp.Optional[int]
    block_no: tp.Optional[int]
    previous_id: tp.Optional[int]
    tx_count: tp.Optional[int]
    proto_major: tp.Optional[int]
    proto_minor: tp.Optional[int]
    pool_id: tp.Optional[str]


@dataclasses.dataclass(frozen=True)
class DatumDBRow:
    # pylint: disable-next=invalid-name
    id: int
    datum_hash: memoryview
    tx_id: int
    value: dict
    bytes: memoryview


@dataclasses.dataclass(frozen=True)
class SchemaVersionStages:
    one: int
    two: int
    three: int


@dataclasses.dataclass(frozen=True)
class ParamProposalDBRow:
    # pylint: disable=too-many-instance-attributes disable-next=invalid-name
    id: int
    epoch_no: int
    key: memoryview
    min_fee_a: int
    min_fee_b: int
    max_block_size: int
    max_tx_size: int
    max_bh_size: int
    key_deposit: int
    pool_deposit: int
    max_epoch: int
    optimal_pool_count: int
    influence: float
    monetary_expand_rate: float
    treasury_growth_rate: float
    decentralisation: float
    entropy: memoryview
    protocol_major: int
    protocol_minor: int
    min_utxo_value: int
    min_pool_cost: int
    coins_per_utxo_word: int
    cost_model_id: int
    price_mem: float
    price_step: float
    max_tx_ex_mem: int
    max_tx_ex_steps: int
    max_block_ex_mem: int
    max_block_ex_steps: int
    max_val_size: int
    collateral_percent: int
    max_collateral_inputs: int
    registered_tx_id: int
    pvt_motion_no_confidence: int
    pvt_committee_normal: int
    pvt_committee_no_confidence: int
    pvt_hard_fork_initiation: int
    dvt_motion_no_confidence: int
    dvt_committee_normal: int
    dvt_committee_no_confidence: int
    dvt_update_to_constitution: int
    dvt_hard_fork_initiation: int
    dvt_p_p_network_group: int
    dvt_p_p_economic_group: int
    dvt_p_p_technical_group: int
    dvt_p_p_gov_group: int
    dvt_treasury_withdrawal: int
    committee_min_size: int
    committee_max_term_length: int
    gov_action_lifetime: int
    gov_action_deposit: int
    drep_deposit: int
    drep_activity: str


@dataclasses.dataclass(frozen=True)
class EpochDBRow:
    # pylint: disable-next=invalid-name
    id: int
    out_sum: int
    fees: int
    tx_count: int
    blk_count: int
    epoch_number: int


@dataclasses.dataclass(frozen=True)
class CommitteeRegistrationDBRow:
    # pylint: disable-next=invalid-name
    id: int
    tx_id: int
    cert_index: int
    cold_key: memoryview
    hot_key: memoryview


@dataclasses.dataclass(frozen=True)
class CommitteeDeregistrationDBRow:
    # pylint: disable-next=invalid-name
    id: int
    tx_id: int
    cert_index: int
    voting_anchor_id: int
    cold_key: memoryview


@dataclasses.dataclass(frozen=True)
class DrepRegistrationDBRow:
    # pylint: disable-next=invalid-name
    id: int
    tx_id: int
    cert_index: int
    deposit: int
    drep_hash_id: int
    voting_anchor_id: int
    hash_raw: memoryview
    hash_view: str
    has_script: bool


@dataclasses.dataclass(frozen=True)
class GovActionProposalDBRow:
    # pylint: disable-next=invalid-name
    id: int
    tx_id: int
    prev_gov_action_proposal: int
    deposit: int
    return_address: int
    expiration: int
    voting_anchor_id: int
    type: str
    description: str
    param_proposal: int
    ratified_epoch: int
    enacted_epoch: int
    dropped_epoch: int
    expired_epoch: int


@contextlib.contextmanager
def execute(query: str, vars: tp.Sequence = ()) -> tp.Iterator[psycopg2.extensions.cursor]:
    # pylint: disable=redefined-builtin
    cur = None
    try:
        cur = dbsync_conn.conn().cursor()

        try:
            cur.execute(query, vars)
            conn_alive = True
        except psycopg2.Error:
            conn_alive = False

        if not conn_alive:
            cur = dbsync_conn.reconn().cursor()
            cur.execute(query, vars)

        yield cur
    finally:
        if cur is not None:
            cur.close()


class SchemaVersion:
    """Query and cache db-sync schema version."""

    _stages: tp.ClassVar[tp.Optional[SchemaVersionStages]] = None

    @classmethod
    def stages(cls) -> SchemaVersionStages:
        if cls._stages is not None:
            return cls._stages

        query = (
            "SELECT stage_one, stage_two, stage_three "
            "FROM schema_version ORDER BY id DESC LIMIT 1;"
        )

        with execute(query=query) as cur:
            cls._stages = SchemaVersionStages(*cur.fetchone())

        return cls._stages


def query_tx(txhash: str) -> tp.Generator[TxDBRow, None, None]:
    """Query a transaction in db-sync."""
    query = (
        "SELECT"
        " tx.id, tx.hash, tx.block_id, tx.block_index, tx.out_sum, tx.fee, tx.deposit, tx.size,"
        " tx.invalid_before, tx.invalid_hereafter,"
        " tx_out.id, tx_out.tx_id, tx_out.index, tx_out.address, tx_out.address_has_script,"
        " tx_out.value, tx_out.data_hash, datum.hash, script.hash,"
        " (SELECT COUNT(id) FROM tx_metadata WHERE tx_id=tx.id) AS metadata_count,"
        " (SELECT COUNT(id) FROM reserve WHERE tx_id=tx.id) AS reserve_count,"
        " (SELECT COUNT(id) FROM treasury WHERE tx_id=tx.id) AS treasury_count,"
        " (SELECT COUNT(id) FROM pot_transfer WHERE tx_id=tx.id) AS pot_transfer_count,"
        " (SELECT COUNT(id) FROM stake_registration WHERE tx_id=tx.id) AS reg_count,"
        " (SELECT COUNT(id) FROM stake_deregistration WHERE tx_id=tx.id) AS dereg_count,"
        " (SELECT COUNT(id) FROM delegation WHERE tx_id=tx.id) AS deleg_count,"
        " (SELECT COUNT(id) FROM withdrawal WHERE tx_id=tx.id) AS withdrawal_count,"
        " (SELECT COUNT(id) FROM collateral_tx_in WHERE tx_in_id=tx.id) AS collateral_count,"
        " (SELECT COUNT(id) FROM reference_tx_in WHERE tx_in_id=tx.id) AS reference_input_count,"
        " (SELECT COUNT(id) FROM collateral_tx_out WHERE tx_id=tx.id) AS collateral_out_count,"
        " (SELECT COUNT(id) FROM script WHERE tx_id=tx.id) AS script_count,"
        " (SELECT COUNT(id) FROM redeemer WHERE tx_id=tx.id) AS redeemer_count,"
        " (SELECT COUNT(id) FROM extra_key_witness WHERE tx_id=tx.id) AS extra_key_witness_count,"
        " ma_tx_out.id, join_ma_out.policy, join_ma_out.name, ma_tx_out.quantity,"
        " ma_tx_mint.id, join_ma_mint.policy, join_ma_mint.name, ma_tx_mint.quantity "
        "FROM tx "
        "LEFT JOIN tx_out ON tx.id = tx_out.tx_id "
        "LEFT JOIN ma_tx_out ON tx_out.id = ma_tx_out.tx_out_id "
        "LEFT JOIN ma_tx_mint ON tx.id = ma_tx_mint.tx_id "
        "LEFT JOIN multi_asset join_ma_out ON ma_tx_out.ident = join_ma_out.id "
        "LEFT JOIN multi_asset join_ma_mint ON ma_tx_mint.ident = join_ma_mint.id "
        "LEFT JOIN datum ON tx_out.inline_datum_id = datum.id "
        "LEFT JOIN script ON tx_out.reference_script_id = script.id "
        "WHERE tx.hash = %s;"
    )

    with execute(query=query, vars=(rf"\x{txhash}",)) as cur:
        while (result := cur.fetchone()) is not None:
            yield TxDBRow(*result)


def query_tx_ins(txhash: str) -> tp.Generator[TxInDBRow, None, None]:
    """Query transaction txins in db-sync."""
    query = (
        "SELECT"
        " tx_out.id, tx_out.index, tx_out.address, tx_out.value, jtx_out_id.hash,"
        " script.hash, script.json, script.bytes, script.type,"
        " ma_tx_out.id, join_ma_out.policy, join_ma_out.name, ma_tx_out.quantity "
        "FROM tx_in "
        "LEFT JOIN tx_out"
        " ON (tx_out.tx_id = tx_in.tx_out_id AND tx_out.index = tx_in.tx_out_index) "
        "LEFT JOIN tx jtx_in ON jtx_in.id = tx_in.tx_in_id "
        "LEFT JOIN tx jtx_out_id ON jtx_out_id.id = tx_out.tx_id "
        "LEFT JOIN ma_tx_out ON tx_out.id = ma_tx_out.tx_out_id "
        "LEFT JOIN multi_asset join_ma_out ON ma_tx_out.ident = join_ma_out.id "
        "LEFT JOIN script ON script.id = tx_out.reference_script_id "
        "WHERE jtx_in.hash = %s;"
    )

    with execute(query=query, vars=(rf"\x{txhash}",)) as cur:
        while (result := cur.fetchone()) is not None:
            yield TxInDBRow(*result)


def query_collateral_tx_ins(txhash: str) -> tp.Generator[TxInNoMADBRow, None, None]:
    """Query transaction collateral txins in db-sync."""
    query = (
        "SELECT"
        " tx_out.id, tx_out.index, tx_out.address, tx_out.value, jtx_out_id.hash,"
        " script.hash, script.json, script.bytes, script.type "
        "FROM collateral_tx_in "
        "LEFT JOIN tx_out"
        " ON (tx_out.tx_id = collateral_tx_in.tx_out_id AND"
        "     tx_out.index = collateral_tx_in.tx_out_index) "
        "LEFT JOIN tx jtx_col ON jtx_col.id = collateral_tx_in.tx_in_id "
        "LEFT JOIN tx jtx_out_id ON jtx_out_id.id = tx_out.tx_id "
        "LEFT JOIN script ON script.id = tx_out.reference_script_id "
        "WHERE jtx_col.hash = %s;"
    )

    with execute(query=query, vars=(rf"\x{txhash}",)) as cur:
        while (result := cur.fetchone()) is not None:
            yield TxInNoMADBRow(*result)


def query_reference_tx_ins(txhash: str) -> tp.Generator[TxInNoMADBRow, None, None]:
    """Query transaction reference txins in db-sync."""
    query = (
        "SELECT "
        " tx_out.id, tx_out.index, tx_out.address, tx_out.value, jtx_out_id.hash,"
        " script.hash, script.json, script.bytes, script.type "
        "FROM reference_tx_in "
        "LEFT JOIN tx_out"
        " ON (tx_out.tx_id = reference_tx_in.tx_out_id AND"
        "     tx_out.index = reference_tx_in.tx_out_index) "
        "LEFT JOIN tx jtx_ref ON jtx_ref.id = reference_tx_in.tx_in_id "
        "LEFT JOIN tx jtx_out_id ON jtx_out_id.id = tx_out.tx_id "
        "LEFT JOIN script ON script.id = tx_out.reference_script_id "
        "WHERE jtx_ref.hash = %s;"
    )

    with execute(query=query, vars=(rf"\x{txhash}",)) as cur:
        while (result := cur.fetchone()) is not None:
            yield TxInNoMADBRow(*result)


def query_collateral_tx_outs(txhash: str) -> tp.Generator[CollateralTxOutDBRow, None, None]:
    """Query transaction collateral txouts in db-sync."""
    query = (
        "SELECT "
        " collateral_tx_out.id, collateral_tx_out.index, collateral_tx_out.address,"
        " collateral_tx_out.value, jtx_out_id.hash "
        "FROM collateral_tx_out "
        "LEFT JOIN tx jtx_col ON jtx_col.id = collateral_tx_out.tx_id "
        "LEFT JOIN tx jtx_out_id ON jtx_out_id.id = collateral_tx_out.tx_id "
        "WHERE jtx_col.hash = %s;"
    )

    with execute(query=query, vars=(rf"\x{txhash}",)) as cur:
        while (result := cur.fetchone()) is not None:
            yield CollateralTxOutDBRow(*result)


def query_scripts(txhash: str) -> tp.Generator[ScriptDBRow, None, None]:
    """Query transaction scripts in db-sync."""
    query = (
        "SELECT"
        " script.id, script.tx_id, script.hash, script.type, script.serialised_size "
        "FROM script "
        "LEFT JOIN tx ON tx.id = script.tx_id "
        "WHERE tx.hash = %s;"
    )

    with execute(query=query, vars=(rf"\x{txhash}",)) as cur:
        while (result := cur.fetchone()) is not None:
            yield ScriptDBRow(*result)


def query_redeemers(txhash: str) -> tp.Generator[RedeemerDBRow, None, None]:
    """Query transaction redeemers in db-sync."""
    query = (
        "SELECT"
        " redeemer.id, redeemer.tx_id, redeemer.unit_mem, redeemer.unit_steps, redeemer.fee,"
        " redeemer.purpose, redeemer.script_hash, redeemer_data.value "
        "FROM redeemer "
        "LEFT JOIN tx ON tx.id = redeemer.tx_id "
        "LEFT JOIN redeemer_data ON redeemer_data.id = redeemer.redeemer_data_id "
        "WHERE tx.hash = %s;"
    )

    with execute(query=query, vars=(rf"\x{txhash}",)) as cur:
        while (result := cur.fetchone()) is not None:
            yield RedeemerDBRow(*result)


def query_tx_metadata(txhash: str) -> tp.Generator[MetadataDBRow, None, None]:
    """Query transaction metadata in db-sync."""
    query = (
        "SELECT"
        " tx_metadata.id, tx_metadata.key, tx_metadata.json, tx_metadata.bytes,"
        " tx_metadata.tx_id "
        "FROM tx_metadata "
        "INNER JOIN tx ON tx.id = tx_metadata.tx_id "
        "WHERE tx.hash = %s;"
    )

    with execute(query=query, vars=(rf"\x{txhash}",)) as cur:
        while (result := cur.fetchone()) is not None:
            yield MetadataDBRow(*result)


def query_tx_reserve(txhash: str) -> tp.Generator[ADAStashDBRow, None, None]:
    """Query transaction reserve record in db-sync."""
    query = (
        "SELECT"
        " reserve.id, stake_address.view, reserve.cert_index, reserve.amount, reserve.tx_id "
        "FROM reserve "
        "INNER JOIN stake_address ON reserve.addr_id = stake_address.id "
        "INNER JOIN tx ON tx.id = reserve.tx_id "
        "WHERE tx.hash = %s;"
    )

    with execute(query=query, vars=(rf"\x{txhash}",)) as cur:
        while (result := cur.fetchone()) is not None:
            yield ADAStashDBRow(*result)


def query_tx_treasury(txhash: str) -> tp.Generator[ADAStashDBRow, None, None]:
    """Query transaction treasury record in db-sync."""
    query = (
        "SELECT"
        " treasury.id, stake_address.view, treasury.cert_index,"
        " treasury.amount, treasury.tx_id "
        "FROM treasury "
        "INNER JOIN stake_address ON treasury.addr_id = stake_address.id "
        "INNER JOIN tx ON tx.id = treasury.tx_id "
        "WHERE tx.hash = %s;"
    )

    with execute(query=query, vars=(rf"\x{txhash}",)) as cur:
        while (result := cur.fetchone()) is not None:
            yield ADAStashDBRow(*result)


def query_tx_pot_transfers(txhash: str) -> tp.Generator[PotTransferDBRow, None, None]:
    """Query transaction MIR certificate records in db-sync."""
    query = (
        "SELECT"
        " pot_transfer.id, pot_transfer.cert_index, pot_transfer.treasury,"
        " pot_transfer.reserves, pot_transfer.tx_id "
        "FROM pot_transfer "
        "INNER JOIN tx ON tx.id = pot_transfer.tx_id "
        "WHERE tx.hash = %s;"
    )

    with execute(query=query, vars=(rf"\x{txhash}",)) as cur:
        while (result := cur.fetchone()) is not None:
            yield PotTransferDBRow(*result)


def query_tx_stake_reg(txhash: str) -> tp.Generator[StakeAddrDBRow, None, None]:
    """Query stake registration record in db-sync."""
    query = (
        "SELECT"
        " stake_registration.addr_id, stake_address.view, stake_registration.tx_id "
        "FROM stake_registration "
        "INNER JOIN stake_address ON stake_registration.addr_id = stake_address.id "
        "INNER JOIN tx ON tx.id = stake_registration.tx_id "
        "WHERE tx.hash = %s;"
    )

    with execute(query=query, vars=(rf"\x{txhash}",)) as cur:
        while (result := cur.fetchone()) is not None:
            yield StakeAddrDBRow(*result)


def query_tx_stake_dereg(txhash: str) -> tp.Generator[StakeAddrDBRow, None, None]:
    """Query stake deregistration record in db-sync."""
    query = (
        "SELECT"
        " stake_deregistration.addr_id, stake_address.view, stake_deregistration.tx_id "
        "FROM stake_deregistration "
        "INNER JOIN stake_address ON stake_deregistration.addr_id = stake_address.id "
        "INNER JOIN tx ON tx.id = stake_deregistration.tx_id "
        "WHERE tx.hash = %s;"
    )

    with execute(query=query, vars=(rf"\x{txhash}",)) as cur:
        while (result := cur.fetchone()) is not None:
            yield StakeAddrDBRow(*result)


def query_tx_stake_deleg(txhash: str) -> tp.Generator[StakeDelegDBRow, None, None]:
    """Query stake registration record in db-sync."""
    query = (
        "SELECT"
        " tx.id, delegation.active_epoch_no, pool_hash.view AS pool_view,"
        " stake_address.view AS address_view "
        "FROM delegation "
        "INNER JOIN stake_address ON delegation.addr_id = stake_address.id "
        "INNER JOIN tx ON tx.id = delegation.tx_id "
        "INNER JOIN pool_hash ON pool_hash.id = delegation.pool_hash_id "
        "WHERE tx.hash = %s;"
    )

    with execute(query=query, vars=(rf"\x{txhash}",)) as cur:
        while (result := cur.fetchone()) is not None:
            yield StakeDelegDBRow(*result)


def query_tx_withdrawal(txhash: str) -> tp.Generator[WithdrawalDBRow, None, None]:
    """Query reward withdrawal record in db-sync."""
    query = (
        "SELECT"
        " tx.id, stake_address.view, amount "
        "FROM withdrawal "
        "INNER JOIN stake_address ON withdrawal.addr_id = stake_address.id "
        "INNER JOIN tx ON tx.id = withdrawal.tx_id "
        "WHERE tx.hash = %s;"
    )

    with execute(query=query, vars=(rf"\x{txhash}",)) as cur:
        while (result := cur.fetchone()) is not None:
            yield WithdrawalDBRow(*result)


def query_ada_pots(
    epoch_from: int = 0, epoch_to: int = 99999999
) -> tp.Generator[ADAPotsDBRow, None, None]:
    """Query ADA pots record in db-sync."""
    query = (
        "SELECT"
        " id, slot_no, epoch_no, treasury, reserves, rewards, utxo, deposits, fees, block_id "
        "FROM ada_pots "
        "WHERE epoch_no BETWEEN %s AND %s "
        "ORDER BY id;"
    )

    with execute(query=query, vars=(epoch_from, epoch_to)) as cur:
        while (result := cur.fetchone()) is not None:
            yield ADAPotsDBRow(*result)


def query_address_reward(
    address: str, epoch_from: int = 0, epoch_to: int = 99999999
) -> tp.Generator[RewardDBRow, None, None]:
    """Query reward records for stake address in db-sync."""
    query = (
        "SELECT"
        " stake_address.view, reward.type, reward.amount, reward.earned_epoch,"
        " reward.spendable_epoch, pool_hash.view AS pool_view "
        "FROM reward "
        "INNER JOIN stake_address ON reward.addr_id = stake_address.id "
        "LEFT JOIN pool_hash ON pool_hash.id = reward.pool_id "
        "WHERE (stake_address.view = %s) AND (reward.spendable_epoch BETWEEN %s AND %s) ;"
    )

    with execute(query=query, vars=(address, epoch_from, epoch_to)) as cur:
        while (result := cur.fetchone()) is not None:
            yield RewardDBRow(*result)


def query_address_instant_reward(
    address: str, epoch_from: int = 0, epoch_to: int = 99999999
) -> tp.Generator[RewardDBRow, None, None]:
    """Query instant reward records for stake address in db-sync."""
    query = (
        "SELECT"
        " stake_address.view, instant_reward.type, instant_reward.amount, "
        " instant_reward.earned_epoch, instant_reward.spendable_epoch "
        "FROM instant_reward "
        "INNER JOIN stake_address ON instant_reward.addr_id = stake_address.id "
        "WHERE (stake_address.view = %s) AND (instant_reward.spendable_epoch BETWEEN %s AND %s) ;"
    )

    with execute(query=query, vars=(address, epoch_from, epoch_to)) as cur:
        while (result := cur.fetchone()) is not None:
            yield RewardDBRow(*result)


def query_utxo(address: str) -> tp.Generator[UTxODBRow, None, None]:
    """Query UTxOs for payment address in db-sync."""
    query = (
        "SELECT"
        " tx.hash, utxo_view.index, utxo_view.address, stake_address.view,"
        " utxo_view.address_has_script, utxo_view.value, utxo_view.data_hash "
        "FROM utxo_view "
        "INNER JOIN tx ON utxo_view.tx_id = tx.id "
        "LEFT JOIN stake_address ON utxo_view.stake_address_id = stake_address.id "
        "WHERE utxo_view.address = %s "
        "ORDER BY utxo_view.id;"
    )

    with execute(query=query, vars=(address,)) as cur:
        while (result := cur.fetchone()) is not None:
            yield UTxODBRow(*result)


def query_pool_data(pool_id_bech32: str) -> tp.Generator[PoolDataDBRow, None, None]:
    """Query pool data record in db-sync."""
    query = (
        "SELECT DISTINCT"
        " pool_hash.id, pool_hash.hash_raw, pool_hash.view,"
        " pool_update.cert_index, pool_update.vrf_key_hash, pool_update.pledge,"
        " join_reward_address.hash_raw, join_reward_address.view,"
        " pool_update.active_epoch_no, pool_update.meta_id,"
        " pool_update.margin, pool_update.fixed_cost, pool_update.registered_tx_id,"
        " pool_metadata_ref.url AS metadata_url, pool_metadata_ref.hash AS metadata_hash,"
        " pool_owner.addr_id AS owner_stake_address_id,"
        " join_owner_address.hash_raw AS owner,"
        " pool_relay.ipv4, pool_relay.ipv6, pool_relay.dns_name, pool_relay.port,"
        " pool_retire.cert_index AS retire_cert_index,"
        " pool_retire.announced_tx_id AS retire_announced_tx_id, pool_retire.retiring_epoch "
        "FROM pool_hash "
        "INNER JOIN pool_update ON pool_hash.id = pool_update.hash_id "
        "FULL JOIN pool_metadata_ref ON pool_update.meta_id = pool_metadata_ref.id "
        "INNER JOIN pool_owner ON pool_update.id = pool_owner.pool_update_id "
        "FULL JOIN pool_relay ON pool_update.id = pool_relay.update_id "
        "FULL JOIN pool_retire ON pool_hash.id = pool_retire.hash_id "
        "INNER JOIN stake_address join_reward_address ON"
        " pool_update.reward_addr_id = join_reward_address.id "
        "INNER JOIN stake_address join_owner_address ON pool_owner.addr_id = join_owner_address.id "
        "WHERE pool_hash.view = %s ORDER BY registered_tx_id;"
    )

    with execute(query=query, vars=(pool_id_bech32,)) as cur:
        while (result := cur.fetchone()) is not None:
            yield PoolDataDBRow(*result)


def query_off_chain_pool_data(
    pool_id_bech32: str,
) -> tp.Generator[PoolOffChainDataDBRow, None, None]:
    """Query `Off_Chain_Pool_Data` record in db-sync."""
    query = (
        "SELECT"
        " off_chain_pool_data.pool_id, off_chain_pool_data.ticker_name, off_chain_pool_data.hash,"
        " off_chain_pool_data.json, off_chain_pool_data.bytes, off_chain_pool_data.pmr_id "
        "FROM off_chain_pool_data "
        "INNER JOIN pool_hash ON pool_hash.id = off_chain_pool_data.pool_id "
        "WHERE pool_hash.view = %s;"
    )

    with execute(query=query, vars=(pool_id_bech32,)) as cur:
        while (result := cur.fetchone()) is not None:
            yield PoolOffChainDataDBRow(*result)


def query_off_chain_pool_fetch_error(
    pool_id_bech32: str,
) -> tp.Generator[PoolOffChainFetchErrorDBRow, None, None]:
    """Query `Off_Chain_Pool_Fetch_Error` record in db-sync."""
    query = (
        "SELECT"
        " off_chain_pool_fetch_error.pool_id, off_chain_pool_fetch_error.pmr_id,"
        " off_chain_pool_fetch_error.fetch_error, off_chain_pool_fetch_error.retry_count "
        "FROM off_chain_pool_fetch_error "
        "INNER JOIN pool_hash ON pool_hash.id = off_chain_pool_fetch_error.pool_id "
        "WHERE pool_hash.view = %s;"
    )

    with execute(query=query, vars=(pool_id_bech32,)) as cur:
        while (result := cur.fetchone()) is not None:
            yield PoolOffChainFetchErrorDBRow(*result)


def query_epoch_stake(
    pool_id_bech32: str, epoch_number: int
) -> tp.Generator[EpochStakeDBRow, None, None]:
    """Query epoch stake record for a pool in db-sync."""
    query = (
        "SELECT "
        " epoch_stake.id, pool_hash.hash_raw, pool_hash.view, epoch_stake.amount,"
        " epoch_stake.epoch_no "
        "FROM epoch_stake "
        "INNER JOIN pool_hash ON epoch_stake.pool_id = pool_hash.id "
        "WHERE pool_hash.view = %s AND epoch_stake.epoch_no = %s "
        "ORDER BY epoch_stake.epoch_no DESC;"
    )

    with execute(query=query, vars=(pool_id_bech32, epoch_number)) as cur:
        while (result := cur.fetchone()) is not None:
            yield EpochStakeDBRow(*result)


def query_blocks(
    pool_id_bech32: str = "", epoch_from: int = 0, epoch_to: int = 99999999
) -> tp.Generator[BlockDBRow, None, None]:
    """Query block records in db-sync."""
    if pool_id_bech32:
        pool_query = "(pool_hash.view = %s) AND"
        query_vars: tuple = (pool_id_bech32, epoch_from, epoch_to)
    else:
        pool_query = ""
        query_vars = (epoch_from, epoch_to)

    query = (
        "SELECT"
        " block.id, block.epoch_no, block.slot_no, block.epoch_slot_no, block.block_no,"
        " block.previous_id, block.tx_count, block.proto_major, block.proto_minor,"
        " pool_hash.view "
        "FROM block "
        "INNER JOIN slot_leader ON slot_leader.id = block.slot_leader_id "
        "LEFT JOIN pool_hash ON pool_hash.id = slot_leader.pool_hash_id "
        f"WHERE {pool_query} (epoch_no BETWEEN %s AND %s) "
        "ORDER BY block.id;"
    )

    with execute(query=query, vars=query_vars) as cur:
        while (result := cur.fetchone()) is not None:
            yield BlockDBRow(*result)


def query_table_names() -> tp.List[str]:
    """Query table names in db-sync."""
    query = (
        "SELECT tablename "
        "FROM pg_catalog.pg_tables "
        "WHERE schemaname != 'pg_catalog' AND schemaname != 'information_schema' "
        "ORDER BY tablename ASC;"
    )

    with execute(query=query) as cur:
        results: tp.List[tp.Tuple[str]] = cur.fetchall()
        table_names = [r[0] for r in results]
        return table_names


def query_datum(datum_hash: str) -> tp.Generator[DatumDBRow, None, None]:
    """Query datum record in db-sync."""
    query = "SELECT id, hash, tx_id, value, bytes FROM datum WHERE hash = %s;"

    with execute(query=query, vars=(rf"\x{datum_hash}",)) as cur:
        while (result := cur.fetchone()) is not None:
            yield DatumDBRow(*result)


def query_cost_model() -> tp.Dict[str, tp.Dict[str, tp.Any]]:
    """Query last cost-model record in db-sync."""
    query = "SELECT * FROM cost_model ORDER BY ID DESC LIMIT 1"

    with execute(query=query) as cur:
        results = cur.fetchone()
        cost_model: tp.Dict[str, tp.Dict[str, tp.Any]] = results[1] if results else {}
        return cost_model


def query_param_proposal(txhash: str = "") -> ParamProposalDBRow:
    """Query param proposal record in db-sync.

    If txhash is not provided the query will return the last record available.
    """
    if txhash:
        hash_query = "WHERE tx.hash = %s "
        query_var: str = rf"\x{txhash}"
    else:
        hash_query = ""
        query_var = ""

    query = (
        "SELECT"
        " p.id, p.epoch_no, p.key, p.min_fee_a, p.min_fee_b, p.max_block_size,"
        " p.max_tx_size, p.max_bh_size, p.key_deposit, p.pool_deposit, p.max_epoch,"
        " p.optimal_pool_count, p.influence, p.monetary_expand_rate, p.treasury_growth_rate,"
        " p.decentralisation, p.entropy, p.protocol_major, p.protocol_minor, p.min_utxo_value,"
        " p.min_pool_cost, p.coins_per_utxo_size, p.cost_model_id, p.price_mem, p.price_step,"
        " p.max_tx_ex_mem, p.max_tx_ex_steps, p.max_block_ex_mem, p.max_block_ex_steps,"
        " p.max_val_size, p.collateral_percent, p.max_collateral_inputs, p.registered_tx_id,"
        " p.pvt_motion_no_confidence, p.pvt_committee_normal, p.pvt_committee_no_confidence,"
        " p.pvt_hard_fork_initiation, p.dvt_motion_no_confidence, p.dvt_committee_normal,"
        " p.dvt_committee_no_confidence, p.dvt_update_to_constitution, p.dvt_hard_fork_initiation,"
        " p.dvt_p_p_network_group, p.dvt_p_p_economic_group, p.dvt_p_p_technical_group,"
        " p.dvt_p_p_gov_group, p.dvt_treasury_withdrawal, p.committee_min_size,"
        " p.committee_max_term_length, p.gov_action_lifetime, p.gov_action_deposit,"
        " p.drep_deposit, p.drep_activity "
        "FROM param_proposal AS p "
        "INNER JOIN tx ON tx.id = p.registered_tx_id "
        f"{hash_query}"
        "ORDER BY ID DESC LIMIT 1"
    )

    with execute(query=query, vars=(query_var,)) as cur:
        results = cur.fetchone()
        return ParamProposalDBRow(*results)


def query_extra_key_witness(txhash: str) -> tp.Generator[memoryview, None, None]:
    """Query extra key witness records in db-sync."""
    query = (
        "SELECT extra_key_witness.hash "
        "FROM extra_key_witness "
        "INNER JOIN tx ON tx.id = extra_key_witness.tx_id "
        "WHERE tx.hash = %s;"
    )

    with execute(query=query, vars=(rf"\x{txhash}",)) as cur:
        while (result := cur.fetchone()) is not None:
            yield result[0]


def query_epoch(
    epoch_from: int = 0, epoch_to: int = 99999999
) -> tp.Generator[EpochDBRow, None, None]:
    """Query epoch records in db-sync."""
    query_vars = (epoch_from, epoch_to)

    query = (
        "SELECT"
        " epoch.id, epoch.out_sum, epoch.fees, epoch.tx_count, epoch.blk_count, epoch.no "
        "FROM epoch "
        "WHERE (no BETWEEN %s AND %s);"
    )

    with execute(query=query, vars=query_vars) as cur:
        while (result := cur.fetchone()) is not None:
            yield EpochDBRow(*result)


def query_committee_registration(
    cold_key: str,
) -> tp.Generator[CommitteeRegistrationDBRow, None, None]:
    """Query committee registration in db-sync."""
    query = (
        "SELECT id, tx_id, cert_index, cold_key, hot_key "
        "FROM committee_registration "
        "WHERE cold_key = %s;"
    )

    with execute(query=query, vars=(rf"\x{cold_key}",)) as cur:
        while (result := cur.fetchone()) is not None:
            yield CommitteeRegistrationDBRow(*result)


def query_committee_deregistration(
    cold_key: str,
) -> tp.Generator[CommitteeDeregistrationDBRow, None, None]:
    """Query committee registration in db-sync."""
    query = (
        "SELECT id, tx_id, cert_index, voting_anchor_id, cold_key "
        "FROM committee_de_registration "
        "WHERE cold_key = %s;"
    )

    with execute(query=query, vars=(rf"\x{cold_key}",)) as cur:
        while (result := cur.fetchone()) is not None:
            yield CommitteeDeregistrationDBRow(*result)


def query_drep_registration(
    drep_hash: str, drep_deposit: int = 2000000
) -> tp.Generator[DrepRegistrationDBRow, None, None]:
    """Query drep registration in db-sync."""
    query = (
        "SELECT"
        " dr.id, dr.tx_id, dr.cert_index, dr.deposit, "
        " dr.drep_hash_id, dr.voting_anchor_id, "
        " dh.raw, dh.view, dh.has_script "
        "FROM drep_registration as dr "
        "INNER JOIN drep_hash dh on dh.id = dr.drep_hash_id "
        "WHERE dh.raw = %s "
        "AND dr.deposit = %s "
        "ORDER BY dr.tx_id;"
    )

    with execute(query=query, vars=(rf"\x{drep_hash}", drep_deposit)) as cur:
        while (result := cur.fetchone()) is not None:
            yield DrepRegistrationDBRow(*result)


def query_gov_action_proposal(
    txhash: str = "", type: str = ""
) -> tp.Generator[GovActionProposalDBRow, None, None]:
    """Query gov_action_proposal table in db-sync.

    If type is provided txhash will be ignored.
    """
    if type:
        gap_query = "gap.type = %s"
        query_var: str = type
    else:
        gap_query = "tx.hash = %s"
        query_var = rf"\x{txhash}"

    query = (
        "SELECT"
        " gap.id, gap.tx_id, gap.prev_gov_action_proposal, gap.deposit, gap.return_address,"
        " gap.expiration, gap.voting_anchor_id, gap.type, gap.description, gap.param_proposal,"
        " gap.ratified_epoch, gap.enacted_epoch, gap.dropped_epoch, gap.expired_epoch "
        "FROM gov_action_proposal as gap "
        "INNER JOIN tx ON tx.id = gap.tx_id "
        f"WHERE {gap_query};"
    )

    with execute(query=query, vars=(query_var,)) as cur:
        while (result := cur.fetchone()) is not None:
            yield GovActionProposalDBRow(*result)
