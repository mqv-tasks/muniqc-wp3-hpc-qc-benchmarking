# H2 - reference data

Usage instructions: ../../docs/EXPERIMENTALIST_GUIDE.md

## Energies (Hartree)

- VQE (this circuit):        -1.13730604
- Exact diagonalization (qiskit-nature qubit Hamiltonian): -1.13730604
- Independent classical reference (PySCF FCI): -1.13730604

## Formula

    E_total = energy_offset + sum_over_all_terms( coefficient * <term> )

    energy_offset = 0.71996899 Ha

## Circuit cost on hardware

Every circuit is a sequence of moments separated by barriers: CZ layers (CZ gates on
disjoint pairs, run in parallel) and single-qubit blocks [Z_1, global sqrt(X), Z_2,
global sqrt(X), Z_3] (`gsx` = one global sqrt(X) pulse on all qubits).

| File | CZ gates | CZ layers | Single-qubit blocks | Global sqrt(X) pulses |
|------|----------|-----------|---------------------|-----------------------|
| ansatz.qasm | 3 | 2 | 3 | 6 |
| measure_group_0.qasm | 3 | 2 | 3 | 6 |
| measure_group_1.qasm | 3 | 2 | 3 | 6 |
| measure_group_2.qasm | 3 | 2 | 3 | 6 |
| measure_group_3.qasm | 3 | 2 | 3 | 6 |
| measure_group_4.qasm | 3 | 2 | 3 | 6 |

## Pauli terms per measurement group

(qubit ordering: rightmost character = qubit 0; a group's basis label is its per-qubit measurement basis in that same ordering)

measure_group_0.qasm  (basis YYYY):
    +0.04523280  YYYY
    -0.81054798  IIII

measure_group_1.qasm  (basis XXYY):
    +0.04523280  XXYY

measure_group_2.qasm  (basis YYXX):
    +0.04523280  YYXX

measure_group_3.qasm  (basis XXXX):
    +0.04523280  XXXX

measure_group_4.qasm  (basis ZZZZ):
    +0.17218393  IIIZ
    -0.22575349  IIZI
    +0.17218393  IZII
    -0.22575349  ZIII
    +0.12091263  IIZZ
    +0.16892754  IZIZ
    +0.16614543  ZIIZ
    +0.16614543  IZZI
    +0.17464343  ZIZI
    +0.12091263  ZZII

