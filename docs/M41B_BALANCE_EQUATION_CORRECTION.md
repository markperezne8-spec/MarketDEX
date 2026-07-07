# M41.B1 balance equation correction

The REALIZED_SALES_PROFIT ledger account stores finalized recognized profit after the M24 fee, shipping, and packaging financial truth has already been preserved upstream. M41.B1 therefore balances this account by reconstructing the exact sum of accepted POSTED `posted_profit_minor` values and reconciling that aggregate to the accepted posting lineage. It must not re-derive profit as `revenue - COGS`, because that discards the preserved M24 expense truth.
