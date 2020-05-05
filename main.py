from bitcoinutils.transactions import Transaction, TxInput, TxOutput, Sequence, TYPE_RELATIVE_TIMELOCK, TYPE_ABSOLUTE_TIMELOCK
from identity import Id
import txs
from helper import hash256, print_tx

def main():

    id_a = Id('e120477e329a0f15bcf977c86181828f2e015bfe34e2efe9af6362c8d53a13e2') # addr: mobucks9e3YkyvCL4CQN87kSTr5xypTJd9
    id_i = Id('e12049bc238a0f15bcf977c86171828f3e0363cb2ac2efe9af6362c8d53a22c5') # addr: mj5fp2UhS5uzfus2uC5RSQKLQ4p4JRxZSF
    id_b = Id('e12046ad146a0f15bcf977c86181828f1e0472ea1bd2efe9af6362c8d53a41a7') # addr: mnMpxq29PSL6nkT4WXBtKm1vKr6MmjPrWA

    tx_in_a = TxInput('1bc0352ce8ffdda1d516c748d7e13a16488ae8d1bfb1945a22a7d5be2d688163', 1) # A in ai
    tx_in_i1 = TxInput('f3a4dbfe080a850bbe4551f45a639aa9b2e8f7ea8609070b077e7060ba5aff23', 1) # I in ai
    tx_in_i2 = TxInput('ea7e68713b9dfcf5088a0747a4119a1900e577f7545deccfef90179a7566843e', 1) # I in ib
    tx_in_b = TxInput('746e1ea87bb9d3005cc3486b740a57f1a2bddf63dd22f1ef438355f7b1ff874e', 0) # B in ib

    c = 0.0001
    f = 0.00001
    fee = 0.00001

    # These transactions are the commitment transaction and would be replace with real ones
    ct_ai = txs.get_TX_multisig(tx_in_a, tx_in_i1, id_a, id_i, c, fee)
    print_tx(ct_ai, 'ct_ai')
    ct_ib = txs.get_TX_multisig(tx_in_i2, tx_in_b, id_i, id_b, c, fee)
    print_tx(ct_ib, 'ct_ib')

    #### Transaction required for the Validity construction
    print('Validity')
    # The two split transactions:
    txa_v = txs.get_TX_txa_V(TxInput(ct_ai.get_txid(), 0), id_a, id_i, c-f-fee, f, fee)
    print_tx(txa_v, 'txa_v')
    txb_v = txs.get_TX_txa_V(TxInput(ct_ib.get_txid(), 0), id_i, id_b, c-f-fee, f, fee)
    print_tx(txb_v, 'txb_v')
    # The two transactions TX_f and TX_refund:
    txf_v = txs.get_TXf_V(TxInput(txa_v.get_txid(), 0), id_a, id_b, id_i, c-f-2*fee, f, fee)
    print_tx(txf_v, 'txf_v')
    txrefund_v = txs.get_TXrefund_V(TxInput(txf_v.get_txid(), 1), TxInput(txb_v.get_txid(), 0), id_a, id_b, id_i, c-f-2*fee, f, fee)
    print_tx(txrefund_v, 'txrefund_v')
    #### Transaction required for the Non-Validity
    print('Non-Validity')
    # The two split transactions:
    txa_nv = txs.get_TX_txa_NV(TxInput(ct_ai.get_txid(), 0), id_a, id_b, id_i, c-fee, f, fee, ai=True)
    print_tx(txa_nv, 'txa_nv')
    txb_nv = txs.get_TX_txa_NV(TxInput(ct_ib.get_txid(), 0), id_a, id_b, id_i, c-fee, f, fee, ai=False)
    print_tx(txb_nv, 'txb_nv')
    # The transaction TX_f:
    txf_nv = txs.get_TXf_NV(TxInput(txa_nv.get_txid(), 0), TxInput(txb_nv.get_txid(), 0), id_a, id_b, id_i, c-2*f-2*fee, f, fee)
    print_tx(txf_nv, 'txf_nv')

if __name__ == "__main__":
    main()