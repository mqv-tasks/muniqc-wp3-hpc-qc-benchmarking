"""Run the full pipeline for H2 and export the hardware-format deliverable to outputs/h2/."""

from pathlib import Path

from vqe_native.classical_reference import pyscf_fci_total_energy
from vqe_native.measurement import build_measurement_groups
from vqe_native.native_gates import validate_hardware_format
from vqe_native.molecules import H2
from vqe_native.pipeline import run_pipeline
from vqe_native.report import write_deliverables

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "outputs" / "h2"


def main() -> None:
    result = run_pipeline(H2)
    measurement_groups = build_measurement_groups(
        result.vqe_result.bound_circuit, result.hamiltonian.operator
    )
    classical_energy = pyscf_fci_total_energy(H2)

    write_deliverables(
        molecule_name="h2",
        native_ansatz_circuit=result.native_ansatz_circuit,
        hamiltonian=result.hamiltonian,
        vqe_result=result.vqe_result,
        measurement_groups=measurement_groups,
        classical_reference_energy=classical_energy,
        classical_reference_description="PySCF FCI",
        output_dir=OUTPUT_DIR,
    )

    print(f"H2 VQE total energy:   {result.vqe_result.vqe_total_energy:.8f} Ha")
    print(f"H2 exact total energy: {result.vqe_result.exact_total_energy:.8f} Ha")
    print(f"H2 PySCF FCI energy:   {classical_energy:.8f} Ha")
    costs = [validate_hardware_format(g.circuit) for g in measurement_groups]
    print(f"Measurement circuits: <= {max(c.cz_gates for c in costs)} CZ, "
          f"<= {max(c.cz_layers for c in costs)} CZ layers, "
          f"<= {max(c.global_sx_pulses for c in costs)} global sqrt(X) pulses")
    print(f"Wrote {1 + len(measurement_groups)} circuits + reference.md to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
