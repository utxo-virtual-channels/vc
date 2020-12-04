from typing import Tuple

from bitcoinutils.transactions import Transaction, TxOutput, TxInput
from bitcoinutils.script import Script
from identity import Id
import init
import scripts
import consts
from helper import hash256

init.initNetwork()


def get_TX_multisig(tx_in0: TxInput, tx_in1: TxInput, id_l: Id, id_r: Id, c: float, fee: float, timedelay: int = 0x02) \
        -> Transaction:
    tx_out = TxOutput(c - fee, scripts.get_script_2sig(id_l, id_r))

    tx = Transaction([tx_in0, tx_in1], [tx_out])

    sig_l = id_l.sk.sign_input(tx, 0, id_l.p2pkh)
    sig_r = id_r.sk.sign_input(tx, 1, id_r.p2pkh)

    tx_in0.script_sig = Script([sig_l, id_l.pk.to_hex()])
    tx_in1.script_sig = Script([sig_r, id_r.pk.to_hex()])

    return tx


def get_TXf_NV(tx_in0: TxInput, tx_in1: TxInput, id_a: Id, id_b: Id, id_i: Id, c: float, f: float, fee: float,
               timedelay: int = 0x02) \
        -> Transaction:
    tx_out0 = TxOutput(c, Script([
        id_a.pk.to_hex(), 'OP_CHECKSIGVERIFY', id_b.pk.to_hex(), 'OP_CHECKSIGVERIFY', 0x1]))
    tx_out1 = TxOutput(c + f / 2, id_i.p2pkh)

    tx = Transaction([tx_in0, tx_in1], [tx_out0, tx_out1])

    script_in = scripts.get_script_txa_nv(id_a, id_b, id_i, timedelay)

    sig_a = id_a.sk.sign_input(tx, 0, script_in)
    sig_b = id_b.sk.sign_input(tx, 0, script_in)
    sig_i = id_i.sk.sign_input(tx, 0, script_in)
    sig_a1 = id_a.sk.sign_input(tx, 1, script_in)
    sig_b1 = id_b.sk.sign_input(tx, 1, script_in)
    sig_i1 = id_i.sk.sign_input(tx, 1, script_in)

    tx_in0.script_sig = Script([sig_i, sig_b, sig_a])
    tx_in1.script_sig = Script([sig_i1, sig_b1, sig_a1])

    return tx


def get_TXf_V(tx_in: TxInput, id_a: Id, id_b: Id, id_i: Id, c: float, f: float, fee: float, timedelay: int = 0x02) \
        -> Transaction:
    tx_out0 = TxOutput(c, Script([
        id_a.pk.to_hex(), 'OP_CHECKSIGVERIFY', id_b.pk.to_hex(), 'OP_CHECKSIGVERIFY', 0x1]))
    tx_out1 = TxOutput(f / 2, id_i.p2pkh)

    tx = Transaction([tx_in], [tx_out0, tx_out1])

    script_in = scripts.scripts.get_script_txa_v(id_a, id_i, timedelay)

    sig_a = id_a.sk.sign_input(tx, 0, script_in)
    sig_i = id_i.sk.sign_input(tx, 0, script_in)

    tx_in.script_sig = Script([sig_a, sig_i])

    return tx


def get_TXrefund_V(tx_in0: TxInput, tx_in1: TxInput, id_a: Id, id_b: Id, id_i: Id, c: float, f: float, fee: float,
                   timedelay: int = 0x02) \
        -> Transaction:
    tx_out = TxOutput(c + f, id_i.p2pkh)

    tx = Transaction([tx_in0, tx_in1], [tx_out])

    script_in = scripts.scripts.get_script_txa_v(id_i, id_b, timedelay)

    sig_i = id_i.sk.sign_input(tx, 0, id_i.p2pkh)
    sig_i2 = id_i.sk.sign_input(tx, 1, script_in)
    sig_b = id_b.sk.sign_input(tx, 1, script_in)

    tx_in0.script_sig = Script([sig_i, id_i.pk.to_hex()])
    tx_in1.script_sig = Script([sig_i2, sig_b])

    return tx


def get_TX_txa_NV(tx_in: TxInput, id_a: Id, id_b: Id, id_i: Id, c: float, f: float, fee: float, ai=True,
                  timedelay: int = 0x02) \
        -> Transaction:
    tx_out = TxOutput(c - fee, scripts.get_script_txa_nv(id_a, id_b, id_i, timedelay))

    tx = Transaction([tx_in], [tx_out])

    if ai:
        script_in = scripts.get_script_2sig(id_a, id_i)

        sig_a = id_a.sk.sign_input(tx, 0, script_in)
        sig_i = id_i.sk.sign_input(tx, 0, script_in)

        tx_in.script_sig = Script([sig_i, sig_a])
    else:
        script_in = scripts.get_script_2sig(id_i, id_b)

        sig_i = id_i.sk.sign_input(tx, 0, script_in)
        sig_b = id_b.sk.sign_input(tx, 0, script_in)

        tx_in.script_sig = Script([sig_b, sig_i])
    return tx


def get_TX_txa_V(tx_in: TxInput, id_l: Id, id_r: Id, c: float, f: float, fee: float, timedelay: int = 0x02) \
        -> Transaction:
    tx_out = TxOutput(c + f / 2, scripts.get_script_txa_v(id_l, id_r, timedelay))

    tx = Transaction([tx_in], [tx_out])

    script_in = scripts.get_script_2sig(id_l, id_r)

    sig_l = id_l.sk.sign_input(tx, 0, script_in)
    sig_r = id_r.sk.sign_input(tx, 0, script_in)

    tx_in.script_sig = Script([sig_r, sig_l])

    return tx

def get_CT_LN(tx_in: TxInput, id_a: Id, id_i: Id, id_b: Id, id_l: Id, id_r: Id, ct_l: bool, id_punish_vc: Id, c: float,
              fee: float, rev_secret: str, timedelay1: int = 0x02, timedelay2: int = 0x04) \
        -> Tuple[Transaction, Script]:
    """
    id_post ... id of the party posting this CT
    id_punish ... id of the party punishing the channel
    id_punish_vc ... id of the party punishing the VC
    """
    if ct_l:
        id_post = id_l
        id_punish = id_r
    else:
        id_post = id_r
        id_punish = id_l

    script = scripts.get_script_ln_ct(id_a, id_b, id_i, id_punish_vc, id_punish, hash256(rev_secret), timedelay1,
                                      timedelay2)
    tx_out0 = TxOutput(c - fee, script)
    tx_out1 = TxOutput(c - fee, scripts.get_output_ln_ct(id_post, id_punish, hash256(rev_secret), timedelay1))
    tx_out2 = TxOutput(c - fee, id_punish.p2pkh)

    tx = Transaction([tx_in], [tx_out0, tx_out1, tx_out2])

    sig_l = id_post.sk.sign_input(tx, 0, scripts.get_script_2sig(id_l, id_r))
    sig_r = id_punish.sk.sign_input(tx, 0, scripts.get_script_2sig(id_l, id_r))

    tx_in.script_sig = Script([sig_r, sig_l])

    return tx, script


def get_CT_LN_val(tx_in: TxInput, id_l: Id, id_r: Id, ct_l: bool, id_punish_vc: Id, c: float,
                  fee: float, rev_secret: str, timedelay1: int = 0x02, timedelay2: int = 0x04) \
        -> Tuple[Transaction, Script]:
    """
    id_post ... id of the party posting this CT
    id_punish ... id of the party punishing the channel
    id_punish_vc ... id of the party punishing the VC
    """
    if ct_l:
        id_post = id_l
        id_punish = id_r
    else:
        id_post = id_r
        id_punish = id_l

    script = scripts.get_script_ln_ct_val(id_l, id_r, id_punish_vc, id_punish, hash256(rev_secret),
                                          timedelay1, timedelay2)
    tx_out0 = TxOutput(c - fee, script)
    tx_out1 = TxOutput(c - fee, scripts.get_output_ln_ct(id_post, id_punish, hash256(rev_secret), timedelay1))
    tx_out2 = TxOutput(c - fee, id_punish.p2pkh)

    tx = Transaction([tx_in], [tx_out0, tx_out1, tx_out2])

    sig_l = id_post.sk.sign_input(tx, 0, scripts.get_script_2sig(id_l, id_r))
    sig_r = id_punish.sk.sign_input(tx, 0, scripts.get_script_2sig(id_l, id_r))

    tx_in.script_sig = Script([sig_r, sig_l])

    return tx, script

def get_TXf_NV_LN(tx_in0: TxInput, tx_in1: TxInput, id_a: Id, id_b: Id, id_i: Id, c: float, f: float, fee: float, script1, script2,
               timedelay: int = 0x02) \
        -> Transaction:
    tx_out0 = TxOutput(c, Script([
        id_a.pk.to_hex(), 'OP_CHECKSIGVERIFY', id_b.pk.to_hex(), 'OP_CHECKSIGVERIFY', 0x1]))
    tx_out1 = TxOutput(c + f / 2, id_i.p2pkh)

    tx = Transaction([tx_in0, tx_in1], [tx_out0, tx_out1])

    script_in = scripts.get_script_txa_nv(id_a, id_b, id_i, timedelay)

    sig_a = id_a.sk.sign_input(tx, 0, script1)
    sig_b = id_b.sk.sign_input(tx, 0, script1)
    sig_i = id_i.sk.sign_input(tx, 0, script1)
    sig_a1 = id_a.sk.sign_input(tx, 1, script2)
    sig_b1 = id_b.sk.sign_input(tx, 1, script2)
    sig_i1 = id_i.sk.sign_input(tx, 1, script2)

    tx_in0.script_sig = Script([sig_i, sig_b, sig_a, 0x0])
    tx_in1.script_sig = Script([sig_i1, sig_b1, sig_a1, 0x0])

    return tx

def get_TXf_V_LN(tx_in: TxInput, id_a: Id, id_b: Id, id_i: Id, c: float, f: float, fee: float, script: Script, timedelay: int = 0x02) \
        -> Transaction:
    tx_out0 = TxOutput(c, Script([
        id_a.pk.to_hex(), 'OP_CHECKSIGVERIFY', id_b.pk.to_hex(), 'OP_CHECKSIGVERIFY', 0x1]))
    tx_out1 = TxOutput(f / 2, id_i.p2pkh)

    tx = Transaction([tx_in], [tx_out0, tx_out1])

    sig_a = id_a.sk.sign_input(tx, 0, script)
    sig_i = id_i.sk.sign_input(tx, 0, script)

    tx_in.script_sig = Script([sig_a, sig_i, 0x0])

    return tx


def get_TXrefund_V_LN(tx_in0: TxInput, tx_in1: TxInput, id_a: Id, id_b: Id, id_i: Id, c: float, f: float, fee: float, script: Script,
                   timedelay: int = 0x02) \
        -> Transaction:
    tx_out = TxOutput(c + f, id_i.p2pkh)

    tx = Transaction([tx_in0, tx_in1], [tx_out])

    script_in = scripts.scripts.get_script_txa_v(id_i, id_b, timedelay)

    sig_i = id_i.sk.sign_input(tx, 0, id_i.p2pkh)
    sig_i2 = id_i.sk.sign_input(tx, 1, script)
    sig_b = id_b.sk.sign_input(tx, 1, script)

    tx_in0.script_sig = Script([sig_i, id_i.pk.to_hex()])
    tx_in1.script_sig = Script([sig_i2, sig_b, 0x0])

    return tx