# RC Delivery CI Note

The Windows RC Delivery workflow is intentionally manual (`workflow_dispatch`). Pull-request CI protects its delivery contract; the delivery workflow itself is invoked after merge when an operator package is required.

This prevents every pull request from publishing a new operator package while preserving a tested, repeatable delivery path.
