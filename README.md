# Pre-optimized VQE circuits for H₂ and LiH (neutral-atom native gates)

This repository provides **ready-to-run quantum circuits** that prepare the ground states of H₂ and LiH, compiled to the neutral-atom hardware format: parallel CZ layers, and single-qubit gates as [local Z, global √X, local Z, global √X, local Z].

The variational optimization (VQE, Variational Quantum Eigensolver) has **already been carried out on a classical simulator**. The circuits contain fixed, converged parameters. Experimentalists only need to run the circuits on the device, collect measurement counts, and combine them into a molecular energy, following the [Experimentalist Guide](docs/EXPERIMENTALIST_GUIDE.md). **No optimization loop runs on the quantum hardware.**

## Who is this for?

- **Experimentalists:** go to `outputs/<molecule>/` and the [Experimentalist Guide](docs/EXPERIMENTALIST_GUIDE.md). You don't need to install or run any code.
- **Developers / reviewers:** the Python pipeline in `src/vqe_native/` shows how the circuits were generated and lets you regenerate them.

## What is delivered

| Molecule | Basis | Qubits | Measurement circuits | CZ gates / CZ layers per circuit | Global √X pulses per circuit | Reference energy (Ha) |
|----------|-------|--------|----------------------|----------------------------------|------------------------------|-----------------------|
| H₂ | STO-3G | 4 | 5 | 3 / 2 | 6 | −1.13730604 |
| LiH | STO-3G, Li 1s core frozen | 10 | 58 | 24 / 12 | 24–26 | −7.88217599 |

For each molecule, `outputs/<molecule>/` contains:

- `ansatz.qasm`: the converged state-preparation circuit, without measurements.
- `measure_group_N.qasm`: the ansatz followed by a basis-rotation layer and a measurement of all qubits. These are the files to execute, one per group.
- `reference.md`: which Pauli terms and coefficients each measurement file covers, the energy offset, the formula to combine the measured expectation values into the total energy, the reference energies to compare against, and the hardware cost of every circuit.

All circuits are OpenQASM 3 and use only three operations:

- `cz`: entangling gate. CZs on disjoint pairs are grouped into one **CZ layer** and run in parallel.
- `gsx`: one **global** √X pulse acting on all qubits at once (defined at the top of each file as `sx` on every qubit).
- `rz`: local virtual Z rotation, with a different phase per qubit.

Barriers separate the circuit into *moments*. Each moment is either a CZ layer or a single-qubit block `rz… gsx rz… gsx rz…` (local Z₁, global √X, local Z₂, global √X, local Z₃). The `ansatz.qasm` files can also end with a layer of only `rz`. `tests/test_hardware_format.py` checks every committed file against these rules.

## How the circuits were generated

We ran VQE classically (exact statevector estimator, no shot or hardware noise, SLSQP optimizer) until convergence, then compiled the converged circuit to the hardware format.

- **H₂**, STO-3G, no active-space reduction needed: **4 qubits**.
- **LiH**, STO-3G, Li 1s core frozen (`FreezeCoreTransformer`): **10 qubits**.
- Ansatz: a compact *pair ansatz*, exact for two electrons in a singlet (both problems reduce to this). It spreads the α electron over the orbitals, copies it to the β register with one parallel CZ layer, and applies the same orbital rotation (Givens rotations) to both registers. It starts from Hartree-Fock and can represent the exact ground state. Parameters that converge to ~0 (symmetry-forbidden or redundant rotations) are removed, and VQE is re-run on the smaller circuit. See `src/vqe_native/ansatz.py`.
- Compared with the first version (UCCSD compiled gate by gate): H₂ went from 42 CZ to 3 CZ (2 CZ layers), and LiH from 530 CZ (507 layers) to 24 CZ (12 layers).
- Every energy was cross-checked against two independent classical references: exact diagonalization of the same qubit Hamiltonian (`NumPyMinimumEigensolver`), and a direct PySCF calculation built independently of qiskit-nature (FCI for H₂, CASCI over the matching frozen-core active space for LiH). All three agree to ~1e-6 Ha or better.
- The converged circuit was compiled to the hardware format (`src/vqe_native/native_gates.py`) assuming all-to-all connectivity (reconfigurable neutral-atom array). CZs are packed into as few parallel layers as possible, Z-only gates are moved through CZs (they commute), and the number of single-qubit blocks, each costing 2 global pulses, is kept to the minimum for that CZ layering.
- Hamiltonian terms were grouped into qubit-wise commuting sets, so each group needs only a local basis-rotation layer before measurement. That layer is merged into the last single-qubit block, so it adds no CZs and no extra pulses.

## Repository layout

- `outputs/h2/`, `outputs/lih/`: the deliverable circuits and reference data (see above).
- `docs/EXPERIMENTALIST_GUIDE.md`: instructions for the experimental team: what each file in `outputs/` is and how to run the measurement circuits.
- `src/vqe_native/`: the generation pipeline (molecule → qubit Hamiltonian → pair ansatz → VQE → hardware-format compilation → measurement grouping → QASM 3 export).
- `scripts/run_h2.py`, `scripts/run_lih.py`: run the full pipeline end-to-end for each molecule.
- `tests/`: pytest suite verifying qubit counts, VQE-vs-classical-reference agreement, the hardware format (on the pipeline circuits, on the committed QASM files and on random circuits), and a closed-loop check that the exported measurement circuits reconstruct the correct energy.

## Regenerating the circuits (optional)

The circuits in `outputs/` are already generated; you only need this to reproduce or modify them.

```bash
uv sync
uv run pytest                 # ~30 s
uv run python scripts/run_h2.py
uv run python scripts/run_lih.py
```

## Scope and next steps

Not included here (possible next steps):

- Running the VQE optimization loop against real hardware (hybrid HPC/QC loop).
- Mapping the circuits onto a specific physical qubit layout and atom-rearrangement schedule (currently all-to-all connectivity is assumed, with any choice of CZ pairs in each layer).
- Integration with the MQSS Benchmarking Framework for full-system HPC/QC benchmarking.

Developed as part of hybrid HPC/QC benchmarking work for neutral-atom platforms.

## License

Licensed under the [Apache License 2.0](LICENSE), consistent with the Munich Quantum Software Stack.
