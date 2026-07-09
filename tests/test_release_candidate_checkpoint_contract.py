from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECKPOINT = ROOT / "docs" / "RELEASE_CANDIDATE_CHECKPOINT.md"
CI = ROOT / ".github" / "workflows" / "ci.yml"


def test_release_candidate_checkpoint_names_all_permanent_ci_gates():
    checkpoint = CHECKPOINT.read_text(encoding="utf-8")

    for gate in ("Core Tests", "Inventory", "Pricing", "Listing", "Desktop Build"):
        assert gate in checkpoint


def test_release_candidate_checkpoint_preserves_operator_authority():
    checkpoint = CHECKPOINT.read_text(encoding="utf-8")

    assert "does not poll marketplaces" in checkpoint
    assert "infer sales" in checkpoint
    assert "mutate remote marketplace state" in checkpoint
    assert "operator remains authoritative" in checkpoint


def test_release_candidate_checkpoint_requires_runtime_data_preservation():
    checkpoint = CHECKPOINT.read_text(encoding="utf-8")

    assert "preserve an existing non-empty operator database" in checkpoint
    assert "missing or empty" in checkpoint


def test_permanent_ci_surface_matches_release_candidate_checkpoint():
    workflow = CI.read_text(encoding="utf-8")

    assert workflow.count("runs-on:") == 5
    for job in ("core-tests:", "inventory:", "pricing:", "listing:", "desktop-build:"):
        assert job in workflow
