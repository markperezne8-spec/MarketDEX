from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class BrandAssetDefinition:
    asset_id: str
    relative_path: str
    git_blob_sha: str
    required_in_source: bool = True
    required_in_package: bool = True


VISUAL_NORTH_STAR = BrandAssetDefinition(
    asset_id="visual-north-star",
    relative_path="MarketDEX_Mission_Control_Visual_North_Star.png",
    git_blob_sha="2ad414034ab1715c2f5019acc2ccff71f213706c",
)

OFFICIAL_MASCOT = BrandAssetDefinition(
    asset_id="official-mascot",
    relative_path="MarketDEX_Official_Mascot.png",
    git_blob_sha="5c192e8833896cf754f20fcb636d30098bc75ecf",
)

REQUIRED_BRAND_ASSETS = (
    VISUAL_NORTH_STAR,
    OFFICIAL_MASCOT,
)


def source_asset_path(asset: BrandAssetDefinition, repository_root: Path) -> Path:
    """Resolve a canonical source asset without providing a silent fallback."""
    path = repository_root / asset.relative_path
    if not path.is_file():
        raise FileNotFoundError(
            f"Required MarketDEX brand asset is missing: {asset.relative_path}"
        )
    return path
