from pathlib import Path


def test_ci_note_names_primary_workspace_gate_strategy():
    text = Path('docs/listing_workspace_ci_note.md').read_text(encoding='utf-8')
    assert 'connected pricing decision contracts together' in text
