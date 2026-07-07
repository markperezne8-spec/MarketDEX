from core.event_repository import ReplayRejected

class M29AcceptanceService:
    def __init__(self,database,services): self.database,self.s=database,services

    def run(self):
        asset='M29-ASSET'
        with self.database.connect() as c: exists=c.execute('SELECT 1 FROM assets WHERE asset_id=?',(asset,)).fetchone()
        if exists is None:
            self.s.asset.create_asset(request_id='M29:ASSET',asset_id=asset,asset_name='M29 Damage Loss Test Asset',asset_type='SINGLE',state='COMPLETED')
            self.s.inventory.apply_acquisition(request_id='M29:ACQUISITION',asset_id=asset,quantity=3,total_cost_minor=300)

        incomplete=self.s.adjustment.eligibility(asset_id=asset,adjustment_type='DAMAGE',adjustment_quantity=1,evidence_type='PHOTO',evidence_reference='',evidence_complete=False,request_id='M29:DAMAGE:BLOCK')
        if incomplete['adjustment_eligible'] or incomplete['control_result']!='BLOCKED': raise RuntimeError('Incomplete damage evidence did not fail closed')

        self._execute_or_replay(request_id='M29:DAMAGE:1',adjustment_id='M29-DAMAGE-1',asset_id=asset,adjustment_type='DAMAGE',adjustment_quantity=1,evidence_type='PHOTO',evidence_reference='M29-DAMAGE-EVIDENCE',evidence_complete=True)
        self._must_replay_block(request_id='M29:DAMAGE:1',adjustment_id='M29-DAMAGE-REPLAY',asset_id=asset,adjustment_type='DAMAGE',adjustment_quantity=1,evidence_type='PHOTO',evidence_reference='M29-DAMAGE-EVIDENCE',evidence_complete=True)

        loss_block=self.s.adjustment.eligibility(asset_id=asset,adjustment_type='LOSS',adjustment_quantity=3,evidence_type='LOSS_REPORT',evidence_reference='M29-LOSS-OVER',evidence_complete=True,request_id='M29:LOSS:BLOCK')
        if loss_block['adjustment_eligible'] or loss_block['control_result']!='BLOCKED': raise RuntimeError('Excess loss quantity did not fail closed')

        self._execute_or_replay(request_id='M29:LOSS:1',adjustment_id='M29-LOSS-1',asset_id=asset,adjustment_type='LOSS',adjustment_quantity=1,evidence_type='LOSS_REPORT',evidence_reference='M29-LOSS-EVIDENCE',evidence_complete=True)
        self._must_replay_block(request_id='M29:LOSS:1',adjustment_id='M29-LOSS-REPLAY',asset_id=asset,adjustment_type='LOSS',adjustment_quantity=1,evidence_type='LOSS_REPORT',evidence_reference='M29-LOSS-EVIDENCE',evidence_complete=True)
        return self.verify()

    def _execute_or_replay(self,**kwargs):
        try: self.s.adjustment.execute(**kwargs)
        except ReplayRejected: pass

    def _must_replay_block(self,**kwargs):
        try: self.s.adjustment.execute(**kwargs)
        except ReplayRejected: return
        raise RuntimeError('Replay created second adjustment authority')

    def verify(self):
        with self.database.connect() as c:
            q=int(c.execute("SELECT quantity FROM inventory_authority WHERE asset_id='M29-ASSET'").fetchone()[0])
            damage=int(c.execute("SELECT COUNT(*) FROM inventory_adjustments WHERE adjustment_type='DAMAGE'").fetchone()[0])
            loss=int(c.execute("SELECT COUNT(*) FROM inventory_adjustments WHERE adjustment_type='LOSS'").fetchone()[0])
            movements=int(c.execute("SELECT COUNT(*) FROM inventory_movements WHERE movement_type IN ('DAMAGE','LOSS')").fetchone()[0])
            audits=int(c.execute("SELECT COUNT(*) FROM audit_events WHERE authority_type IN ('DAMAGE','LOSS') AND verification_result='VERIFIED'").fetchone()[0])
            replay=int(c.execute("SELECT COUNT(*) FROM replay_defense_history WHERE request_id IN ('M29:DAMAGE:1','M29:LOSS:1')").fetchone()[0])
            deltas=[int(r[0]) for r in c.execute("SELECT quantity_delta FROM inventory_movements WHERE movement_type IN ('DAMAGE','LOSS') ORDER BY recorded_at").fetchall()]
            expected=int(c.execute("SELECT COALESCE(SUM(quantity_delta),0) FROM inventory_history WHERE asset_id='M29-ASSET'").fetchone()[0])
        return {'quantity':q,'damage':damage,'loss':loss,'movements':movements,'audits':audits,'replay':replay,'deltas':deltas,'reconciled':expected==q}
