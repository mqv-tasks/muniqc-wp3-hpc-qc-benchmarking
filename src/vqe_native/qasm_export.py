"""Export circuits to OpenQASM 3."""

from __future__ import annotations

from pathlib import Path

from qiskit import qasm3
from qiskit.circuit import QuantumCircuit


def export_qasm3(circuit: QuantumCircuit, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as stream:
        qasm3.dump(circuit, stream)
