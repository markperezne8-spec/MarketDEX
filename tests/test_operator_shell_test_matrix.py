from pathlib import Path


def test_operator_shell_test_matrix_covers_first_slice_boundaries():
    matrix = Path('docs/operator_shell_test_matrix.md').read_text(encoding='utf-8')

    for boundary in ('Mission Control separation', 'Snapshot authority', 'Operator navigation', 'Visual acceptance', 'Scope preservation'):
        assert boundary in matrix
