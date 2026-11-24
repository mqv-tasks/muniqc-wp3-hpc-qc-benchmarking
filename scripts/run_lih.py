"""Generate the LiH (frozen core, 10 qubits) deliverable into outputs/<ansatz>/lih/.

    uv run python scripts/run_lih.py                        # all three ansätze
    uv run python scripts/run_lih.py --ansatz pair          # just one
"""

from vqe_native.classical_reference import pyscf_casci_total_energy
from vqe_native.deliverable import main
from vqe_native.molecules import LIH

# Must match the FreezeCoreTransformer reduction: Li 1s frozen -> 2 active electrons in 5 active
# spatial orbitals.
ACTIVE_ORBITALS = 5
ACTIVE_ELECTRONS = 2

if __name__ == "__main__":
    main(
        LIH,
        lambda: pyscf_casci_total_energy(LIH, ACTIVE_ORBITALS, ACTIVE_ELECTRONS),
        "PySCF CASCI (2e, 5o), matching the frozen-core active space",
    )
