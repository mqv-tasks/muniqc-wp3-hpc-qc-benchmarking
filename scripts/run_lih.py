"""Run the full pipeline for LiH (frozen-core, 10 qubits) and export the native-gate
deliverable to outputs/lih/."""

from pathlib import Path

from vqe_native.classical_reference import pyscf_casci_total_energy
from vqe_native.measurement import build_measurement_groups
from vqe_native.molecules import LIH
from vqe_native.pipeline import run_pipeline
from vqe_native.report import write_deliverables

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "outputs" / "lih"

# Must match the FreezeCoreTransformer reduction: Li 1s frozen -> 2 active
# electrons in 5 active spatial orbitals.
ACTIVE_ORBITALS = 5
ACTIVE_ELECTRONS = 2


def main() -> None:
    result = run_pipeline(LIH)
    measurement_groups = build_measurement_groups(
        result.vqe_result.bound_circuit, result.hamiltonian.operator
    )
    classical_energy = pyscf_casci_total_energy(LIH, ACTIVE_ORBITALS, ACTIVE_ELECTRONS)

    write_deliverables(
        molecule_name="lih",
        native_ansatz_circuit=result.native_ansatz_circuit,
        hamiltonian=result.hamiltonian,
        vqe_result=result.vqe_result,
        measurement_groups=measurement_groups,
        classical_reference_energy=classical_energy,
        classical_reference_description="PySCF CASCI (2e, 5o), matching the frozen-core active space",
        output_dir=OUTPUT_DIR,
    )

    print(f"LiH VQE total energy:   {result.vqe_result.vqe_total_energy:.8f} Ha")
    print(f"LiH exact total energy: {result.vqe_result.exact_total_energy:.8f} Ha")
    print(f"LiH PySCF CASCI energy: {classical_energy:.8f} Ha")
    print(f"Wrote {1 + len(measurement_groups)} circuits + reference.md to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
