# Running the VQE circuits and extracting the molecular energy

This guide explains what is in `outputs/` and how to turn a run of those circuits on your
hardware into a molecular ground-state energy. It assumes no familiarity with Qiskit or with how
the circuits were generated — everything you need is the QASM3 files themselves plus this
document.

## What you are being handed

For each molecule (H2, LiH), we ran VQE on a classical simulator to find the circuit that
prepares the molecule's ground state, then compiled that circuit to your native gate set. **The
optimization is already done** — these are fixed circuits with numeric parameters baked in. You
do not need to run any classical optimization loop or feedback iteration; you just execute the
circuits below and post-process the measurement outcomes as described here. (A future phase of
this project may involve running the optimization loop itself against your hardware — that is
not what this delivers.)

Every circuit is OpenQASM 3, using only your three native operations:

- `sx` — the fixed SQRT(X) pulse
- `rz(angle)` — the free virtual Z rotation ("PHI")
- `cz` — the entangling gate

No other gates appear anywhere in these files. Qubit connectivity is assumed to be all-to-all
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
- **`measure_group_N.qasm`** is `ansatz.qasm` followed by (a) a short layer of single-qubit basis
  rotations and (b) a measurement of every qubit into a classical register named `meas`. This is
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

Concretely: for a given group, each qubit is rotated (or left alone) so that afterwards a plain
Z-basis measurement of that qubit gives the correct outcome for every term in the group. That is
why the basis-rotation layer differs between `measure_group_*.qasm` files but the trailing
measurement instructions always just measure in the computational (Z) basis.

## Step-by-step protocol

For each molecule:

1. Open that molecule's `outputs/<molecule>/reference.md` and note:
   - `energy_offset` (a constant, in Hartree, that gets added at the very end — it comes from
     nuclear repulsion and, for LiH, the frozen-core energy; it needs no measurement).
   - The list of Pauli terms + coefficients for each `measure_group_N.qasm` file.

2. For each `measure_group_N.qasm` file:
   - Run the circuit for a number of shots (a few thousand is a reasonable starting point; more
     shots reduce statistical noise on the resulting expectation values).
   - For every shot, record the `meas[i]` outcome (0 or 1) for every qubit `i`.

3. For each Pauli term listed for that group (e.g. `+0.12091263  IIZZ`, using the file's own
   qubit-ordering convention — see "Reading the Pauli labels" below):
   - Identify which qubits that term is non-identity on (skip qubits marked `I`).
   - For every shot, compute the **parity**: multiply together `(-1)^meas[i]` for each qubit `i`
     the term acts on (i.e. +1 if an even number of those qubits measured 1, -1 if odd).
   - Average that parity over all shots. This average is your measured expectation value
     `<term>` for that Pauli term.
   - A term that is `IIII` (identity on every qubit) needs no measurement at all: its expectation
     value is always exactly `+1` by definition — just use its coefficient directly.

4. Once you have `<term>` for every term in every group, compute:

   ```
   E_total = energy_offset + sum over all terms of ( coefficient * <term> )
   ```

   `E_total` is your hardware-measured estimate of the molecule's total ground-state energy, in
   Hartree.

5. Compare `E_total` against the reference energies in that molecule's `reference.md` (VQE, exact
   diagonalization, and an independent PySCF calculation — all three agree with each other to
   about 1e-6 to 1e-7 Hartree on the classical simulator). Your hardware result will differ from
   these by whatever noise/imperfection your system has; that gap is itself a useful benchmark
   number for this milestone.

## Reading the Pauli labels

Each molecule's `reference.md` writes Pauli terms as strings like `IIZZ` or `XXYY`, following the
usual convention where the **rightmost character is qubit 0** and the leftmost is the
highest-indexed qubit. So for a 4-qubit term `IIZZ`, reading right to left: qubit 0 = `Z`, qubit 1
= `Z`, qubit 2 = `I`, qubit 3 = `I` — i.e. this term acts on qubits 0 and 1 only. This labeling
convention only affects how you read the term strings in the `reference.md` tables; the QASM
files themselves are indexed directly (`meas[i]` = qubit `i`), so no reversal is needed when
processing your actual measurement data.

## Worked example (H2, `measure_group_4.qasm`)

H2's `measure_group_4.qasm` basis-rotates nothing (it is a pure Z-basis group) and covers, among
others, the term `+0.12091263  IIZZ` (qubits 0 and 1) and `+0.17218393  IIIZ` (qubit 0 only).
Suppose across 1000 shots you observe `meas[0]=1` and `meas[1]=0` in 400 of them, and other
combinations in the rest, such that the averaged parities come out to `<IIZZ> = -0.15` and
`<IIIZ> = 0.30` (illustrative numbers). Their contributions to the total energy are:

```
0.12091263 * (-0.15) = -0.01813690
0.17218393 * ( 0.30) =  0.05165518
```

Every other term in every other group is treated the same way, all summed together, then
`energy_offset` (`+0.71996899` Ha for H2) is added once at the end to get `E_total`.

## Circuit size, per molecule

| Molecule | Qubits | Measurement groups | `ansatz.qasm` CZ count |
|---|---|---|---|
| H2  | 4  | 5  | 42  |
| LiH | 10 | 58 | 530 |

H2's circuit is shallow, as expected. LiH's is not (530 two-qubit gates) — that is a genuine
consequence of the UCCSD ansatz at this active-space size, and is worth discussing as a co-design
topic (e.g. reducing the active space further, or a hardware-efficient ansatz) if LiH's raw
circuit turns out to be impractical on current hardware.
