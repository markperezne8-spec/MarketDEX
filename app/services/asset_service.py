from app.repositories.asset_repository import AssetRepository

class AssetService:
    def __init__(self):
        self.repo=AssetRepository()
        self.repo.initialize()

    def create_asset(self, asset):
        self.repo.add(asset)

    def get_assets(self):
        return self.repo.all()
