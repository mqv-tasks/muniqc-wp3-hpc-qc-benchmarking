"""Print a comparison table of all generated deliverables.

    uv run python scripts/summarize_outputs.py

For every outputs/<ansatz>/<molecule>/ folder it reads reference.md (written by the pipeline):
the VQE energy and the per-circuit hardware cost table, and reports the worst case (max) over
the measurement circuits. (The committed QASM files themselves are re-checked against the
hardware format by tests/test_hardware_format.py.)
"""

from pathlib import Path

from vqe_native.ansatz import ANSATZE

OUTPUTS = Path(__file__).resolve().parent.parent / "outputs"


def read_reference(path: Path):
    energy, costs = "?", []
    for line in path.read_text().splitlines():
        if line.startswith("- VQE (this circuit):"):
            energy = line.split(":")[1].strip()
        if line.startswith("| measure_group_"):
            # | file | CZ gates | CZ layers | single-qubit blocks | global sqrt(X) pulses |
            cells = [c.strip() for c in line.strip("|").split("|")]
            costs.append((int(cells[1]), int(cells[2]), int(cells[4])))
    return energy, costs


def main() -> None:
    print("| Molecule | Ansatz | Measurement circuits | CZ gates (max) | CZ layers (max) | Global √X pulses (max) | VQE energy (Ha) |")
    print("|---|---|---|---|---|---|---|")
    for molecule in ("h2", "lih"):
        for ansatz in ANSATZE:
            reference = OUTPUTS / ansatz / molecule / "reference.md"
            if not reference.exists():
                continue
            energy, costs = read_reference(reference)
            cz, layers, pulses = (max(c[k] for c in costs) for k in range(3))
            print(f"| {molecule.upper()} | `{ansatz}` | {len(costs)} | {cz} | {layers} | {pulses} | {energy} |")


if __name__ == "__main__":
    main()
