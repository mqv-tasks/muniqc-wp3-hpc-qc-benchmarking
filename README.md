# HPC/QC VQE Benchmark

This repository contains work toward a hybrid HPC/QC application for neutral-atom platforms, focusing on full-system HPC/QC benchmarking.

The selected application is the **Variational Quantum Eigensolver (VQE)** for quantum chemistry. VQE provides a representative hybrid workflow in which classical HPC resources are used together with a quantum processor to estimate molecular ground-state energies.

Initial molecular systems considered are:

* **H₂**, requiring 4 qubits in the STO-3G basis
* **LiH**, requiring 10 qubits in the STO-3G basis (Li 1s core frozen)

The quantum circuits will be compiled and adapted to the native gate set of the neutral-atom platform. The native operations are based on **CZ gates and local Pauli rotations**, with local rotations typically decomposed using `SQRT(X)`, `PHI`, and `SQRT(X)` operations.

The implementation will be developed with hardware–algorithm co-design in mind, allowing the initially compiled VQE circuits to be further optimized for the target neutral-atom architecture.

This work is intended to integrate with the **MQSS Benchmarking Framework** for full-system HPC/QC benchmarking.

## What this repo produces

For each molecule, a classical HPC step (this code) runs VQE to convergence and hands the
experimentalists a **fixed, already-optimized circuit** — they measure it, they do not run any
VQE optimization loop themselves. (Iterating VQE against real hardware is an explicit
second-phase item, out of scope here.)

- **H2**, STO-3G, no active-space reduction needed: **4 qubits**.
- **LiH**, STO-3G, Li 1s core frozen (`FreezeCoreTransformer`): **10 qubits**.
- Ansatz: UCCSD (Hartree-Fock reference + single/double excitations), via qiskit-nature.
- VQE runs on an exact statevector estimator (no shot/hardware noise) with SLSQP.
- Every energy is cross-checked against two independent classical references: exact
  diagonalization of the same qubit Hamiltonian (`NumPyMinimumEigensolver`), and a direct PySCF
  calculation built independently of qiskit-nature (FCI for H2, CASCI over the matching
  frozen-core active space for LiH). All three agree to ~1e-6 Ha or better.
- The converged circuit is compiled to `{rz, sx, cz}` — the neutral-atom native set (`sx` =
  fixed SQRT(X) pulse, `rz` = free virtual phase "PHI", `cz` = entangling gate) — assuming
  all-to-all connectivity (reconfigurable neutral-atom array). Mapping onto a specific hardware
  layout is a follow-up hardware/algorithm co-design step.
- Hamiltonian terms are grouped into qubit-wise commuting sets so each group needs only a local
  basis-rotation layer (no extra entangling gates) before measurement.

## Layout

- `src/vqe_native/`: the pipeline (molecule → qubit Hamiltonian → UCCSD → VQE → native-gate
  compilation → measurement grouping → QASM3 export).
- `scripts/run_h2.py`, `scripts/run_lih.py`: run the full pipeline end-to-end for each molecule.
- `outputs/h2/`, `outputs/lih/`: the deliverable — `ansatz.qasm` (the converged circuit, no
  measurements) plus one `measure_group_*.qasm` per qubit-wise commuting Pauli group, all in
  OpenQASM 3 using only `rz`/`sx`/`cz`. Each folder's `reference.md` documents which Pauli terms and
  coefficients each measurement file covers and the formula to combine measured counts into the
  total energy.
- `docs/EXPERIMENTALIST_GUIDE.md`: step-by-step instructions for the experimental team — what
  each file in `outputs/` is, how to run the measurement circuits, and how to turn the measured
  counts into a molecular energy, with a worked numeric example.
- `tests/`: pytest suite verifying qubit counts, VQE-vs-classical-reference agreement,
  native-gate-only compilation, and a closed-loop check that the exported measurement circuits
  reconstruct the correct energy.

## Running it

```bash
uv sync
uv run pytest                 # ~3-4 min, mostly the LiH (10-qubit) VQE run
uv run python scripts/run_h2.py
uv run python scripts/run_lih.py
```


## License

Licensed under the [Apache License 2.0](LICENSE), consistent with the Munich Quantum Software Stack.
