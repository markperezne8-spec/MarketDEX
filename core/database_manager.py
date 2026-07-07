import sqlite3
from pathlib import Path
from contextlib import contextmanager
from datetime import datetime,timezone
from .schema import SCHEMA_SQL,SCHEMA_VERSION
class DatabaseManager:
 def __init__(self,database_path:Path): self.database_path=Path(database_path); self.database_path.parent.mkdir(parents=True,exist_ok=True)
 def connect(self):
  c=sqlite3.connect(self.database_path); c.row_factory=sqlite3.Row; c.execute('PRAGMA foreign_keys=ON'); c.execute('PRAGMA journal_mode=WAL'); return c
 def initialize(self):
  with self.connect() as c:
   c.executescript(SCHEMA_SQL); row=c.execute('SELECT schema_version FROM schema_metadata ORDER BY rowid DESC LIMIT 1').fetchone(); current=0 if row is None else int(row['schema_version'])
   if current>SCHEMA_VERSION: raise RuntimeError(f'Unsupported schema version: {current}')
   c.executescript(SCHEMA_SQL)
   if current<SCHEMA_VERSION:c.execute('INSERT INTO schema_metadata VALUES (?,?)',(SCHEMA_VERSION,datetime.now(timezone.utc).isoformat()))
 @contextmanager
 def transaction(self):
  c=self.connect()
  try:c.execute('BEGIN IMMEDIATE'); yield c; c.commit()
  except Exception as exc:
   from core.event_repository import ReplayRejected
   if isinstance(exc,ReplayRejected): c.commit()
   else: c.rollback()
   raise
  finally:c.close()
