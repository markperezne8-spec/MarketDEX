from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class BrandAssetDefinition:
    asset_id: str
    relative_path: str
    git_blob_sha: str
    sha256: str | None = None
    width: int | None = None
    height: int | None = None
    status: str = "canonical"
    required_in_source: bool = True
    required_in_package: bool = True


APPROVED_VISUAL_NORTH_STAR_V1 = BrandAssetDefinition(
    asset_id="visual-north-star-v1",
    relative_path=(
        "assets/brand/visual_north_star/marketdex_visual_north_star_v1.png"
    ),
    git_blob_sha="27d4b34b24984678225ae38c7e77240a02d521b4",
    sha256="1269e2af119c569cc5d4f76b82a6f92984a04f6f752119d8e1dcf417557909a5",
    width=1536,
    height=1024,
    status="approved-pending-binary-sync",
    required_in_source=False,
    required_in_package=False,
)


HISTORICAL_VISUAL_NORTH_STAR = BrandAssetDefinition(
    asset_id="visual-north-star-historical-v0",
    relative_path="MarketDEX_Mission_Control_Visual_North_Star.png",
    git_blob_sha="2ad414034ab1715c2f5019acc2ccff71f213706c",
    status="historical-compatibility",
)

# Compatibility alias used by current source/package tests until the approved v1
# binary is committed and packaging migration is complete. It must not be
# interpreted as active product-design authority.
VISUAL_NORTH_STAR = HISTORICAL_VISUAL_NORTH_STAR


OFFICIAL_MASCOT = BrandAssetDefinition(
    asset_id="official-mascot",
    relative_path="MarketDEX_Official_Mascot.png",
    git_blob_sha="5c192e8833896cf754f20fcb636d30098bc75ecf",
    sha256="32fad644bd5e8f6cfa4a3166913030fc4520ad0fef560943f4e432a5f39cebc4",
    width=1254,
    height=1254,
    status="canonical-permanent",
)


# Assets currently required by source, executable, installer, and installed
# runtime verification. The v1 Visual North Star joins this tuple only after its
# exact approved binary is synchronized and packaging paths are migrated.
REQUIRED_BRAND_ASSETS = (
    VISUAL_NORTH_STAR,
    OFFICIAL_MASCOT,
)


# Product-approved identities, including assets that may still have a visible
# synchronization gate. This is product direction, not proof of package delivery.
APPROVED_BRAND_ASSETS = (
    APPROVED_VISUAL_NORTH_STAR_V1,
    OFFICIAL_MASCOT,
)


def source_asset_path(asset: BrandAssetDefinition, repository_root: Path) -> Path:
    """Resolve a required source asset without providing a silent fallback."""
    path = repository_root / asset.relative_path
    if not path.is_file():
        raise FileNotFoundError(
            f"Required MarketDEX brand asset is missing: {asset.relative_path}"
        )
    return path


def approved_asset_path(asset: BrandAssetDefinition, repository_root: Path) -> Path:
    """Resolve a Product Owner-approved asset and fail visibly while unsynced."""
    path = repository_root / asset.relative_path
    if not path.is_file():
        raise FileNotFoundError(
            "Approved MarketDEX asset has not been synchronized to the repository: "
            f"{asset.relative_path} (expected sha256={asset.sha256})"
        )
    return path
