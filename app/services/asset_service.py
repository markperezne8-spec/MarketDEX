from app.repositories.asset_repository import AssetRepository

class AssetService:
    def __init__(self):
        self.repo=AssetRepository()

    def assets(self):
        return self.repo.all()
