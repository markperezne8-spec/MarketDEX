# Workspace Tab Access CI Repair

Follow-up after PR #88 merge: legacy viewport tests still asserted the removed tab-lock behavior, and Desktop Build referenced a temporary regression file. The viewport tests now directly assert that Pricing and Listing Workflow remain openable without inventory selection, and Desktop Build runs the consolidated viewport regression suite.
