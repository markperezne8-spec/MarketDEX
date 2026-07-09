# MarketDEX Release Candidate Checkpoint

## Purpose

Define the final offline-first desktop release-candidate checkpoint after the operator workflow and runtime-data preservation boundaries are complete.

## Required gates

A MarketDEX release candidate is eligible for operator verification only when all five permanent CI jobs pass:

1. Core Tests
2. Inventory
3. Pricing
4. Listing
5. Desktop Build

## Desktop workflow regression

The release candidate must preserve the completed operator chain:

Inventory → Business Details → Unit Cost → Sale Readiness → Fee-aware True Profit → Price Guidance → Listing Decision Workspace → Saved Listing Plan → Listing Plan Queue → Listing Execution Readiness → Marketplace Listing Preparation → Marketplace Listing Package Review → Persisted Listing Review State → Completion Tracking → Completed Listing Package Queue → Operator Handoff → Operator-Recorded LISTED Outcome → Listing Execution History → Confirmed Sale Evidence → Authoritative Sale Completion → Controlled SOLD Conversion → Sale History.

## Runtime data safety

Startup must preserve an existing non-empty operator database. Legacy inventory seeding is allowed only when the runtime database is missing or empty.

## Packaging readiness

The Windows desktop entry point must compile under Python 3.12 in the Desktop Build gate. A release artifact is not authoritative merely because it exists; it must be produced from a commit that satisfies the five permanent CI gates.

## Release authority

The operator remains authoritative for marketplace actions, LISTED outcomes, confirmed sale evidence, and SOLD conversion. MarketDEX does not poll marketplaces, infer sales, or mutate remote marketplace state.

## Checkpoint result

When the five CI gates are green and the Windows package launches against preserved runtime data, the commit may be marked as the verified MarketDEX release-candidate checkpoint.
