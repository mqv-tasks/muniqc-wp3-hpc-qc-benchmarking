# Running the VQE circuits and extracting the molecular energy

This guide explains what is in `outputs/` and how to measure the molecular ground-state energy. 

## What you are being handed

For each molecule (H2, LiH), we ran VQE on a classical simulator to find the circuit that
prepares the molecule's ground state, then compiled that circuit to your native gate set. **The
optimization is already done** — these are fixed circuits with numeric parameters baked in. You
do not need to run any classical optimization loop or feedback iteration; you just execute the
`measure_group_*.qasm` circuits in `outputs/<molecule>/` (described below) and post-process the measurement outcomes as described here. (A future phase of
this project may involve running the optimization loop itself against your hardware — that is
not what this delivers.)

Every circuit is OpenQASM 3 and follows the hardware format you specified:

1. **CZ gates in parallel on pairs of qubits.** CZs on disjoint pairs are grouped into one
   *CZ layer*, to be executed simultaneously.
2. **Single-qubit gates as [local Z_1, global sqrt(X), local Z_2, global sqrt(X), local Z_3].**

Only three operations appear in the files:

- `cz q[a], q[b];` — the entangling gate
- `gsx q[0], q[1], ...;` — **one global SQRT(X) pulse on all qubits**. It is defined at the top of
  each file as `sx` on every qubit, so standard QASM tools understand it.
- `rz(angle) q[i];` — the local virtual Z rotation ("PHI"), with a different phase per qubit

`barrier` statements split each file into *moments*, executed in order:

- a **CZ layer**: only `cz` gates, each qubit used at most once;
- a **single-qubit block**: `rz` on some qubits (Z_1), `gsx`, `rz` (Z_2), `gsx`, `rz` (Z_3). A
  missing `rz` for a qubit means a phase of 0. Every block has exactly two global pulses.
  Qubits with nothing to do in a block get phases that make the block the identity on them;
- in `ansatz.qasm` only: a final layer of `rz` gates (no pulse), so the file prepares the exact
  state.

Z rotations immediately before measurement, and Z rotations on the initial |0> state, change
nothing and have been removed. Each `reference.md` lists the CZ count, CZ layers and global pulses
of every file. Qubit connectivity is assumed to be all-to-all
(reasonable for a reconfigurable neutral-atom array); mapping this onto your actual physical
layout is a follow-up co-design step, not something already handled here.

## Directory layout

```
outputs/
  h2/
    reference.md                # auto-generated numeric details for this molecule (see below)
    ansatz.qasm               # the converged state-preparation circuit, no measurement
    measure_group_0.qasm       # ansatz.qasm + a basis rotation + measurement
    measure_group_1.qasm
    ...
  lih/
    reference.md
    ansatz.qasm
    measure_group_0.qasm
    ...
```

- **`ansatz.qasm`** prepares the (approximate) ground state on the qubits. It has no
  measurements. You never run this file by itself to get a result — it exists so you can
  inspect/characterize the state-preparation part of each `measure_group_*.qasm` file in
  isolation if useful (e.g. for calibration or partial tomography).
- **`measure_group_N.qasm`** is the state preparation of `ansatz.qasm` followed by (a) the
  single-qubit basis rotations for that group, merged into the last single-qubit block so they
  cost no extra pulses, and (b) a measurement of every qubit into a classical register named `meas`. This is
  the file you actually execute, once per group, to collect data. `meas[i]` in the file is always
  the measurement outcome of qubit `i` — there is no bit-reversal or reordering to worry about;
  read the register exactly as indexed in the QASM.
- **`reference.md`** in each molecule folder is the numeric companion to this guide: for that
  specific molecule it lists, file by file, exactly which Hamiltonian terms (Pauli strings) and
  coefficients that measurement file covers, the energy offset constant, and the VQE/classical
  reference energies to check your result against. You will need the numbers in that file to do
  the post-processing below — this guide explains the *procedure*, that file gives the *numbers*.

## Why several measurement files per molecule?

The molecular energy is a weighted sum of many Pauli terms (e.g. `ZIII`, `XXYY`, ...). A single
circuit execution followed by a single measurement basis can only give you the expectation value
of terms that are simultaneously measurable in that basis. We grouped the terms into batches that
are all measurable together ("qubit-wise commuting" groups), so each `measure_group_N.qasm` file
gives you, from one set of runs, several terms' worth of information at once. H2 needs 5 such
groups; LiH needs 58 (10 qubits, more terms).



## Reading the Pauli labels

Each molecule's `reference.md` writes Pauli terms as strings like `IIZZ` or `XXYY`, following the
usual convention where the **rightmost character is qubit 0** and the leftmost is the
highest-indexed qubit. So for a 4-qubit term `IIZZ`, reading right to left: qubit 0 = `Z`, qubit 1
= `Z`, qubit 2 = `I`, qubit 3 = `I` — i.e. this term acts on qubits 0 and 1 only. This labeling
convention only affects how you read the term strings in the `reference.md` tables; the QASM
files themselves are indexed directly (`meas[i]` = qubit `i`), so no reversal is needed when
processing your actual measurement data.

