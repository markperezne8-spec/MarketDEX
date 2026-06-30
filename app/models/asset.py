from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4


@dataclass
class Asset:
    """Asset model representing a collectible item (trading card, etc.)."""
    uuid: str = ""
    name: str = ""
    asset_type: str = "Raw Card"
    set_name: str = ""
    card_number: str = ""
    rarity: str = ""
    variant: str = ""
    card_condition: str = "Near Mint"
    quantity: int = 1
    purchase_price: float = 0.0
    current_value: float = 0.0
    purchase_date: str = ""
    purchase_source: str = ""
    storage_location: str = ""
    notes: str = ""
    status: str = "inventory"
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self):
        """Auto-generate UUID and timestamps if not provided."""
        if not self.uuid:
            self.uuid = str(uuid4())
        
        # Use UTC timezone-aware timestamp
        now_utc = datetime.now(timezone.utc).isoformat()
        
        if not self.created_at:
            self.created_at = now_utc
        
        if not self.updated_at:
            self.updated_at = now_utc
