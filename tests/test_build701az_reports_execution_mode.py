from composition.application_composition import ApplicationComposition
from reports.definitions import CATALOG_ONLY_EXECUTION_MODE


def test_build701az_composition_exposes_report_execution_mode(tmp_path) -> None:
    composition = ApplicationComposition(tmp_path / 'marketdex.sqlite3')

    mode = composition.report_execution_mode(' INVENTORY-AGE-PATTERNS ')

    assert mode == CATALOG_ONLY_EXECUTION_MODE
