"""Generate the H2 deliverable into outputs/<ansatz>/h2/.

    uv run python scripts/run_h2.py                         # all three ansätze
    uv run python scripts/run_h2.py --ansatz pair           # just one
"""

from vqe_native.classical_reference import pyscf_fci_total_energy
from vqe_native.deliverable import main
from vqe_native.molecules import H2

if __name__ == "__main__":
    main(H2, lambda: pyscf_fci_total_energy(H2), "PySCF FCI")
