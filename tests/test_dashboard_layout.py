from app.ui.mission_control.layouts.dashboard_layout import DashboardLayout

def test_dashboard_layout():
    assert len(DashboardLayout().build())>=10
