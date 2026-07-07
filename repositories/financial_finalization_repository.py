class FinancialFinalizationRepository:
    def ensure_schema(self, c):
        c.executescript('''
        CREATE TABLE IF NOT EXISTS financial_finalizations (
          finalization_id TEXT PRIMARY KEY, closure_id TEXT NOT NULL UNIQUE,
          sale_id TEXT NOT NULL UNIQUE, settlement_id TEXT NOT NULL UNIQUE,
          finalization_request_id TEXT NOT NULL UNIQUE, finalization_event_id TEXT NOT NULL UNIQUE,
          revenue_minor INTEGER NOT NULL, marketplace_fees_minor INTEGER NOT NULL,
          shipping_minor INTEGER NOT NULL, packaging_minor INTEGER NOT NULL,
          cogs_minor INTEGER NOT NULL, profit_minor INTEGER NOT NULL,
          observed_payout_minor INTEGER NOT NULL, finalization_result TEXT NOT NULL CHECK(finalization_result='FINALIZED'),
          created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS financial_finalization_history (
          history_id INTEGER PRIMARY KEY AUTOINCREMENT, finalization_id TEXT NOT NULL,
          closure_id TEXT NOT NULL, sale_id TEXT NOT NULL, settlement_id TEXT NOT NULL,
          finalization_event_id TEXT NOT NULL, finalization_result TEXT NOT NULL CHECK(finalization_result='FINALIZED'),
          recorded_at TEXT NOT NULL, UNIQUE(finalization_event_id,finalization_result));
        CREATE TRIGGER IF NOT EXISTS financial_finalizations_no_update BEFORE UPDATE ON financial_finalizations BEGIN SELECT RAISE(ABORT,'financial_finalizations is append-only'); END;
        CREATE TRIGGER IF NOT EXISTS financial_finalizations_no_delete BEFORE DELETE ON financial_finalizations BEGIN SELECT RAISE(ABORT,'financial_finalizations is append-only'); END;
        CREATE TRIGGER IF NOT EXISTS financial_finalization_history_no_update BEFORE UPDATE ON financial_finalization_history BEGIN SELECT RAISE(ABORT,'financial_finalization_history is append-only'); END;
        CREATE TRIGGER IF NOT EXISTS financial_finalization_history_no_delete BEFORE DELETE ON financial_finalization_history BEGIN SELECT RAISE(ABORT,'financial_finalization_history is append-only'); END;
        ''')

    def append(self,c,*,finalization_id,closure_id,sale_id,settlement_id,request_id,event_id,financial,observed_payout_minor,created_at):
        values=(finalization_id,closure_id,sale_id,settlement_id,request_id,event_id,int(financial['revenue_minor']),int(financial['marketplace_fees_minor']),int(financial['shipping_minor']),int(financial['packaging_minor']),int(financial['cogs_minor']),int(financial['profit_minor']),int(observed_payout_minor),'FINALIZED',created_at)
        c.execute('INSERT INTO financial_finalizations VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',values)
        c.execute('INSERT INTO financial_finalization_history(finalization_id,closure_id,sale_id,settlement_id,finalization_event_id,finalization_result,recorded_at) VALUES (?,?,?,?,?,?,?)',(finalization_id,closure_id,sale_id,settlement_id,event_id,'FINALIZED',created_at))

    def by_id(self,c,finalization_id): return c.execute('SELECT * FROM financial_finalizations WHERE finalization_id=?',(finalization_id,)).fetchone()
    def by_request(self,c,request_id): return c.execute('SELECT * FROM financial_finalizations WHERE finalization_request_id=?',(request_id,)).fetchone()
