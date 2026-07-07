# Inventory CSV Export Checkpoint

Accepted parent merge SHA: `fd924fdc5b090a49d104091397ce24ffbc6a3e74`.

Visible workflow: Mission Control exposes Export CSV beside the inventory controls. The exported file contains the exact current searched, type-filtered, and sorted inventory projection with Asset ID, Asset Name, Asset Type, Quantity, and decimal Total Cost columns. UTF-8 BOM output is compatible with LibreOffice Calc.

CSV export is projection-only and read-only to MarketDEX authority. It appends no event identity, inventory history, movement, or audit evidence and does not mutate the protected M39-M165 authority spine.
