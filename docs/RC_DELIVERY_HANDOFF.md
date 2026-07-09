# RC Delivery Handoff

The Windows RC delivery path now separates three operator concepts clearly:

`⬇️ source pull -> 📦 delivery build -> 🪟 operator package`

A source pull updates the permanent codebase. A delivery build generates and verifies the Windows executable. The operator package is downloaded and run outside the source repository.

These are separate actions and must not be presented as interchangeable.
