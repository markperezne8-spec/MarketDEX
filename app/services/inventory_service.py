from app.models.inventory_item import InventoryItem
from app.repositories.inventory_repository import InventoryRepository

class InventoryService:
    def __init__(self):
        self.repo=InventoryRepository()

    def add_item(self,item:InventoryItem):
        self.repo.add(item)
