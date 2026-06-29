class SearchService:
    def filter_assets(self, assets, text):
        text=text.lower()
        return [a for a in assets if text in getattr(a,"name","").lower()]
