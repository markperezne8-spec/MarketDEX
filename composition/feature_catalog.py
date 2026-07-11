from collections.abc import Callable, Iterable
from dataclasses import dataclass

from ui.inventory_completed_listing_package_queue_feature import install_inventory_completed_listing_package_queue_feature
from ui.inventory_cost_feature import install_inventory_cost_feature
from ui.inventory_edit_feature import install_inventory_edit_feature
from ui.inventory_listing_execution_history_feature import install_inventory_listing_execution_history_feature
from ui.inventory_listing_execution_readiness_feature import install_inventory_listing_execution_readiness_feature
from ui.inventory_listing_plan_queue_feature import install_inventory_listing_plan_queue_feature
from ui.inventory_listing_workspace_feature import install_inventory_listing_workspace_feature
from ui.inventory_marketplace_listing_package_review_feature import install_inventory_marketplace_listing_package_review_feature
from ui.inventory_marketplace_listing_preparation_feature import install_inventory_marketplace_listing_preparation_feature
from ui.inventory_price_guidance_feature import install_inventory_price_guidance_feature
from ui.inventory_profit_feature import install_inventory_profit_feature
from ui.inventory_sale_completion_feature import install_inventory_sale_completion_feature
from ui.inventory_sale_readiness_feature import install_inventory_sale_readiness_feature
from ui.wheel_safe_value_controls_feature import install_wheel_safe_value_controls_feature


FeatureInstaller = Callable[[object], None]


@dataclass(frozen=True)
class FeatureDefinition:
    feature_id: str
    installer: FeatureInstaller

    def __post_init__(self) -> None:
        normalized = self.feature_id.strip()
        if not normalized:
            raise ValueError('feature_id must not be empty')
        if normalized != self.feature_id:
            raise ValueError('feature_id must not contain surrounding whitespace')
        if not callable(self.installer):
            raise TypeError(f'feature installer must be callable: {self.feature_id}')


CORE_DESKTOP_FEATURES = (
    FeatureDefinition('inventory-edit', install_inventory_edit_feature),
    FeatureDefinition('inventory-cost', install_inventory_cost_feature),
    FeatureDefinition('inventory-sale-readiness', install_inventory_sale_readiness_feature),
    FeatureDefinition('inventory-profit', install_inventory_profit_feature),
    FeatureDefinition('inventory-price-guidance', install_inventory_price_guidance_feature),
    FeatureDefinition('inventory-listing-workspace', install_inventory_listing_workspace_feature),
    FeatureDefinition('inventory-listing-plan-queue', install_inventory_listing_plan_queue_feature),
    FeatureDefinition('inventory-listing-execution-readiness', install_inventory_listing_execution_readiness_feature),
    FeatureDefinition('inventory-marketplace-listing-preparation', install_inventory_marketplace_listing_preparation_feature),
    FeatureDefinition('inventory-marketplace-listing-package-review', install_inventory_marketplace_listing_package_review_feature),
    FeatureDefinition('inventory-completed-listing-package-queue', install_inventory_completed_listing_package_queue_feature),
    FeatureDefinition('inventory-listing-execution-history', install_inventory_listing_execution_history_feature),
    FeatureDefinition('inventory-sale-completion', install_inventory_sale_completion_feature),
    FeatureDefinition('wheel-safe-value-controls', install_wheel_safe_value_controls_feature),
)


def validate_feature_catalog(features: Iterable[FeatureDefinition]) -> tuple[FeatureDefinition, ...]:
    catalog = tuple(features)
    seen: set[str] = set()
    duplicates: set[str] = set()
    for feature in catalog:
        if feature.feature_id in seen:
            duplicates.add(feature.feature_id)
        seen.add(feature.feature_id)
    if duplicates:
        raise ValueError(f'duplicate feature ids: {", ".join(sorted(duplicates))}')
    return catalog


def install_features(window, features: Iterable[FeatureDefinition] = CORE_DESKTOP_FEATURES) -> None:
    for feature in validate_feature_catalog(features):
        feature.installer(window)
