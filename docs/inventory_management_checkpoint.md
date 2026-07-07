# Inventory Management App Integration Checkpoint

Accepted parent merge SHA: `0967b5034e106186b87c642350a10e96993601b1`.

Visible workflow: select inventory row -> inspect authoritative asset detail -> adjust quantity and/or total cost by explicit delta -> append event, inventory history, movement, and verified audit evidence -> refresh Mission Control.

Negative resulting quantity or cost is blocked by the existing inventory authority repository. Zero adjustments are blocked. Request identity remains exactly-once through event identity.
