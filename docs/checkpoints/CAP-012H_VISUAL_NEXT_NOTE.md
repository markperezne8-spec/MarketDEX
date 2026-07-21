# CAP-012H visual-next checkpoint

After CAP-012H merges green, the next approved build must be a read-only Inventory Turnover visual slice in the desktop app.

That next build must:

- produce a visible in-app change;
- present Inventory Turnover results without adding mutation authority;
- preserve unavailable and conflict states visibly;
- use the existing design system;
- include focused UI tests and a visual check before merge.

No additional non-visual CAP-012 dependency should be inserted ahead of that visual slice without a newly documented blocking authority issue.
