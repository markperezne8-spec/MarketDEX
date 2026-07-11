from __future__ import annotations

import hashlib
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
VISUAL_NORTH_STAR = (
    REPOSITORY_ROOT
    / "assets"
    / "brand"
    / "visual_north_star"
    / "marketdex_visual_north_star_v1.png"
)
OFFICIAL_MASCOT = REPOSITORY_ROOT / "MarketDEX_Official_Mascot.png"


def _git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_canonical_brand_assets_exist_and_match_approved_identity():
    assert VISUAL_NORTH_STAR.is_file()
    assert VISUAL_NORTH_STAR.stat().st_size == 2_863_520
    assert _sha256(VISUAL_NORTH_STAR) == (
        "1269e2af119c569cc5d4f76b82a6f92984a04f6f752119d8e1dcf417557909a5"
    )
    assert _git_blob_sha(VISUAL_NORTH_STAR) == (
        "27d4b34b24984678225ae38c7e77240a02d521b4"
    )

    assert OFFICIAL_MASCOT.is_file()
    assert OFFICIAL_MASCOT.stat().st_size == 2_269_552
    assert _sha256(OFFICIAL_MASCOT) == (
        "32fad644bd5e8f6cfa4a3166913030fc4520ad0fef560943f4e432a5f39cebc4"
    )
    assert _git_blob_sha(OFFICIAL_MASCOT) == (
        "5c192e8833896cf754f20fcb636d30098bc75ecf"
    )


def test_pyinstaller_spec_packages_both_canonical_brand_assets():
    spec = (REPOSITORY_ROOT / "MarketDEX.spec").read_text(encoding="utf-8")

    assert "marketdex_visual_north_star_v1.png" in spec
    assert "MarketDEX_Official_Mascot.png" in spec
    assert "assets/brand/visual_north_star" in spec
    assert "datas=brand_assets" in spec
