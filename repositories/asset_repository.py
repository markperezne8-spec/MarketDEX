class AssetRepository:
 def insert(self,c,*,asset_id,asset_name,asset_type,state,event_id,created_at):
  c.execute('INSERT INTO assets(asset_id,asset_name,asset_type,state,created_event_id,created_at) VALUES (?,?,?,?,?,?)',(asset_id,asset_name,asset_type,state,event_id,created_at))
 def get(self,c,asset_id): return c.execute('SELECT * FROM assets WHERE asset_id=?',(asset_id,)).fetchone()
 def count(self,c): return int(c.execute('SELECT COUNT(*) FROM assets').fetchone()[0])
