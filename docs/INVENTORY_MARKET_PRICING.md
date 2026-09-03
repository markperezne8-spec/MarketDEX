# Daily Online Market Pricing

MarketDEX reads current market pricing through the official TCGplayer API. It does not scrape marketplace pages and it never changes an Inventory Listing Draft asking price automatically.

## Credentials

TCGplayer API access requires an existing API Developer Key. TCGplayer's official documentation currently says new API access is not being granted. If you already have access, expose the bearer token to MarketDEX as an environment variable.

PowerShell for the current user:

```powershell
[Environment]::SetEnvironmentVariable(
  "TCGPLAYER_BEARER_TOKEN",
  "PASTE_YOUR_BEARER_TOKEN_HERE",
  "User"
)
```

Close and reopen MarketDEX after setting the variable. To use the variable only in the current PowerShell window:

```powershell
$env:TCGPLAYER_BEARER_TOKEN = "PASTE_YOUR_BEARER_TOKEN_HERE"
python launcher.py
```

Never commit the token to GitHub or place it in source code.

## Pricing behavior

- Market prices are stored independently from the draft asking price.
- A Ready to List inventory item is refreshed automatically when its saved price is missing or at least 24 hours old.
- Refresh runs in a background worker so the UI remains responsive.
- Use **Refresh Price** for an individual item.
- The UI shows **Updated**, **Source**, and **Price unavailable** states.
- Missing credentials, network failures, invalid catalog matches, and unavailable prices are recorded as status/error information instead of raising an unhandled UI error.

## Official API endpoints used

- Catalog product lookup: https://api.tcgplayer.com/catalog/products
- Product market price: https://api.tcgplayer.com/pricing/product/{productId}
- Condition-specific market price: https://api.tcgplayer.com/pricing/marketprices/{productconditionId}

Documentation: https://docs.tcgplayer.com/docs/getting-started

## Market price history warehouse

Each manual or automatic refresh appends one observation to SQLite, including successful prices and unavailable/error results. The latest result remains in the current online market-price snapshot for fast Draft display, while the **View Price History** action opens the retained observation ledger. This history is local, survives application restart, and never changes the draft or inventory asking price.

