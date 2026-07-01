from app.ui.navigation.navigation_service import NavigationService

def test_nav():
 assert NavigationService().navigate('Dashboard')=='Dashboard'
