# MarketDEX OS

MarketDEX is a Windows desktop, offline-first collectibles business operating system. It helps organize inventory, collection positions, pricing, listings, sales, settlement evidence, reports, and business intelligence while keeping authoritative data local and auditable.

## Version and releases

The canonical product version is maintained in `version.py` and verified against the Windows executable marker and installer metadata by CI. Releases should publish the installer first, with the portable executable clearly identified as an optional diagnostic artifact.

## Install on Windows

1. Open the repository's Releases page: https://github.com/markperezne8-spec/MarketDEX/releases
2. Download the latest MarketDEX_Setup.exe installer when available.
3. Run the installer and choose whether to create a desktop shortcut.
4. Launch MarketDEX OS from the Start Menu or desktop.
5. Your runtime database is stored in the user's local application data directory and is not replaced by the installer.

For a verified development build, download the Windows executable published with the release and launch MarketDEX.exe directly.

## First launch

MarketDEX opens to Mission Control, the command-center workspace. The application is designed to work offline first. Missing or insufficient evidence is shown explicitly instead of being converted into fabricated business values.

Primary workspaces include:

- Mission Control
- Inventory
- Collection
- Pricing
- Listings
- Market Intelligence
- Reports

## Data and safety

- Runtime SQLite data is kept outside the installed program files.
- The installer does not bundle, delete, or overwrite your runtime database.
- Business-state changes remain controlled by the application services and audit rules.
- Marketplace and external-provider execution is not assumed to be live or automatic.
- Back up your local application data before testing development builds or migrations.

## Developer quick start

    python -m venv .venv
    .venv\Scripts\activate
    pip install -r requirements.txt
    python launcher.py

On Windows, RUN_MARKETDEX.bat can prepare the environment and start the source runtime.

To verify runtime initialization without opening the window:

    python launcher.py --verify-runtime

## Project direction

The active visual and product direction is documented in:

- Visual North Star: docs/design/VISUAL_NORTH_STAR.md
- Design System Foundation: docs/design/DESIGN_SYSTEM_FOUNDATION.md
- MarketDEX Start Here: MARKETDEX_START_HERE.md
- Architecture Gates: docs/governance/Architecture_Gates.md

The canonical runtime path is the root launcher.py, the root ui/ shell, the application composition root, and the canonical runtime database authority.

## Support and bug reports

Please include:

- MarketDEX version or release name
- Windows version
- the workspace where the issue occurred
- exact reproduction steps
- the relevant sanitized error text

Do not attach your private SQLite database or credentials to a public issue.
