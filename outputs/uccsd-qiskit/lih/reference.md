# LIH - reference data (uccsd-qiskit)

Usage instructions: ../../../docs/EXPERIMENTALIST_GUIDE.md

Ansatz: `uccsd-qiskit`: UCCSD (qiskit-nature) on Hartree-Fock - the original method, any molecule.

## Energies (Hartree)

- VQE (this circuit):        -7.88217588
- Exact diagonalization (qiskit-nature qubit Hamiltonian): -7.88217599
- Independent classical reference (PySCF CASCI (2e, 5o), matching the frozen-core active space): -7.88217599

## Formula

    E_total = energy_offset + sum_over_all_terms( coefficient * <term> )

    energy_offset = -6.80295271 Ha

## Circuit cost on hardware

Every circuit is a sequence of moments separated by barriers: CZ layers (CZ gates on
disjoint pairs, run in parallel) and single-qubit blocks [Z_1, global sqrt(X), Z_2,
global sqrt(X), Z_3] (`gsx` = one global sqrt(X) pulse on all qubits).

| File | CZ gates | CZ layers | Single-qubit blocks | Global sqrt(X) pulses |
|------|----------|-----------|---------------------|-----------------------|
| ansatz.qasm | 530 | 507 | 496 | 992 |
| measure_group_0.qasm | 530 | 507 | 496 | 992 |
| measure_group_1.qasm | 530 | 507 | 496 | 992 |
| measure_group_2.qasm | 530 | 507 | 496 | 992 |
| measure_group_3.qasm | 530 | 507 | 496 | 992 |
| measure_group_4.qasm | 530 | 507 | 496 | 992 |
| measure_group_5.qasm | 530 | 507 | 496 | 992 |
| measure_group_6.qasm | 530 | 507 | 496 | 992 |
| measure_group_7.qasm | 530 | 507 | 496 | 992 |
| measure_group_8.qasm | 530 | 507 | 496 | 992 |
| measure_group_9.qasm | 530 | 507 | 496 | 992 |
| measure_group_10.qasm | 530 | 507 | 496 | 992 |
| measure_group_11.qasm | 530 | 507 | 496 | 992 |
| measure_group_12.qasm | 530 | 507 | 496 | 992 |
| measure_group_13.qasm | 530 | 507 | 496 | 992 |
| measure_group_14.qasm | 530 | 507 | 496 | 992 |
| measure_group_15.qasm | 530 | 507 | 496 | 992 |
| measure_group_16.qasm | 530 | 507 | 496 | 992 |
| measure_group_17.qasm | 530 | 507 | 496 | 992 |
| measure_group_18.qasm | 530 | 507 | 496 | 992 |
| measure_group_19.qasm | 530 | 507 | 496 | 992 |
| measure_group_20.qasm | 530 | 507 | 496 | 992 |
| measure_group_21.qasm | 530 | 507 | 496 | 992 |
| measure_group_22.qasm | 530 | 507 | 496 | 992 |
| measure_group_23.qasm | 530 | 507 | 496 | 992 |
| measure_group_24.qasm | 530 | 507 | 496 | 992 |
| measure_group_25.qasm | 530 | 507 | 496 | 992 |
| measure_group_26.qasm | 530 | 507 | 496 | 992 |
| measure_group_27.qasm | 530 | 507 | 496 | 992 |
| measure_group_28.qasm | 530 | 507 | 496 | 992 |
| measure_group_29.qasm | 530 | 507 | 496 | 992 |
| measure_group_30.qasm | 530 | 507 | 496 | 992 |
| measure_group_31.qasm | 530 | 507 | 496 | 992 |
| measure_group_32.qasm | 530 | 507 | 496 | 992 |
| measure_group_33.qasm | 530 | 507 | 496 | 992 |
| measure_group_34.qasm | 530 | 507 | 496 | 992 |
| measure_group_35.qasm | 530 | 507 | 496 | 992 |
| measure_group_36.qasm | 530 | 507 | 496 | 992 |
| measure_group_37.qasm | 530 | 507 | 496 | 992 |
| measure_group_38.qasm | 530 | 507 | 496 | 992 |
| measure_group_39.qasm | 530 | 507 | 496 | 992 |
| measure_group_40.qasm | 530 | 507 | 496 | 992 |
| measure_group_41.qasm | 530 | 507 | 496 | 992 |
| measure_group_42.qasm | 530 | 507 | 496 | 992 |
| measure_group_43.qasm | 530 | 507 | 496 | 992 |
| measure_group_44.qasm | 530 | 507 | 496 | 992 |
| measure_group_45.qasm | 530 | 507 | 496 | 992 |
| measure_group_46.qasm | 530 | 507 | 496 | 992 |
| measure_group_47.qasm | 530 | 507 | 496 | 992 |
| measure_group_48.qasm | 530 | 507 | 496 | 992 |
| measure_group_49.qasm | 530 | 507 | 496 | 992 |
| measure_group_50.qasm | 530 | 507 | 496 | 992 |
| measure_group_51.qasm | 530 | 507 | 496 | 992 |
| measure_group_52.qasm | 530 | 507 | 496 | 992 |
| measure_group_53.qasm | 530 | 507 | 496 | 992 |
| measure_group_54.qasm | 530 | 507 | 496 | 992 |
| measure_group_55.qasm | 530 | 507 | 496 | 992 |
| measure_group_56.qasm | 530 | 507 | 496 | 992 |
| measure_group_57.qasm | 530 | 507 | 496 | 992 |

## Pauli terms per measurement group

(qubit ordering: rightmost character = qubit 0; a group's basis label is its per-qubit measurement basis in that same ordering)

measure_group_0.qasm  (basis YYZZYYYZZY):
    +0.00586267  IYZZYIYZZY
    -0.00489370  YYIIIIYZZY
    -0.00489370  IYZZYYYIII
    +0.00492832  YYIIIYYIII
    -0.00088575  IIIIIYIZZY
    -0.00088575  YIZZYIIIII
    +0.08448401  IIIZIIIIZI
    +0.06018155  IIIIIIIZZI
    +0.07050101  IIZIIIIIZI
    +0.07050101  IIIZIIIZII
    +0.06018155  IIZZIIIIII
    -0.39048044  IIIIIIIIZI
    -0.39048044  IIIZIIIIII
    -0.42609505  IIIIIIIZII
    -0.42609505  IIZIIIIIII
    +0.07823638  IIZIIIIZII
    +1.06993761  IIIIIIIIII

measure_group_1.qasm  (basis XXZZXYYZZY):
    +0.00586267  IXZZXIYZZY
    -0.00489370  XXIIIIYZZY
    -0.00489370  IXZZXYYIII
    +0.00492832  XXIIIYYIII
    -0.00088575  XIZZXIIIII

measure_group_2.qasm  (basis YYZZYXXZZX):
    +0.00586267  IYZZYIXZZX
    -0.00489370  YYIIIIXZZX
    -0.00489370  IYZZYXXIII
    +0.00492832  YYIIIXXIII
    -0.00088575  IIIIIXIZZX

measure_group_3.qasm  (basis XXZZXXXZZX):
    +0.00586267  IXZZXIXZZX
    -0.00489370  XXIIIIXZZX
    -0.00489370  IXZZXXXIII
    +0.00492832  XXIIIXXIII

measure_group_4.qasm  (basis YZYZYYZYZY):
    +0.00586267  IIYZYIIYZY
    -0.00489370  YZYIIIIYZY
    -0.00489370  IIYZYYZYII
    +0.00492832  YZYIIYZYII
    -0.00088575  IIIIIYZIZY
    -0.00088575  YZIZYIIIII
    +0.06018155  IIIIIIZIZI
    +0.07050101  IZIIIIIIZI
    +0.07050101  IIIZIIZIII
    +0.06018155  IZIZIIIIII
    -0.42609505  IIIIIIZIII
    -0.42609505  IZIIIIIIII
    +0.07823638  IZIIIIZIII

measure_group_5.qasm  (basis XZXZXYZYZY):
    +0.00586267  IIXZXIIYZY
    -0.00489370  XZXIIIIYZY
    -0.00489370  IIXZXYZYII
    +0.00492832  XZXIIYZYII
    -0.00088575  XZIZXIIIII

measure_group_6.qasm  (basis YZYZYXZXZX):
    +0.00586267  IIYZYIIXZX
    -0.00489370  YZYIIIIXZX
    -0.00489370  IIYZYXZXII
    +0.00492832  YZYIIXZXII
    -0.00088575  IIIIIXZIZX

measure_group_7.qasm  (basis XZXZXXZXZX):
    +0.00586267  IIXZXIIXZX
    -0.00489370  XZXIIIIXZX
    -0.00489370  IIXZXXZXII
    +0.00492832  XZXIIXZXII

measure_group_8.qasm  (basis ZYZYYYYZZY):
    +0.00481813  IYZYIIYZZY
    -0.00343307  IYZYIYYIII
    -0.00185422  IIIYYIIIZI
    +0.00285920  ZIIYYIIIII
    -0.00142795  IIIYYIIZII
    +0.00339018  IIZYYIIIII
    +0.06036712  ZIIIIIIIZI
    -0.00362934  IIIYYIIIII
    +0.06704889  ZIIIIIIZII
    +0.06212057  ZIZIIIIIII
    -0.56446402  ZIIIIIIIII

measure_group_9.qasm  (basis ZXZXXYYZZY):
    +0.00481813  IXZXIIYZZY
    -0.00343307  IXZXIYYIII
    -0.00185422  IIIXXIIIZI
    +0.00285920  ZIIXXIIIII
    -0.00142795  IIIXXIIZII
    +0.00339018  IIZXXIIIII
    -0.00362934  IIIXXIIIII

measure_group_10.qasm  (basis YYZYZXXZZX):
    +0.00481813  IYZYIIXZZX
    -0.00343307  IYZYIXXIII
    -0.00398149  YIZYIIIIII
    +0.05593899  IIIIZIIIZI
    +0.06760577  IIIIZIIZII
    +0.06174311  IIZIZIIIII
    -0.29860906  IIIIZIIIII

measure_group_11.qasm  (basis XXZXIXXZZX):
    +0.00481813  IXZXIIXZZX
    -0.00343307  IXZXIXXIII
    -0.00398149  XIZXIIIIII

measure_group_12.qasm  (basis YYZZYZYZYY):
    +0.00481813  IYZZYIYZYI
    -0.00343307  YYIIIIYZYI
    -0.00185422  IIIZIIIIYY
    +0.00285920  IIIIIZIIYY
    +0.00339018  IIIIIIIZYY
    -0.00142795  IIZIIIIIYY
    +0.06036712  IIIZIZIIII
    -0.00362934  IIIIIIIIYY
    +0.06212057  IIIIIZIZII
    +0.06704889  IIZIIZIIII
    -0.56446402  IIIIIZIIII

measure_group_13.qasm  (basis XXZZXYYZYZ):
    +0.00481813  IXZZXIYZYI
    -0.00343307  XXIIIIYZYI
    -0.00398149  IIIIIYIZYI
    +0.05593899  IIIZIIIIIZ
    +0.06174311  IIIIIIIZIZ
    +0.06760577  IIZIIIIIIZ
    -0.29860906  IIIIIIIIIZ

measure_group_14.qasm  (basis YYZZYZXZXX):
    +0.00481813  IYZZYIXZXI
    -0.00343307  YYIIIIXZXI
    -0.00185422  IIIZIIIIXX
    +0.00285920  IIIIIZIIXX
    +0.00339018  IIIIIIIZXX
    -0.00142795  IIZIIIIIXX
    -0.00362934  IIIIIIIIXX

measure_group_15.qasm  (basis XXZZXXXZXI):
    +0.00481813  IXZZXIXZXI
    -0.00343307  XXIIIIXZXI
    -0.00398149  IIIIIXIZXI

measure_group_16.qasm  (basis YZZZYYZZZY):
    +0.03096781  YZZZYYZZZY
    +0.00307038  IIIZIYZZZY
    +0.00307038  YZZZYIIIZI
    -0.01285481  IIIIIYZZZY
    -0.01285481  YZZZYIIIII
    +0.00400794  IIZIIYZZZY
    +0.00400794  IZIIIYZZZY
    +0.00400794  YZZZYIIZII
    +0.00400794  YZZZYIZIII
    +0.00540949  IIIIIYZZIY
    +0.00540949  YZZIYIIIII
    +0.06558452  IIIIIIZZII
    +0.06980181  IZIIIIIZII
    +0.06980181  IIZIIIZIII
    +0.06558452  IZZIIIIIII

measure_group_17.qasm  (basis XZZZXYZZZY):
    +0.03096781  XZZZXYZZZY
    +0.00307038  XZZZXIIIZI
    -0.01285481  XZZZXIIIII
    +0.00400794  XZZZXIIZII
    +0.00400794  XZZZXIZIII
    +0.00540949  XZZIXIIIII

measure_group_18.qasm  (basis YZZZYXZZZX):
    +0.03096781  YZZZYXZZZX
    +0.00307038  IIIZIXZZZX
    -0.01285481  IIIIIXZZZX
    +0.00400794  IIZIIXZZZX
    +0.00400794  IZIIIXZZZX
    +0.00540949  IIIIIXZZIX

measure_group_19.qasm  (basis XZZZXXZZZX):
    +0.03096781  XZZZXXZZZX

measure_group_20.qasm  (basis YZYYYYZYZY):
    +0.00481813  IIYYIIIYZY
    -0.00343307  IIYYIYZYII
    -0.00398149  YZIYIIIIII
    -0.00142795  IIIYYIZIII
    +0.00339018  IZIYYIIIII

measure_group_21.qasm  (basis XZXXXYZYZY):
    +0.00481813  IIXXIIIYZY
    -0.00343307  IIXXIYZYII
    -0.00398149  XZIXIIIIII
    -0.00142795  IIIXXIZIII
    +0.00339018  IZIXXIIIII

measure_group_22.qasm  (basis ZZYYZXZXZX):
    +0.00481813  IIYYIIIXZX
    -0.00343307  IIYYIXZXII
    +0.08254366  ZIIIZIIIII
    +0.06760577  IIIIZIZIII
    +0.06704889  ZIIIIIZIII
    +0.06174311  IZIIZIIIII
    +0.06212057  ZZIIIIIIII

measure_group_23.qasm  (basis IIXXIXZXZX):
    +0.00481813  IIXXIIIXZX
    -0.00343307  IIXXIXZXII

measure_group_24.qasm  (basis YZYZYYZYYY):
    +0.00481813  IIYZYIIYYI
    -0.00343307  YZYIIIIYYI
    -0.00398149  IIIIIYZIYI
    +0.00339018  IIIIIIZIYY
    -0.00142795  IZIIIIIIYY

measure_group_25.qasm  (basis XZXZXZZYYZ):
    +0.00481813  IIXZXIIYYI
    -0.00343307  XZXIIIIYYI
    +0.08254366  IIIIIZIIIZ
    +0.06174311  IIIIIIZIIZ
    +0.06760577  IZIIIIIIIZ
    +0.06212057  IIIIIZZIII
    +0.06704889  IZIIIZIIII

measure_group_26.qasm  (basis YZYZYXZXXX):
    +0.00481813  IIYZYIIXXI
    -0.00343307  YZYIIIIXXI
    -0.00398149  IIIIIXZIXI
    +0.00339018  IIIIIIZIXX
    -0.00142795  IZIIIIIIXX

measure_group_27.qasm  (basis XZXZXIIXXI):
    +0.00481813  IIXZXIIXXI
    -0.00343307  XZXIIIIXXI

measure_group_28.qasm  (basis ZYZYYZYZYY):
    +0.01031945  IYZYIIYZYI
    +0.00325324  IIIYYIIIYY
    +0.01082323  ZIIIIIIIYY
    +0.01082323  IIIYYZIIII
    +0.11349047  ZIIIIZIIII

measure_group_29.qasm  (basis IXZXXZYZYY):
    +0.01031945  IXZXIIYZYI
    +0.00325324  IIIXXIIIYY
    +0.01082323  IIIXXZIIII

measure_group_30.qasm  (basis ZYZYYIXZXX):
    +0.01031945  IYZYIIXZXI
    +0.00325324  IIIYYIIIXX
    +0.01082323  ZIIIIIIIXX

measure_group_31.qasm  (basis IXZXXIXZXX):
    +0.01031945  IXZXIIXZXI
    +0.00325324  IIIXXIIIXX

measure_group_32.qasm  (basis YZZZYYZZYY):
    -0.00863495  YZZZYIIIYY
    -0.00796403  YZZZYYZZYI
    -0.00899549  IIIZIYZZYI
    +0.02407755  IIIIIYZZYI
    -0.00054842  IIZIIYZZYI
    -0.00054842  IZIIIYZZYI

measure_group_33.qasm  (basis XZZZXYZZYY):
    -0.00863495  XZZZXIIIYY
    -0.00796403  XZZZXYZZYI

measure_group_34.qasm  (basis YZZZYXZZXX):
    -0.00863495  YZZZYIIIXX
    -0.00796403  YZZZYXZZXI
    -0.00899549  IIIZIXZZXI
    +0.02407755  IIIIIXZZXI
    -0.00054842  IIZIIXZZXI
    -0.00054842  IZIIIXZZXI

measure_group_35.qasm  (basis XZZZXXZZXX):
    -0.00863495  XZZZXIIIXX
    -0.00796403  XZZZXXZZXI

measure_group_36.qasm  (basis YZZYYYZZZY):
    -0.00863495  IIIYYYZZZY
    -0.00796403  YZZYIYZZZY
    -0.00899549  YZZYIIIIZI
    +0.02407755  YZZYIIIIII
    -0.00054842  YZZYIIIZII
    -0.00054842  YZZYIIZIII

measure_group_37.qasm  (basis XZZXXYZZZY):
    -0.00863495  IIIXXYZZZY
    -0.00796403  XZZXIYZZZY
    -0.00899549  XZZXIIIIZI
    +0.02407755  XZZXIIIIII
    -0.00054842  XZZXIIIZII
    -0.00054842  XZZXIIZIII

measure_group_38.qasm  (basis YZZYYXZZZX):
    -0.00863495  IIIYYXZZZX
    -0.00796403  YZZYIXZZZX

measure_group_39.qasm  (basis XZZXXXZZZX):
    -0.00863495  IIIXXXZZZX
    -0.00796403  XZZXIXZZZX

measure_group_40.qasm  (basis ZYYYYIYYYZ):
    +0.01031945  IIYYIIIYYI
    +0.00421728  IYYIIIYYII
    +0.01212332  IIIYYIIIIZ
    +0.11351147  ZIIIIIIIIZ

measure_group_41.qasm  (basis IXXXXIYYYZ):
    +0.01031945  IIXXIIIYYI
    +0.00421728  IXXIIIYYII
    +0.01212332  IIIXXIIIIZ

measure_group_42.qasm  (basis IYYYZZXXXX):
    +0.01031945  IIYYIIIXXI
    +0.00421728  IYYIIIXXII
    +0.01212332  IIIIZIIIXX
    +0.11351147  IIIIZZIIII

measure_group_43.qasm  (basis IXXXZIXXXZ):
    +0.01031945  IIXXIIIXXI
    +0.00421728  IXXIIIXXII
    +0.12191619  IIIIZIIIIZ

measure_group_44.qasm  (basis YZZYYYZZYY):
    +0.00233911  YZZYIIIIYY
    +0.00233911  IIIYYYZZYI
    +0.00660912  YZZYIYZZYI

measure_group_45.qasm  (basis XZZXXYZZYY):
    +0.00233911  XZZXIIIIYY
    +0.00233911  IIIXXYZZYI
    +0.00660912  XZZXIYZZYI

measure_group_46.qasm  (basis YZZYYXZZXX):
    +0.00233911  YZZYIIIIXX
    +0.00233911  IIIYYXZZXI
    +0.00660912  YZZYIXZZXI

measure_group_47.qasm  (basis XZZXXXZZXX):
    +0.00233911  XZZXIIIIXX
    +0.00233911  IIIXXXZZXI
    +0.00660912  XZZXIXZZXI

measure_group_48.qasm  (basis YZZZYZIIZZ):
    -0.03176436  YZZZYIIIIZ
    -0.03363380  YZZZYZIIII
    +0.05268574  IIIIIIIIZZ
    +0.05375800  IIIIIZIIZI

measure_group_49.qasm  (basis XZZZXZIIIZ):
    -0.03176436  XZZZXIIIIZ
    -0.03363380  XZZZXZIIII

measure_group_50.qasm  (basis ZIIZZYZZZY):
    -0.03176436  IIIIZYZZZY
    -0.03363380  ZIIIIYZZZY
    +0.05268574  IIIZZIIIII
    +0.05375800  ZIIZIIIIII

measure_group_51.qasm  (basis ZIIIZXZZZX):
    -0.03176436  IIIIZXZZZX
    -0.03363380  ZIIIIXZZZX

measure_group_52.qasm  (basis YZZYZYZZYZ):
    +0.01283507  YZZYIIIIIZ
    +0.01283507  IIIIZYZZYI
    +0.00420011  IIIIIYZZYZ
    +0.00420011  YZZYZIIIII

measure_group_53.qasm  (basis XZZXZXZZXZ):
    +0.01283507  XZZXIIIIIZ
    +0.01283507  IIIIZXZZXI
    +0.00420011  IIIIIXZZXZ
    +0.00420011  XZZXZIIIII

measure_group_54.qasm  (basis ZIIIZYZZYY):
    +0.01101294  ZIIIIYZZYI
    +0.01212332  IIIIZIIIYY

measure_group_55.qasm  (basis ZIIIIXZZXI):
    +0.01101294  ZIIIIXZZXI

measure_group_56.qasm  (basis YZZYIZIIII):
    +0.01101294  YZZYIZIIII

measure_group_57.qasm  (basis XZZXIZIIII):
    +0.01101294  XZZXIZIIII

