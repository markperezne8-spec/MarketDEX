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
    depends_on: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        normalized = self.feature_id.strip()
        if not normalized:
            raise ValueError('feature_id must not be empty')
        if normalized != self.feature_id:
            raise ValueError('feature_id must not contain surrounding whitespace')
        if not callable(self.installer):
            raise TypeError(f'feature installer must be callable: {self.feature_id}')
        if len(self.depends_on) != len(set(self.depends_on)):
            raise ValueError(f'duplicate feature dependencies: {self.feature_id}')
        if self.feature_id in self.depends_on:
            raise ValueError(f'feature must not depend on itself: {self.feature_id}')
        for dependency in self.depends_on:
            if not dependency or dependency.strip() != dependency:
                raise ValueError(
                    f'invalid feature dependency for {self.feature_id}: {dependency!r}'
                )


CORE_DESKTOP_FEATURES = (
    FeatureDefinition('inventory-edit', install_inventory_edit_feature),
    FeatureDefinition('inventory-cost', install_inventory_cost_feature, ('inventory-edit',)),
    FeatureDefinition(
        'inventory-sale-readiness',
        install_inventory_sale_readiness_feature,
        ('inventory-cost',),
    ),
    FeatureDefinition(
        'inventory-profit',
        install_inventory_profit_feature,
        ('inventory-cost', 'inventory-sale-readiness'),
    ),
    FeatureDefinition(
        'inventory-price-guidance',
        install_inventory_price_guidance_feature,
        ('inventory-profit',),
    ),
    FeatureDefinition(
        'inventory-listing-workspace',
        install_inventory_listing_workspace_feature,
        ('inventory-price-guidance',),
    ),
    FeatureDefinition(
        'inventory-listing-plan-queue',
        install_inventory_listing_plan_queue_feature,
        ('inventory-listing-workspace',),
    ),
    FeatureDefinition(
        'inventory-listing-execution-readiness',
        install_inventory_listing_execution_readiness_feature,
        ('inventory-listing-plan-queue',),
    ),
    FeatureDefinition(
        'inventory-marketplace-listing-preparation',
        install_inventory_marketplace_listing_preparation_feature,
        ('inventory-listing-execution-readiness',),
    ),
    FeatureDefinition(
        'inventory-marketplace-listing-package-review',
        install_inventory_marketplace_listing_package_review_feature,
        ('inventory-marketplace-listing-preparation',),
    ),
    FeatureDefinition(
        'inventory-completed-listing-package-queue',
        install_inventory_completed_listing_package_queue_feature,
        ('inventory-marketplace-listing-package-review',),
    ),
    FeatureDefinition(
        'inventory-listing-execution-history',
        install_inventory_listing_execution_history_feature,
        ('inventory-completed-listing-package-queue',),
    ),
    FeatureDefinition(
        'inventory-sale-completion',
        install_inventory_sale_completion_feature,
        ('inventory-listing-execution-history',),
    ),
    FeatureDefinition('wheel-safe-value-controls', install_wheel_safe_value_controls_feature),
)


def validate_feature_catalog(features: Iterable[FeatureDefinition]) -> tuple[FeatureDefinition, ...]:
    catalog = tuple(features)
    feature_ids = [feature.feature_id for feature in catalog]
    seen: set[str] = set()
    duplicates: set[str] = set()
    for feature_id in feature_ids:
        if feature_id in seen:
            duplicates.add(feature_id)
        seen.add(feature_id)
    if duplicates:
        raise ValueError(f'duplicate feature ids: {", ".join(sorted(duplicates))}')

    available = set(feature_ids)
    installed: set[str] = set()
    for feature in catalog:
        missing = set(feature.depends_on) - available
        if missing:
            raise ValueError(
                f'missing feature dependencies for {feature.feature_id}: '
                f'{", ".join(sorted(missing))}'
            )
        out_of_order = set(feature.depends_on) - installed
        if out_of_order:
            raise ValueError(
                f'feature dependencies must be installed first for {feature.feature_id}: '
                f'{", ".join(sorted(out_of_order))}'
            )
        installed.add(feature.feature_id)
    return catalog


def install_features(window, features: Iterable[FeatureDefinition] = CORE_DESKTOP_FEATURES) -> None:
    for feature in validate_feature_catalog(features):
        feature.installer(window)
