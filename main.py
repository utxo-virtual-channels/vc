from bitcoinutils.transactions import Transaction, TxInput, TxOutput, Sequence, TYPE_RELATIVE_TIMELOCK, TYPE_ABSOLUTE_TIMELOCK
from identity import Id
import txs
from helper import hash256, print_tx, gen_secret

def main():
    """
    Execute this file to get the transactions and sizes for the GC virtual channels and LN virtual channels
    constructions, both for without validity and with validity.
    """

    id_a = Id('e120477e329a0f15bcf977c86181828f2e015bfe34e2efe9af6362c8d53a13e2') # addr: mobucks9e3YkyvCL4CQN87kSTr5xypTJd9
    id_i = Id('e12049bc238a0f15bcf977c86171828f3e0363cb2ac2efe9af6362c8d53a22c5') # addr: mj5fp2UhS5uzfus2uC5RSQKLQ4p4JRxZSF
    id_b = Id('e12046ad146a0f15bcf977c86181828f1e0472ea1bd2efe9af6362c8d53a41a7') # addr: mnMpxq29PSL6nkT4WXBtKm1vKr6MmjPrWA

    tx_in_a = TxInput('e570becc3a3969f90ca89569264e46f62b0cb47f034281cbaab7afd14c769290', 1) # A in ai
    tx_in_i1 = TxInput('40054f05fe9daade599b1e4ed1bda9e7b68b148b5a0ececcec939d91564ee99c', 1) # I in ai
    tx_in_i2 = TxInput('c186ff6cb70b2333edf977cea0038e432c081284a33bc0115884058d99b18e58', 0) # I in ib
    tx_in_b = TxInput('91fc5ca20e7e0762ba911b6aec9a1d3326c7b12f415f817fa5d3a7579d8cc56e', 1) # B in ib

    c = 0.00098
    f = 0.00001
    fee = 0.00001

    # These transactions are the commitment transaction and would be replaced with real ones
    ct_ai = txs.get_TX_multisig(tx_in_a, tx_in_i1, id_a, id_i, c, fee)
    print_tx(ct_ai, 'ct_ai')
    ct_ib = txs.get_TX_multisig(tx_in_i2, tx_in_b, id_i, id_b, c, fee)
    print_tx(ct_ib, 'ct_ib')

    ct_LN_ai_a,script = txs.get_CT_LN(TxInput(ct_ai.get_txid(), 0), id_a, id_i, id_b, id_a, id_i, True, id_a, c, fee, gen_secret())
    print_tx(ct_LN_ai_a, 'ct_ai_LN_a')

    ct_LN_ai_a_val,script = txs.get_CT_LN_val(TxInput(ct_ai.get_txid(), 0), id_a, id_i, True, id_a, c, fee,
                                       gen_secret())
    print_tx(ct_LN_ai_a_val, 'ct_ai_LN_a_val')

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

    ### LIGHTNING NETWORK:

    ## Non-Validity:
    ct_LN_ai_a, script = txs.get_CT_LN(TxInput(ct_ai.get_txid(), 0), id_a, id_i, id_b, id_a, id_i, True, id_a, c, fee,
                               gen_secret())
    ct_LN_ai_i, script = txs.get_CT_LN(TxInput(ct_ai.get_txid(), 0), id_a, id_i, id_b, id_a, id_i, False, id_a, c, fee,
                               gen_secret())
    ct_LN_ib_i, script = txs.get_CT_LN(TxInput(ct_ai.get_txid(), 0), id_a, id_i, id_b, id_i, id_b, True, id_b, c, fee,
                               gen_secret())
    ct_LN_ib_b, script = txs.get_CT_LN(TxInput(ct_ai.get_txid(), 0), id_a, id_i, id_b, id_i, id_b, False, id_b, c, fee,
                               gen_secret())
    print_tx(ct_LN_ai_a, 'ct_ai_LN_a (2x)')
    print_tx(ct_LN_ib_i, 'ct_LN_ib_i (2x)')

    txf_nv_1 = txs.get_TXf_NV(TxInput(ct_LN_ai_a.get_txid(), 0), TxInput(ct_LN_ib_i.get_txid(), 0), id_a, id_b, id_i, c-2*f-2*fee, f, fee)
    txf_nv_2 = txs.get_TXf_NV(TxInput(ct_LN_ai_a.get_txid(), 0), TxInput(ct_LN_ib_b.get_txid(), 0), id_a, id_b, id_i,
                                 c - 2 * f - 2 * fee, f, fee)
    txf_nv_3 = txs.get_TXf_NV(TxInput(ct_LN_ai_i.get_txid(), 0), TxInput(ct_LN_ib_i.get_txid(), 0), id_a, id_b, id_i,
                                 c - 2 * f - 2 * fee, f, fee)
    txf_nv_4 = txs.get_TXf_NV(TxInput(ct_LN_ai_i.get_txid(), 0), TxInput(ct_LN_ib_b.get_txid(), 0), id_a, id_b, id_i,
                                 c - 2 * f - 2 * fee, f, fee)
    print_tx(txf_nv_1, 'txf_nv_1 (4x)')

    ### Validity
    ct_LN_ai_a_val, script1 = txs.get_CT_LN_val(TxInput(ct_ai.get_txid(), 0), id_a, id_i, True, id_i, c, fee,
                                       gen_secret())
    ct_LN_ai_i_val, script2 = txs.get_CT_LN_val(TxInput(ct_ai.get_txid(), 0), id_a, id_i, False, id_i, c, fee,
                                       gen_secret())
    ct_LN_ib_i_val, script3 = txs.get_CT_LN_val(TxInput(ct_ai.get_txid(), 0), id_i, id_b, True, id_b, c, fee,
                                       gen_secret())
    ct_LN_ib_b_val, script4 = txs.get_CT_LN_val(TxInput(ct_ai.get_txid(), 0), id_i, id_b, False, id_b, c, fee,
                                       gen_secret())
    print_tx(ct_LN_ai_a_val, 'ct_LN_ai_a_val (4x)')

    txf_v_ai_a = txs.get_TXf_V_LN(TxInput(ct_LN_ai_a.get_txid(), 0), id_a, id_b, id_i, c - f - 2 * fee, f, fee, script1)
    txf_v_ai_i = txs.get_TXf_V_LN(TxInput(ct_LN_ai_i.get_txid(), 0), id_a, id_b, id_i, c - f - 2 * fee, f, fee, script2)
    print_tx(txf_v, 'txf_v (2x)')

    txrefund_v_1 = txs.get_TXrefund_V_LN(TxInput(txf_v_ai_a.get_txid(), 1), TxInput(ct_LN_ib_i_val.get_txid(), 0), id_a, id_b, id_i,
                                    c - f - 2 * fee, f, fee, script3)
    txrefund_v_2 = txs.get_TXrefund_V_LN(TxInput(txf_v_ai_a.get_txid(), 1), TxInput(ct_LN_ib_b_val.get_txid(), 0), id_a,
                                      id_b, id_i,
                                      c - f - 2 * fee, f, fee, script4)
    txrefund_v_3 = txs.get_TXrefund_V_LN(TxInput(txf_v_ai_i.get_txid(), 1), TxInput(ct_LN_ib_i_val.get_txid(), 0), id_a,
                                      id_b, id_i,
                                      c - f - 2 * fee, f, fee, script3)
    txrefund_v_4 = txs.get_TXrefund_V_LN(TxInput(txf_v_ai_i.get_txid(), 1), TxInput(ct_LN_ib_b_val.get_txid(), 0), id_a,
                                      id_b, id_i,
                                      c - f - 2 * fee, f, fee, script4)
    print_tx(txrefund_v_1, 'txrefund_v (4x)')



if __name__ == "__main__":
    main()