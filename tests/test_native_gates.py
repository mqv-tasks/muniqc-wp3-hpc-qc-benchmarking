from vqe_native.native_gates import ALLOWED_OPS


def _assert_only_native_ops(circuit):
    used_ops = set(circuit.count_ops())
    assert used_ops <= ALLOWED_OPS, f"non-native ops found: {used_ops - ALLOWED_OPS}"


def test_h2_ansatz_uses_only_native_gates(h2_pipeline):
    _assert_only_native_ops(h2_pipeline.native_ansatz_circuit)


def test_lih_ansatz_uses_only_native_gates(lih_pipeline):
    _assert_only_native_ops(lih_pipeline.native_ansatz_circuit)


def test_h2_measurement_circuits_use_only_native_gates(h2_measurement_groups):
    for group in h2_measurement_groups:
        _assert_only_native_ops(group.circuit)


def test_lih_measurement_circuits_use_only_native_gates(lih_measurement_groups):
    for group in lih_measurement_groups:
        _assert_only_native_ops(group.circuit)
