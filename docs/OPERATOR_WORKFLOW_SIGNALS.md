# Operator Workflow Signals

MarketDEX engineering communication uses a small visual signal vocabulary for frictionless operator understanding.

- 🟢 safe, complete, or operator action available
- 🟡 active, pending, or verification in progress
- 🔴 blocked, failed, or action must not be taken
- 🔧 repair work
- 📦 packaging or delivery
- 👁️ visual/operator verification
- 🚀 next workflow boundary
- ⬇️ pull checkpoint

Pull discipline: issue `🟢 PULL NOW` only after `main` has genuinely advanced to a merged commit the operator does not yet have. Otherwise state `⬇️ NO PULL`.

Generated executables remain outside the source repository. Operator delivery packages are downloaded, extracted, and launched separately from the Git working tree.
