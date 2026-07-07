from uuid import uuid4
class ConformanceService:
    def __init__(self,database,services): self.database,self.s=database,services
    def run_clean_acceptance(self):
        op=str(uuid4())
        self.s.asset.create_asset(request_id=f'{op}:asset',asset_id=f'BOX-{op[:8]}',asset_name='M28 Acceptance Box',asset_type='BOX',state='COMPLETED')
        box=f'BOX-{op[:8]}'; pack=f'PACK-{op[:8]}'
        self.s.inventory.apply_acquisition(request_id=f'{op}:acq',asset_id=box,quantity=1,total_cost_minor=6000)
        self.s.transformation.execute(request_id=f'{op}:transform',transformation_id=f'TRF-{op}',source_asset_id=box,source_quantity=1,outputs=[{'asset_id':pack,'asset_name':'M28 Acceptance Packs','asset_type':'PACK','quantity':6,'allocated_cost_minor':6000}])
        self.s.integration.allocate(request_id=f'{op}:alloc',allocation_id=f'ALLOC-{op}',asset_id=pack,marketplace='EBAY',allocated_quantity=2,publication_reference='M28-PUBLICATION')
        oversell_blocked=False
        try: self.s.integration.allocate(request_id=f'{op}:oversell',allocation_id=f'OVER-{op}',asset_id=pack,marketplace='TCGPLAYER',allocated_quantity=5,publication_reference='M28-OVERSELL')
        except ValueError: oversell_blocked=True
        self.s.sales.record_sale(request_id=f'{op}:sale',sale_id=f'SALE-{op}',asset_id=pack,quantity=2,revenue_minor=3000,marketplace_fees_minor=300,shipping_minor=500,packaging_minor=100)
        self.s.integration.settle_and_close(request_id=f'{op}:close',settlement_reference=f'SET-{op}',sale_id=f'SALE-{op}',settled_minor=2100)
        self.s.return_service.execute(request_id=f'{op}:return',return_id=f'RET-{op}',sale_id=f'SALE-{op}',quantity=2,condition_evidence='SEALED VERIFIED',restock_authorized=True,refund_minor=3000)
        with self.database.connect() as c: sale_event=c.execute('SELECT created_event_id FROM sales WHERE sale_id=?',(f'SALE-{op}',)).fetchone()[0]
        self.s.correction.execute(request_id=f'{op}:correction',correction_event_id=f'COR-{op}',original_event_id=sale_event,corrective_evidence='M28 verified corrective evidence')
        self.s.integration.detect_variance(request_id=f'{op}:exception',exception_id=f'EXC-{op}',asset_id=pack,expected_quantity=5)
        self.s.integration.resolve_exception(request_id=f'{op}:resolution',resolution_event_id=f'RES-{op}',exception_id=f'EXC-{op}',evidence='Explicit controlled resolution verified')
        self.s.audit.verify(request_id=f'{op}:audit',audit_verification_id=f'AUD-{op}',target_event_id=sale_event)
        m=self.s.dashboard.mission_control()
        return {'operation':op,'box':box,'pack':pack,'oversell_blocked':oversell_blocked,'mission':m}
