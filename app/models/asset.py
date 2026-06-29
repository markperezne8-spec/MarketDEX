from dataclasses import dataclass

@dataclass
class Asset:
    name:str=""
    category:str=""
    set_name:str=""
    card_number:str=""
    condition:str="Near Mint"
    quantity:int=1
    purchase_price:float=0.0
    current_value:float=0.0
