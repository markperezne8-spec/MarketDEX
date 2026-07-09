# Workspace Tab Access Architecture

`QTabWidget` owns top-level workspace navigation. Selection state belongs to inventory workflow context and updates guided action controls only.

This separation prevents navigation authority from being coupled to transient table selection state.
