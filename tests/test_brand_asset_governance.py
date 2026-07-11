from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from branding.asset_manifest import (
    APPROVED_BRAND_ASSETS,
    APPROVED_VISUAL_NORTH_STAR_V1,
    HISTORICAL_VISUAL_NORTH_STAR,
    OFFICIAL_MASCOT,
    REQUIRED_BRAND_ASSETS,
    VISUAL_NORTH_STAR,
    approved_asset_path,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def _git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_current_required_brand_assets_exist_are_png_and_match_identity():
    assert VISUAL_NORTH_STAR is HISTORICAL_VISUAL_NORTH_STAR
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


def test_gamified_visual_north_star_v1_is_active_approved_identity():
    asset = APPROVED_VISUAL_NORTH_STAR_V1

    assert asset in APPROVED_BRAND_ASSETS
    assert asset.relative_path == (
        "assets/brand/visual_north_star/marketdex_visual_north_star_v1.png"
    )
    assert asset.width == 1536
    assert asset.height == 1024
    assert asset.sha256 == (
        "1269e2af119c569cc5d4f76b82a6f92984a04f6f752119d8e1dcf417557909a5"
    )
    assert asset.git_blob_sha == "27d4b34b24984678225ae38c7e77240a02d521b4"

    path = REPOSITORY_ROOT / asset.relative_path
    if path.is_file():
        assert path.read_bytes().startswith(PNG_SIGNATURE)
        assert _sha256(path) == asset.sha256
        assert _git_blob_sha(path) == asset.git_blob_sha
    else:
        with pytest.raises(FileNotFoundError, match="has not been synchronized"):
            approved_asset_path(asset, REPOSITORY_ROOT)


def test_visual_north_star_and_mascot_are_documented_as_permanent_requirements():
    standard = (
        REPOSITORY_ROOT
        / "docs/governance/Visual_North_Star_and_Mascot_Standard.md"
    ).read_text(encoding="utf-8")
    visual = (REPOSITORY_ROOT / "docs/design/VISUAL_NORTH_STAR.md").read_text(
        encoding="utf-8"
    )
    vision = (REPOSITORY_ROOT / "Vision.md").read_text(encoding="utf-8")
    checkpoint = (
        REPOSITORY_ROOT
        / "docs/checkpoints/EC-008_Gamified_Visual_North_Star_Design_System.md"
    ).read_text(encoding="utf-8")

    for required in (
        APPROVED_VISUAL_NORTH_STAR_V1.relative_path,
        HISTORICAL_VISUAL_NORTH_STAR.relative_path,
        OFFICIAL_MASCOT.relative_path,
        APPROVED_VISUAL_NORTH_STAR_V1.sha256,
        OFFICIAL_MASCOT.git_blob_sha,
        "permanent MarketDEX brand element",
        "No release may silently omit the mascot",
    ):
        assert required in standard

    assert "Mission Control Visual North Star — Design Locked" in vision
    assert "MarketDEX Mascot" in vision
    assert APPROVED_VISUAL_NORTH_STAR_V1.relative_path in visual
    assert APPROVED_VISUAL_NORTH_STAR_V1.relative_path in checkpoint
    assert OFFICIAL_MASCOT.relative_path in checkpoint
