from core.database_manager import DatabaseManager
from core.listing_package_review_repository import ListingPackageReviewRepository


def test_review_state_persists_and_approval_marks_complete(tmp_path):
    database = DatabaseManager(tmp_path / 'marketdex.sqlite3')
    repository = ListingPackageReviewRepository(database)
    approved = repository.save('asset-1', 'PACKAGE APPROVED • OFFLINE ONLY')
    assert approved['review_state'] == 'PACKAGE APPROVED • OFFLINE ONLY'
    assert approved['completed'] == 1
    assert ListingPackageReviewRepository(database).get('asset-1')['completed'] == 1


def test_return_for_changes_clears_completion(tmp_path):
    database = DatabaseManager(tmp_path / 'marketdex.sqlite3')
    repository = ListingPackageReviewRepository(database)
    repository.save('asset-1', 'PACKAGE APPROVED • OFFLINE ONLY')
    returned = repository.save('asset-1', 'RETURNED FOR CHANGES')
    assert returned['completed'] == 0
