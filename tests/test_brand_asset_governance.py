from __future__ import annotations

import hashlib
from pathlib import Path

from branding.asset_manifest import OFFICIAL_MASCOT, REQUIRED_BRAND_ASSETS, VISUAL_NORTH_STAR


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def _git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def test_canonical_brand_assets_exist_are_png_and_match_approved_identity():
    assert VISUAL_NORTH_STAR.relative_path == (
        "MarketDEX_Mission_Control_Visual_North_Star.png"
    )
    assert OFFICIAL_MASCOT.relative_path == "MarketDEX_Official_Mascot.png"

    for asset in REQUIRED_BRAND_ASSETS:
        path = REPOSITORY_ROOT / asset.relative_path
        assert path.is_file(), f"Required MarketDEX brand asset missing: {path}"
        assert path.stat().st_size > len(PNG_SIGNATURE), f"Empty brand asset: {path}"
        assert path.read_bytes().startswith(PNG_SIGNATURE), f"Not a PNG asset: {path}"
        assert _git_blob_sha(path) == asset.git_blob_sha, (
            f"Canonical MarketDEX brand asset identity changed: {asset.relative_path}. "
            "Replacement requires explicit Product Owner approval and checkpoint update."
        )


def test_visual_north_star_and_mascot_are_documented_as_permanent_requirements():
    standard = (
        REPOSITORY_ROOT
        / "docs/governance/Visual_North_Star_and_Mascot_Standard.md"
    ).read_text(encoding="utf-8")
    vision = (REPOSITORY_ROOT / "Vision.md").read_text(encoding="utf-8")
    checkpoint = (
        REPOSITORY_ROOT
        / "docs/checkpoints/EC-007_Visual_North_Star_Mascot_Lock.md"
    ).read_text(encoding="utf-8")

    for required in (
        VISUAL_NORTH_STAR.relative_path,
        OFFICIAL_MASCOT.relative_path,
        VISUAL_NORTH_STAR.git_blob_sha,
        OFFICIAL_MASCOT.git_blob_sha,
        "permanent MarketDEX brand element",
        "No release may silently omit the mascot",
    ):
        assert required in standard

    assert "Mission Control Visual North Star — Design Locked" in vision
    assert "MarketDEX Mascot" in vision
    assert VISUAL_NORTH_STAR.relative_path in checkpoint
    assert OFFICIAL_MASCOT.relative_path in checkpoint
