# Runtime Database Authority Contract

MarketDEX desktop runtime data lives in `runtime/marketdex.sqlite3`.

The runtime directory and SQLite database, WAL, and shared-memory files are excluded from Git so repository pulls and merges do not replace the operator's live local business authority.

Historical acceptance databases under `data/` are not desktop runtime authority.

The launcher opens the permanent local runtime database and preserves the offline-first architecture. No subscription, remote database, marketplace authentication, publication, or synchronization is introduced by this boundary.
