import pytest

from composition.feature_catalog import (
    CORE_DESKTOP_FEATURES,
    FeatureDefinition,
    install_features,
    validate_feature_catalog,
)


def test_core_desktop_feature_catalog_has_stable_unique_identity_and_dependencies():
    catalog = validate_feature_catalog(CORE_DESKTOP_FEATURES)
    feature_ids = [feature.feature_id for feature in catalog]

    assert len(feature_ids) == len(set(feature_ids))
    assert feature_ids[:5] == [
        'inventory-edit',
        'inventory-cost',
        'inventory-sale-readiness',
        'inventory-profit',
        'inventory-price-guidance',
    ]
    assert feature_ids[-1] == 'wheel-safe-value-controls'
    assert catalog[1].depends_on == ('inventory-edit',)
    assert catalog[-2].depends_on == ('inventory-listing-execution-history',)


def test_feature_catalog_rejects_duplicate_identity_before_installation():
    calls = []
    installer = lambda window: calls.append(window)
    features = (
        FeatureDefinition('duplicate', installer),
        FeatureDefinition('duplicate', installer),
    )

    with pytest.raises(ValueError, match='duplicate feature ids'):
        install_features(object(), features)

    assert calls == []


def test_feature_catalog_rejects_missing_and_out_of_order_dependencies_before_installation():
    calls = []
    installer = lambda window: calls.append(window)

    with pytest.raises(ValueError, match='missing feature dependencies'):
        install_features(
            object(),
            (FeatureDefinition('dependent', installer, ('missing',)),),
        )

    with pytest.raises(ValueError, match='must be installed first'):
        install_features(
            object(),
            (
                FeatureDefinition('dependent', installer, ('foundation',)),
                FeatureDefinition('foundation', installer),
            ),
        )

    assert calls == []


def test_feature_definition_rejects_invalid_contracts():
    with pytest.raises(ValueError, match='must not be empty'):
        FeatureDefinition('', lambda window: None)
    with pytest.raises(ValueError, match='surrounding whitespace'):
        FeatureDefinition(' invalid ', lambda window: None)
    with pytest.raises(TypeError, match='must be callable'):
        FeatureDefinition('invalid', object())
    with pytest.raises(ValueError, match='duplicate feature dependencies'):
        FeatureDefinition('invalid', lambda window: None, ('one', 'one'))
    with pytest.raises(ValueError, match='must not depend on itself'):
        FeatureDefinition('invalid', lambda window: None, ('invalid',))
