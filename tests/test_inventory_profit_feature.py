from ui.inventory_profit_feature import profit_decision


def test_true_profit_includes_all_selling_costs():
    result=profit_decision(5000,8000,12.75,500,100)
    assert result['fees_minor']==1020
    assert result['net_profit_minor']==1380
    assert result['roi_percent']==27.6


def test_true_profit_can_expose_loss():
    result=profit_decision(6500,7000,13.25,600,100)
    assert result['fees_minor']==928
    assert result['net_profit_minor']==-1128
    assert result['roi_percent'] < 0
