from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4

@dataclass
class Asset:
    uuid:str=""
    name:str=""
    asset_type:str="Raw Card"
    set_name:str=""
    card_number:str=""
    rarity:str=""
    variant:str=""
    condition:str="Near Mint"
    quantity:int=1
    purchase_price:float=0.0
    current_value:float=0.0
    created_at:str=""

    def __post_init__(self):
        if not self.uuid:
            self.uuid=str(uuid4())
        if not self.created_at:
            self.created_at=datetime.utcnow().isoformat()
