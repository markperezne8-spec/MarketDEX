class AssetService:
    def __init__(self, repository):
        self.repository=repository
    def save_asset(self, asset):
        if not asset.name.strip():
            raise ValueError("Asset name required")
        return self.repository.add(asset)
