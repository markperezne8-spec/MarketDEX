from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERIFICATION = ROOT / "docs" / "RELEASE_CANDIDATE_VERIFICATION.md"


def test_windows_verification_covers_launch_and_runtime_preservation():
    text = VERIFICATION.read_text(encoding="utf-8")

    assert "MarketDEX.exe" in text
    assert "Mission Control" in text
    assert "existing operator inventory remains present" in text
    assert "Close and relaunch" in text
    assert "runtime inventory is still preserved" in text


def test_windows_verification_covers_inventory_pricing_listing_handoff():
    text = VERIFICATION.read_text(encoding="utf-8")

    assert "Pricing handoff is selection-aware" in text
    assert "Continue from Pricing into Listing" in text
    assert "selected item remains the active operator context" in text


def test_windows_verification_keeps_marketplace_and_sale_authority_local():
    text = VERIFICATION.read_text(encoding="utf-8")

    assert "saved listing plans remain separate from sale completion" in text
    assert "no marketplace action is performed remotely" in text
