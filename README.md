# Pre-optimized VQE circuits for H₂ and LiH (neutral-atom native gates)

This repository provides **ready-to-run quantum circuits** that prepare the ground states of H₂ and LiH, compiled to a neutral-atom native gate set (`rz`, `sx`, `cz`).

The variational optimization (VQE, Variational Quantum Eigensolver) has **already been carried out on a classical simulator**. The circuits contain fixed, converged parameters. Experimentalists only need to run the circuits on the device, collect measurement counts, and combine them into a molecular energy, following the [Experimentalist Guide](docs/EXPERIMENTALIST_GUIDE.md). **No optimization loop runs on the quantum hardware.**

## Who is this for?

- **Experimentalists:** go to `outputs/<molecule>/` and the [Experimentalist Guide](docs/EXPERIMENTALIST_GUIDE.md). You don't need to install or run any code.
- **Developers / reviewers:** the Python pipeline in `src/vqe_native/` shows how the circuits were generated and lets you regenerate them.

## What is delivered

| Molecule | Basis | Qubits | Measurement circuits | Reference energy (Ha) |
|----------|-------|--------|----------------------|-----------------------|
| H₂ | STO-3G | 4 | 5 | −1.13730604 |
| LiH | STO-3G, Li 1s core frozen | 10 | 58 | −7.88217599 |

For each molecule, `outputs/<molecule>/` contains:

- `ansatz.qasm`: the converged state-preparation circuit, without measurements.
- `measure_group_N.qasm`: the ansatz followed by a basis-rotation layer and a measurement of all qubits. These are the files to execute, one per group.
- `reference.md`: which Pauli terms and coefficients each measurement file covers, the energy offset, the formula to combine the measured expectation values into the total energy, and the reference energies to compare against.

All circuits are OpenQASM 3 and use only the native operations: `sx` (fixed SQRT(X) pulse), `rz` (free virtual phase "PHI") and `cz` (entangling gate).

## How the circuits were generated

We ran VQE classically (exact statevector estimator, no shot or hardware noise, SLSQP optimizer) until convergence, then compiled the converged circuit to the native gates.

- **H₂**, STO-3G, no active-space reduction needed: **4 qubits**.
- **LiH**, STO-3G, Li 1s core frozen (`FreezeCoreTransformer`): **10 qubits**.
- Ansatz: UCCSD (Hartree-Fock reference + single/double excitations), via qiskit-nature.
- Every energy was cross-checked against two independent classical references: exact diagonalization of the same qubit Hamiltonian (`NumPyMinimumEigensolver`), and a direct PySCF calculation built independently of qiskit-nature (FCI for H₂, CASCI over the matching frozen-core active space for LiH). All three agree to ~1e-6 Ha or better.
- The converged circuit was compiled to `{rz, sx, cz}`, assuming all-to-all connectivity (reconfigurable neutral-atom array).
- Hamiltonian terms were grouped into qubit-wise commuting sets, so each group needs only a local basis-rotation layer (no extra entangling gates) before measurement.

## Repository layout

- `outputs/h2/`, `outputs/lih/`: the deliverable circuits and reference data (see above).
- `docs/EXPERIMENTALIST_GUIDE.md`: instructions for the experimental team: what each file in `outputs/` is and how to run the measurement circuits.
- `src/vqe_native/`: the generation pipeline (molecule → qubit Hamiltonian → UCCSD → VQE → native-gate compilation → measurement grouping → QASM 3 export).
- `scripts/run_h2.py`, `scripts/run_lih.py`: run the full pipeline end-to-end for each molecule.
- `tests/`: pytest suite verifying qubit counts, VQE-vs-classical-reference agreement, native-gate-only compilation, and a closed-loop check that the exported measurement circuits reconstruct the correct energy.

## Regenerating the circuits (optional)

The circuits in `outputs/` are already generated; you only need this to reproduce or modify them.

```bash
uv sync
uv run pytest                 # ~3-4 min, mostly the LiH (10-qubit) VQE run
uv run python scripts/run_h2.py
uv run python scripts/run_lih.py
```

## Scope and next steps

Not included here (possible next steps):

- Running the VQE optimization loop against real hardware (hybrid HPC/QC loop).
- Mapping the circuits onto a specific physical qubit layout (currently all-to-all connectivity is assumed), and further hardware–algorithm co-design optimization for the target neutral-atom architecture.
- Integration with the MQSS Benchmarking Framework for full-system HPC/QC benchmarking.

Developed as part of hybrid HPC/QC benchmarking work for neutral-atom platforms.

## License

Licensed under the [Apache License 2.0](LICENSE), consistent with the Munich Quantum Software Stack.
