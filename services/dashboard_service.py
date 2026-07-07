class DashboardService:
    service_name = 'dashboard_service'

    def __init__(self, database):
        self.database = database

    def mission_control(self):
        with self.database.connect() as c:
            inventory = c.execute("""
                SELECT
                    COUNT(*) AS asset_count,
                    COALESCE(SUM(quantity),0) AS units_on_hand,
                    COALESCE(SUM(total_cost_minor),0) AS inventory_cost_minor
                FROM inventory_authority
            """).fetchone()

            sales = c.execute("""
                SELECT
                    COUNT(*) AS completed_sales,
                    COALESCE(SUM(revenue_minor),0) AS revenue_minor,
                    COALESCE(SUM(cogs_minor),0) AS cogs_minor,
                    COALESCE(SUM(profit_minor),0) AS sale_profit_minor
                FROM sales
                WHERE state='COMPLETED'
            """).fetchone()

            restatements = c.execute("""
                SELECT
                    COALESCE(SUM(profit_effect_minor),0) AS profit_restatement_minor
                FROM financial_events
            """).fetchone()

            transformations = c.execute("""
                SELECT COUNT(*) AS completed_transformations
                FROM transformations
                WHERE state='COMPLETED'
            """).fetchone()

            exceptions = c.execute("""
                SELECT COUNT(*) AS review_exceptions
                FROM exception_authority
                WHERE state='REVIEW'
            """).fetchone()

            audits = c.execute("""
                SELECT
                    COUNT(*) AS audit_count,
                    COALESCE(SUM(CASE WHEN verification_result='VERIFIED' THEN 1 ELSE 0 END),0) AS verified_audits
                FROM audit_verifications
            """).fetchone()

            corrections = c.execute("SELECT COUNT(*) AS n FROM correction_events").fetchone()
            reversals = c.execute("SELECT COUNT(*) AS n FROM reversal_events").fetchone()
            returns = c.execute("SELECT COUNT(*) AS n FROM returns").fetchone()
            events = c.execute("SELECT COUNT(*) AS n FROM event_identity").fetchone()

        realized_profit = int(sales['sale_profit_minor']) + int(restatements['profit_restatement_minor'])
        return {
            'asset_count': int(inventory['asset_count']),
            'units_on_hand': int(inventory['units_on_hand']),
            'inventory_cost_minor': int(inventory['inventory_cost_minor']),
            'completed_sales': int(sales['completed_sales']),
            'revenue_minor': int(sales['revenue_minor']),
            'cogs_minor': int(sales['cogs_minor']),
            'realized_profit_minor': realized_profit,
            'completed_transformations': int(transformations['completed_transformations']),
            'review_exceptions': int(exceptions['review_exceptions']),
            'audit_count': int(audits['audit_count']),
            'verified_audits': int(audits['verified_audits']),
            'returns': int(returns['n']),
            'corrections': int(corrections['n']),
            'reversals': int(reversals['n']),
            'authoritative_events': int(events['n']),
        }

    def recent_authority(self, limit=12):
        with self.database.connect() as c:
            rows=c.execute("""
                SELECT event_type, event_id, request_id, committed_at
                FROM event_identity
                ORDER BY committed_at DESC, event_id DESC
                LIMIT ?
            """,(int(limit),)).fetchall()
        return [dict(r) for r in rows]
