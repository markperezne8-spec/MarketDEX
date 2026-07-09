# Architecture Note — Navigation versus workflow authority

`QTabWidget` owns primary workspace navigation. Its tabs must remain enabled because they expose durable MarketDEX workspaces.

Inventory selection owns contextual workflow authority. It controls whether guided handoff buttons can act on an asset.

The viewport feature must not use `setTabEnabled` to express asset selection state and must not redirect the current tab when selection clears.
