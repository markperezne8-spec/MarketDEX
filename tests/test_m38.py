from pathlib import Path
from tempfile import TemporaryDirectory

from services.m38_acceptance_service import M38AcceptanceService


with TemporaryDirectory(prefix="marketdex_m38_") as temp_dir:
    p = Path(temp_dir) / "m38_acceptance.sqlite3"
    service = M38AcceptanceService(p)
    result = service.execute()
    assert result["passed"] == 12, result
    assert result["quantity"] == 1, result
    assert result["active"] == 0, result
    assert result["available"] == 1, result
    assert result["allocation"] == "CONSUMED", result
    assert result["inventory"] == "EXACTLY ONCE", result
    assert result["financial"] == "VERIFIED", result
    assert result["second_financial"] == "NO", result
    assert result["lineage"] == "VERIFIED", result
    assert result["replay"] == "PASS", result

    del service
    reopened = M38AcceptanceService(p)
    restart = reopened.verify()
    assert restart["passed"] == 12, restart
    assert restart["quantity"] == 1, restart
    assert restart["active"] == 0, restart
    assert restart["available"] == 1, restart
    assert restart["restart"] == "PASS", restart

print("M38 authority gates verified: 12 / 12")
print("M24 DIRECT SALE AUTHORITY INTEGRATION: PASS")
print("EXACTLY-ONCE INVENTORY DEPLETION: PASS")
print("M24 FINANCIAL TRUTH / ZERO DUPLICATE FINANCIAL EVENT: PASS")
print("M30 SOLD CONVERSION: PASS")
print("COMPLETE PRODUCT-AWARE SALE LINEAGE: PASS")
print("PERSISTENT REPLAY DEFENSE: PASS")
print("RESTART RECONSTRUCTION: PASS")
print("M38 RESULT: PRODUCT-AWARE SALE VERIFIED")
