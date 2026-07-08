from ui.inventory_sale_readiness_feature import sale_decision


def test_sale_decision_reports_projected_margin():
    row = {'quantity': 2, 'total_cost_minor': 10000}
    result = sale_decision(row, 8000)
    assert result['unit_cost_minor'] == 5000
    assert result['margin_minor'] == 3000
    assert result['margin_percent'] == 37.5
    assert result['status'] == 'SALE READY'


def test_sale_decision_flags_loss_and_thin_margin():
    row = {'quantity': 1, 'total_cost_minor': 6500}
    assert sale_decision(row, 6000)['status'] == 'LOSS'
    assert sale_decision(row, 7000)['status'] == 'THIN MARGIN'
    assert sale_decision(row, 0)['status'] == 'SET ASKING PRICE'
