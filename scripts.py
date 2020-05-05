from bitcoinutils.script import Script
from identity import Id
import init
import consts
import scripts

init.initNetwork()

def get_script_txa_nv(id_a: Id, id_b: Id, id_i: id, timedelay: int) -> Script:
    return Script([
        id_a.pk.to_hex(), 'OP_CHECKSIGVERIFY',
        'OP_DUP', id_b.pk.to_hex(), 'OP_CHECKSIG',
        'OP_IF',
        'OP_DROP', id_i.pk.to_hex(), 'OP_CHECKSIG',
        'OP_ELSE',
        timedelay, 'OP_CHECKSEQUENCEVERIFY',
        'OP_ENDIF'])

def get_script_txa_v(id_a: Id, id_i: id, timedelay: int) -> Script:
    return Script([
        id_i.pk.to_hex(), 'OP_CHECKSIGVERIFY',
        'OP_DUP', id_a.pk.to_hex(), 'OP_CHECKSIG',
        'OP_NOTIF',
            timedelay, 'OP_CHECKLOCKTIMEVERIFY',
        'OP_ENDIF'])

def getScriptTXf(idA: Id, idB: Id) :
    scriptFToutput = Script([
                    idA.pk.to_hex(), 'OP_CHECKSIGVERIFY', idB.pk.to_hex(), 'OP_CHECKSIGVERIFY', 0x1]) # input: sigB, sigA
    return scriptFToutput

def get_script_3sig(id_a: Id, id_b: Id, id_i: Id) -> Script:
    script = Script([
                    id_a.pk.to_hex(), 'OP_CHECKSIGVERIFY', id_b.pk.to_hex(), 'OP_CHECKSIGVERIFY', id_i.pk.to_hex(),
        'OP_CHECKSIGVERIFY', 0x1]) # input: sigB, sigA
    return script

def get_script_2sig(id_a: Id, id_b: Id) -> Script:
    script = Script([
                    id_a.pk.to_hex(), 'OP_CHECKSIGVERIFY', id_b.pk.to_hex(), 'OP_CHECKSIGVERIFY', 0x1]) # input: sigB, sigA
    return script