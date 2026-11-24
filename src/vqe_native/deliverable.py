"""Generate the deliverable for one molecule and one or more ansätze (used by scripts/run_*.py).

Output layout: ``outputs/<ansatz>/<molecule>/`` with ``ansatz.qasm``, ``measure_group_N.qasm`` and
``reference.md``. The circuits first sent to the experiment are kept unchanged in
``outputs/v1_sent_to_experiment/``; this module never writes there.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Callable

from vqe_native.ansatz import ANSATZE
from vqe_native.measurement import build_measurement_groups
from vqe_native.molecules import MoleculeSpec
from vqe_native.native_gates import validate_hardware_format
from vqe_native.pipeline import run_pipeline
from vqe_native.report import write_deliverables

OUTPUTS_ROOT = Path(__file__).resolve().parents[2] / "outputs"


def generate(
    spec: MoleculeSpec,
    ansatz_name: str,
    classical_energy_fn: Callable[[], float],
    classical_description: str,
    outputs_root: Path = OUTPUTS_ROOT,
) -> None:
    result = run_pipeline(spec, ansatz_name)
    groups = build_measurement_groups(result.vqe_result.bound_circuit, result.hamiltonian.operator)
    # The PySCF reference runs after VQE, as in the first delivery. Floating-point details of the
    # linear-algebra library can depend on what ran earlier in the same process; the optimizer
    # can amplify that into ~1e-7 differences in the exported angles (energies and costs are
    # unaffected). Running the same command always reproduces the same files.
    classical_energy = classical_energy_fn()
    output_dir = outputs_root / ansatz_name / spec.name
    write_deliverables(
        molecule_name=spec.name,
        ansatz_name=ansatz_name,
        ansatz_description=result.ansatz.description,
        native_ansatz_circuit=result.native_ansatz_circuit,
        hamiltonian=result.hamiltonian,
        vqe_result=result.vqe_result,
        measurement_groups=groups,
        classical_reference_energy=classical_energy,
        classical_reference_description=classical_description,
        output_dir=output_dir,
    )
    costs = [validate_hardware_format(g.circuit) for g in groups]
    name = spec.name.upper()
    print(f"[{ansatz_name}] {name} VQE energy {result.vqe_result.vqe_total_energy:.8f} Ha "
          f"(exact {result.vqe_result.exact_total_energy:.8f}, {classical_description} {classical_energy:.8f})")
    print(f"[{ansatz_name}] {name} measurement circuits: <= {max(c.cz_gates for c in costs)} CZ, "
          f"<= {max(c.cz_layers for c in costs)} CZ layers, "
          f"<= {max(c.global_sx_pulses for c in costs)} global sqrt(X) pulses")
    print(f"[{ansatz_name}] wrote {1 + len(groups)} circuits + reference.md to {output_dir}")


def main(spec: MoleculeSpec, classical_energy_fn: Callable[[], float], classical_description: str) -> None:
    # Python orders sets and dicts differently in every process (random hash seed). Qiskit's term
    # grouping and transpiler iterate over sets, so without a fixed seed the exported files
    # differ between runs (equivalent circuits, different angles and term order). Restart this
    # same command once with a fixed seed, so every run writes byte-identical files.
    if os.environ.get("PYTHONHASHSEED") != "0":
        os.environ["PYTHONHASHSEED"] = "0"
        os.execv(sys.executable, [sys.executable, *sys.argv])

    parser = argparse.ArgumentParser(description=f"Generate the {spec.name.upper()} deliverable.")
    parser.add_argument(
        "--ansatz",
        choices=[*ANSATZE, "all"],
        default="all",
        help="which ansatz to generate (default: all three; 'uccsd-pennylane' needs: uv sync --extra pennylane)",
    )
    args = parser.parse_args()
    names = list(ANSATZE) if args.ansatz == "all" else [args.ansatz]
    for name in names:
        generate(spec, name, classical_energy_fn, classical_description)
