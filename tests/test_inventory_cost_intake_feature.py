from ui.inventory_cost_feature import unit_cost_minor, intake_quality


def test_unit_cost_minor_uses_total_cost_and_quantity():
    assert unit_cost_minor({'quantity': 4, 'total_cost_minor': 10001}) == 2500
    assert unit_cost_minor({'quantity': 0, 'total_cost_minor': 10001}) == 0


def test_intake_quality_counts_business_details():
    completed, total = intake_quality({
        'purchase_date': '2026-07-08',
        'purchase_source': 'Target',
        'storage_location': '',
        'notes': 'Hold sealed',
    })
    assert (completed, total) == (3, 4)
