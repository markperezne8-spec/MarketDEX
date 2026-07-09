# Operator Shell First Slice PR Summary

This change separates Mission Control from the dense Inventory & Pricing workspace using the existing viewport composition feature.

Mission Control becomes the default first tab and displays the same eight values from the existing business snapshot service. The original dashboard cards embedded above Inventory are hidden rather than deleted, preserving the permanent codebase while the operator shell is recomposed.

A clear Open Inventory action moves the operator into Inventory & Pricing. The existing pricing-to-listing handoff now targets the third tab because Mission Control occupies the first workspace position.

The listing workflow widgets, inventory controls, services, repositories, SQLite authority, and sale completion behavior are preserved.
