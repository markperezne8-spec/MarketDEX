class InventoryRepository:
 def get(self,c,asset_id): return c.execute('SELECT * FROM inventory_authority WHERE asset_id=?',(asset_id,)).fetchone()
 def apply(self,c,*,asset_id,quantity_delta,cost_delta_minor,event_id,recorded_at):
  row=self.get(c,asset_id); q=int(row['quantity']) if row else 0; cost=int(row['total_cost_minor']) if row else 0
  nq=q+quantity_delta; nc=cost+cost_delta_minor
  if nq < 0: raise ValueError('Quantity cannot become negative')
  if nc < 0: raise ValueError('Cost cannot be created or silently lost')
  if row: c.execute('UPDATE inventory_authority SET quantity=?,total_cost_minor=?,last_event_id=?,verified_at=? WHERE asset_id=?',(nq,nc,event_id,recorded_at,asset_id))
  else: c.execute('INSERT INTO inventory_authority VALUES (?,?,?,?,?)',(asset_id,nq,nc,event_id,recorded_at))
  c.execute('INSERT INTO inventory_history(event_id,asset_id,quantity_delta,cost_delta_minor,resulting_quantity,resulting_total_cost_minor,recorded_at) VALUES (?,?,?,?,?,?,?)',(event_id,asset_id,quantity_delta,cost_delta_minor,nq,nc,recorded_at))
  return nq,nc
 def history_count(self,c,asset_id): return int(c.execute('SELECT COUNT(*) FROM inventory_history WHERE asset_id=?',(asset_id,)).fetchone()[0])
