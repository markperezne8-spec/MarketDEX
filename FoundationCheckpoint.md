# MarketDEX Foundation Checkpoint 017

**Status:** 🏁 Verified Knowledge Checkpoint — Execution Handoff

## Active Phase
🚀 LibreOffice Calc Version 0 build execution.

## Checkpoint Theme
🔍 Inventory Reconciliation + Adjustment and Calc Version 0 Architecture Freeze.

## Design-Locked Inventory Contracts
🆔 Inventory Identity
📦 Product Form Taxonomy
🔢 Quantity + Unit Identity
💰 Cost Basis + Cost Layers
📍 Physical Location + Custody
🟡 Inventory Business State
🏪 Platform Exposure + Listing Relationship
📅 Inventory Age + Capital Commitment Clock
🔗 Inventory Lineage + Transformation
🔍 Inventory Reconciliation + Adjustment

## Reconciliation + Adjustment Core Contract
- Reconciliation compares recorded inventory truth with observed physical reality.
- Physical Count is observation and does not automatically replace authoritative inventory quantity.
- Variance derives from Observed Quantity minus Recorded Quantity at Observation.
- Reconciliation Observation preserves dated physical evidence.
- One observation checks one authoritative Inventory Record.
- VERIFIED and ESTIMATED Count Basis values remain explicit.
- Unknown Observed Quantity remains unknown.
- Reconciliation Case ID groups observations, recounts, investigation, and resolution for one discrepancy.
- Every recount creates a new observation and preserves earlier observations.
- MATCHED may resolve without an Adjustment Event.
- A known missing business event should own its correction.
- Inventory Adjustment is a last-resort authoritative quantity-changing event.
- Controlled Adjustment Reasons are COUNT ERROR, UNRECORDED LOSS, UNRECORDED DAMAGE, FOUND INVENTORY, LEGACY DATA CORRECTION, and OTHER REVIEW.
- Controlled Adjustment Statuses are DRAFT, REVIEW, POSTED, and REVERSED.
- Only POSTED adjustments change authoritative quantity.
- Adjustment Direction is INCREASE or DECREASE and Adjustment Quantity is a positive magnitude.
- DECREASE consumes attributable Cost Layers; FIFO is the Version 0 default for interchangeable quantity.
- INCREASE uses KNOWN COST, factually supported ZERO COST BASIS, or UNKNOWN COST.
- MarketDEX never invents acquisition cost.
- POSTED adjustments remain permanent history.
- Reversal uses linked offsetting evidence.
- Resolution Method and Resolution Date are preserved.
- Reopened cases preserve prior resolution history.
- Repeated variances, recounts, reopened cases, and Adjustment Reasons become Data Quality evidence.

## Visual Governance
`MarketDEX_Mission_Control_Visual_North_Star.png` remains the authoritative approved dashboard visual-direction reference.

`MarketDEX_Official_Mascot.png` remains the authoritative locked MarketDEX mascot asset.

The mascot must not be intentionally redesigned, replaced, recolored, restyled, have its markings or face altered, change species, or be substituted by a generative variation unless Mark explicitly unlocks the design.

## Execution Decision
Broad pre-build architecture planning is frozen enough to begin LibreOffice Calc Version 0 execution.

Implementation must follow the authoritative foundation and design-locked contracts.

A real implementation contradiction returns to planning before locked business logic changes.

## Next Formal Project Movement
📊 Calc Version 0 workbook shell and first build milestone.

## Core Operating Principle
> **Enter once. Understand everywhere.**
