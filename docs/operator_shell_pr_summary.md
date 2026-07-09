# Operator Shell Recomposition PR Summary

This change separates the dense legacy viewport into five operator workspaces: Mission Control, Inventory, Pricing, Listings, and Sales.

Mission Control becomes the default first tab and displays the same eight values from the existing business snapshot service. The original dashboard cards embedded above Inventory are hidden rather than deleted, preserving the permanent codebase while the operator shell is recomposed.

A clear Open Inventory action moves the operator into Inventory. Inventory hands off to Pricing, and Pricing hands off to Listings. Listing execution history and sale completion are separated into Sales.

The listing workflow widgets, inventory controls, pricing calculations, services, repositories, SQLite authority, and sale completion behavior are preserved.
