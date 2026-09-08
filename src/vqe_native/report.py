"""Write the per-molecule deliverable: native-gate QASM3 circuits + their numeric reference data.

Usage instructions live in docs/EXPERIMENTALIST_GUIDE.md (one copy, molecule-agnostic).
`reference.md` here is deliberately just the numbers that guide needs per molecule: energies to
check against, the energy offset constant, and each measurement group's Pauli terms/coefficients.
"""

from __future__ import annotations

from pathlib import Path

from vqe_native.hamiltonian import QubitHamiltonian
from vqe_native.measurement import MeasurementGroup
from vqe_native.qasm_export import export_qasm3
from vqe_native.vqe_runner import VQERunResult


def _format_pauli_terms(group: MeasurementGroup) -> list[str]:
    lines = []
    for pauli, coeff in zip(group.paulis.paulis, group.paulis.coeffs):
        lines.append(f"    {coeff.real:+.8f}  {pauli.to_label()}")
    return lines


def write_deliverables(
    *,
    molecule_name: str,
    native_ansatz_circuit,
    hamiltonian: QubitHamiltonian,
    vqe_result: VQERunResult,
    measurement_groups: list[MeasurementGroup],
    classical_reference_energy: float,
    classical_reference_description: str,
    output_dir: Path,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    export_qasm3(native_ansatz_circuit, output_dir / "ansatz.qasm")
    for group in measurement_groups:
        export_qasm3(group.circuit, output_dir / f"measure_group_{group.index}.qasm")

    lines = [
        f"# {molecule_name.upper()} - reference data",
        "",
        "Usage instructions: ../../docs/EXPERIMENTALIST_GUIDE.md",
        "",
        "## Energies (Hartree)",
        "",
        f"- VQE (this circuit):        {vqe_result.vqe_total_energy:.8f}",
        f"- Exact diagonalization (qiskit-nature qubit Hamiltonian): {vqe_result.exact_total_energy:.8f}",
        f"- Independent classical reference ({classical_reference_description}): {classical_reference_energy:.8f}",
        "",
        "## Formula",
        "",
        "    E_total = energy_offset + sum_over_all_terms( coefficient * <term> )",
        "",
        f"    energy_offset = {hamiltonian.energy_offset:.8f} Ha",
        "",
        "## Pauli terms per measurement group",
        "",
        "(qubit ordering: rightmost character = qubit 0; a group's basis label is its "
        "per-qubit measurement basis in that same ordering)",
        "",
    ]
    for group in measurement_groups:
        bases = "".join(group.qubit_bases[::-1])
        lines.append(f"measure_group_{group.index}.qasm  (basis {bases}):")
        lines.extend(_format_pauli_terms(group))
        lines.append("")

    (output_dir / "reference.md").write_text("\n".join(lines) + "\n")
