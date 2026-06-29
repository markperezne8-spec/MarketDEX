from pathlib import Path
import shutil

class BackupService:
    def backup_database(self, database_path):
        backup_dir=Path("data/backups")
        backup_dir.mkdir(parents=True,exist_ok=True)
        dest=backup_dir/"marketdex_backup.db"
        shutil.copy2(database_path,dest)
        return dest
