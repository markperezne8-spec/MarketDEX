from dataclasses import dataclass

@dataclass
class InventoryItem:
    name:str=""
    quantity:int=0
    purchase_price:float=0.0
