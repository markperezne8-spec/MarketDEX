from pathlib import Path


def test_rc_delivery_test_matrix_covers_pass_and_block_paths():
    matrix = Path('docs/RC_DELIVERY_TEST_MATRIX.md').read_text(encoding='utf-8')

    assert 'PASS: manual workflow contract exists' in matrix
    assert 'PASS: executable must be non-empty before staging' in matrix
    assert 'PASS: operator package contains executable and README guidance' in matrix
    assert 'BLOCK: generated executable committed to source' in matrix
    assert 'BLOCK: installer or automatic-update scope added implicitly' in matrix
