class AssetService:
    def __init__(self, repository):
        self.repository=repository

    def save_asset(self, asset):
        if not asset.name.strip():
            raise ValueError("Asset name required")
        return self.repository.add(asset)

    def update_asset(self, asset):
        return self.repository.update(asset)

    def delete_asset(self, asset_id):
        return self.repository.delete(asset_id)

    def search_assets(self, text):
        return self.repository.search(text)
