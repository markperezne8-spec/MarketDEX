from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_cap006_status_documents_match_merged_provisional_slice():
    matrix = (ROOT / 'docs' / 'engineering' / 'Capability_Matrix.md').read_text(encoding='utf-8')
    traceability = (ROOT / 'docs' / 'Architecture' / 'Requirements_Traceability_Matrix.md').read_text(encoding='utf-8')
    intake = (ROOT / 'docs' / 'Architecture' / 'CAP-006_COLLECTION_BUSINESS_RESPONSIBILITY_INTAKE.md').read_text(encoding='utf-8')
    reconciliation = (ROOT / 'docs' / 'engineering' / 'Repository_Reconciliation.md').read_text(encoding='utf-8')

    assert '| CAP-006 | Collection |' in matrix
    assert '| Partial |' in matrix
    assert 'CollectionPositionService' in traceability
    assert '| In Progress |' in traceability
    assert 'PROVISIONAL BUILD SLICE COMPLETE' in intake
    assert 'CAP-006 authority expansion' in reconciliation
