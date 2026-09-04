# HPC/QC VQE Benchmark

This repository contains work toward a hybrid HPC/QC application for neutral-atom platforms, focusing on full-system HPC/QC benchmarking.

The selected application is the **Variational Quantum Eigensolver (VQE)** for quantum chemistry. VQE provides a representative hybrid workflow in which classical HPC resources are used together with a quantum processor to estimate molecular ground-state energies.

Initial molecular systems considered are:

* **H₂**, requiring 4 qubits in the STO-3G basis
* **LiH**, requiring 12 qubits in the STO-3G basis

The quantum circuits will be compiled and adapted to the native gate set of the neutral-atom platform. The native operations are based on **CZ gates and local Pauli rotations**, with local rotations typically decomposed using `SQRT(X)`, `PHI`, and `SQRT(X)` operations.

The implementation will be developed with hardware–algorithm co-design in mind, allowing the initially compiled VQE circuits to be further optimized for the target neutral-atom architecture.

This work is intended to integrate with the **MQSS Benchmarking Framework** for full-system HPC/QC benchmarking.


