# Windows RC Delivery Checklist

- 🟢 Source authority stays in Git.
- 📦 Run `Windows RC Delivery` manually when an operator package is required.
- 🪟 Confirm the workflow verifies `MarketDEX.exe` before staging delivery.
- 📄 Download `MarketDEX-Windows-RC-Operator-Package` from the workflow run.
- 📁 Extract the package outside the source repository.
- 🚀 Launch `MarketDEX.exe`.
- 👁️ Confirm the first MarketDEX window opens successfully.
- 🔴 Never commit the generated executable into the source repository.
