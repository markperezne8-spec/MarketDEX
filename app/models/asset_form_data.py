from dataclasses import dataclass
@dataclass
class AssetFormData:
    name:str=""
    set_name:str=""
    card_number:str=""
    purchase_price:float=0.0
    quantity:int=1
