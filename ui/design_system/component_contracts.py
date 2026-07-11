from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ComponentState(str, Enum):
    DEFAULT = "default"
    HOVER = "hover"
    PRESSED = "pressed"
    FOCUSED = "focused"
    SELECTED = "selected"
    DISABLED = "disabled"
    LOADING = "loading"
    EMPTY = "empty"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    INSUFFICIENT_DATA = "insufficient-data"


@dataclass(frozen=True)
class ComponentDefinition:
    component_id: str
    display_name: str
    purpose: str
    required_states: tuple[ComponentState, ...]
    keyboard_requirement: str
    accessibility_requirement: str
    data_requirement: str = "No authoritative data required"
    mascot_policy: str = "Mascot not used"

    def validate(self) -> None:
        if not self.component_id or self.component_id != self.component_id.lower():
            raise ValueError(f"Invalid component id: {self.component_id!r}")
        if " " in self.component_id:
            raise ValueError(f"Component id cannot contain spaces: {self.component_id}")
        if len(set(self.required_states)) != len(self.required_states):
            raise ValueError(f"Duplicate states for component: {self.component_id}")
        if ComponentState.DEFAULT not in self.required_states:
            raise ValueError(f"Default state missing: {self.component_id}")
        if not self.keyboard_requirement.strip():
            raise ValueError(f"Keyboard requirement missing: {self.component_id}")
        if not self.accessibility_requirement.strip():
            raise ValueError(f"Accessibility requirement missing: {self.component_id}")


_INTERACTIVE_STATES = (
    ComponentState.DEFAULT,
    ComponentState.HOVER,
    ComponentState.PRESSED,
    ComponentState.FOCUSED,
    ComponentState.DISABLED,
)

_DATA_STATES = (
    ComponentState.DEFAULT,
    ComponentState.LOADING,
    ComponentState.EMPTY,
    ComponentState.INSUFFICIENT_DATA,
    ComponentState.ERROR,
)

_FEEDBACK_STATES = (
    ComponentState.DEFAULT,
    ComponentState.SUCCESS,
    ComponentState.WARNING,
    ComponentState.ERROR,
)


def build_component_catalog() -> tuple[ComponentDefinition, ...]:
    """Return the first reusable component contract catalog.

    The catalog defines shared behavior and review obligations before concrete
    PySide widgets are implemented. Pages should compose these components rather
    than inventing unrelated visual or interaction rules.
    """

    components = (
        ComponentDefinition(
            "application-shell",
            "Application Shell",
            "Permanent frame for branding, global navigation, status, workspace, and assistant access.",
            (ComponentState.DEFAULT, ComponentState.LOADING, ComponentState.ERROR),
            "Global shortcuts and focus traversal must remain available.",
            "Landmarks, active workspace, global status, and assistant access are named.",
            mascot_policy="Compact brand treatment only; never obstruct the workspace.",
        ),
        ComponentDefinition(
            "navigation-item",
            "Navigation Item",
            "Open one canonical workspace and communicate active state.",
            _INTERACTIVE_STATES + (ComponentState.SELECTED,),
            "Arrow-key or tab navigation plus Enter/Space activation.",
            "Accessible name, icon description where needed, and non-color-only active state.",
        ),
        ComponentDefinition(
            "workspace-header",
            "Workspace Header",
            "Identify the current workspace, mode, context, and primary action.",
            (ComponentState.DEFAULT, ComponentState.LOADING, ComponentState.ERROR),
            "Primary action and context controls are reachable in logical order.",
            "Heading hierarchy and current context are announced clearly.",
        ),
        ComponentDefinition(
            "kpi-card",
            "KPI Card",
            "Present one important value, comparison, evidence state, and drill-down.",
            _DATA_STATES + (ComponentState.SUCCESS, ComponentState.WARNING),
            "Drill-down is keyboard activatable when interactive.",
            "Value, unit, period, direction, and evidence state have accessible text.",
            "Requires metric owner, calculation version, period, freshness, and source classification.",
        ),
        ComponentDefinition(
            "dashboard-panel",
            "Dashboard Panel",
            "Reusable container for a business question, summary, evidence, and drill-down.",
            _DATA_STATES,
            "Panel controls follow heading then filters then content then actions.",
            "Panel purpose, loading, empty, error, and evidence states are announced.",
            "Requires one business question and one authoritative read model.",
        ),
        ComponentDefinition(
            "status-badge",
            "Status Badge",
            "Communicate concise health, freshness, confidence, or lifecycle status.",
            _FEEDBACK_STATES + (ComponentState.DISABLED,),
            "Non-interactive unless paired with an explicit details action.",
            "Text or symbol communicates meaning without relying on color.",
        ),
        ComponentDefinition(
            "attention-row",
            "Needs Attention Row",
            "Explain one ranked risk, opportunity, blocker, or stale-evidence condition.",
            _INTERACTIVE_STATES + (
                ComponentState.SUCCESS,
                ComponentState.WARNING,
                ComponentState.ERROR,
            ),
            "Open, snooze, and dismiss actions are separately keyboard reachable.",
            "Severity, reason, confidence, freshness, and action are available as text.",
            "Requires an explainable Attention Engine signal and evidence references.",
        ),
        ComponentDefinition(
            "opportunity-card",
            "Opportunity Card",
            "Summarize an evidence-supported opportunity without implying certainty.",
            _DATA_STATES + (ComponentState.SUCCESS, ComponentState.WARNING),
            "Open evidence and action controls are keyboard reachable.",
            "Reason, assumptions, confidence, freshness, and downside are readable.",
            "Requires source-attributed observations and an approved policy/rule version.",
        ),
        ComponentDefinition(
            "recommendation-card",
            "Recommendation Card",
            "Compare paths such as keep, sell, grade, open, or keep sealed.",
            _DATA_STATES + (ComponentState.WARNING,),
            "Alternative paths and evidence details are keyboard reachable.",
            "Recommendation, confidence, assumptions, risk, and user control are explicit.",
            "Requires deterministic calculations plus evidence-linked assumptions.",
        ),
        ComponentDefinition(
            "chart-container",
            "Chart Container",
            "Render a reusable visualization with range, freshness, explanation, and fallback text.",
            _DATA_STATES,
            "Range and series controls are keyboard operable; a text/table alternative is reachable.",
            "Chart has an accessible summary, units, period, series names, and supporting table.",
            "Requires a metric owner, business question, source coverage, period, and drill-down.",
        ),
        ComponentDefinition(
            "data-table",
            "Data Table",
            "Present authoritative rows with sorting, filtering, selection, and evidence access.",
            _DATA_STATES + (ComponentState.SELECTED,),
            "Cell, row, sort, filter, and action navigation follow a documented keyboard model.",
            "Headers, sort state, selected rows, values, units, and actions are named.",
            "Requires a stable row identity and serializable read model.",
        ),
        ComponentDefinition(
            "filter-bar",
            "Filter Bar",
            "Control visible data without changing authoritative records.",
            _INTERACTIVE_STATES,
            "Tab order is predictable and Clear Filters is always reachable.",
            "Active filters and result impact are announced.",
        ),
        ComponentDefinition(
            "search-control",
            "Search Control",
            "Find products, owned items, workspaces, commands, or evidence within declared scope.",
            _INTERACTIVE_STATES + (ComponentState.LOADING, ComponentState.EMPTY),
            "Supports focus shortcut, arrows through results, Enter selection, and Escape close.",
            "Scope, result count, highlighted result, and no-results state are announced.",
        ),
        ComponentDefinition(
            "segmented-control",
            "Segmented Control",
            "Select one mutually exclusive view, metric, or time-range option.",
            _INTERACTIVE_STATES + (ComponentState.SELECTED,),
            "Arrow keys move selection and focus behavior follows desktop conventions.",
            "Group label and selected option are exposed.",
        ),
        ComponentDefinition(
            "primary-button",
            "Primary Button",
            "Represent the most important safe action in the current context.",
            _INTERACTIVE_STATES + (ComponentState.LOADING,),
            "Enter/Space activation with no duplicate submission while loading.",
            "Purpose, busy state, and resulting confirmation are announced.",
        ),
        ComponentDefinition(
            "secondary-button",
            "Secondary Button",
            "Represent a supporting or alternative action.",
            _INTERACTIVE_STATES + (ComponentState.LOADING,),
            "Enter/Space activation and visible focus.",
            "Purpose and disabled reason are available.",
        ),
        ComponentDefinition(
            "mode-selector",
            "Business / Collector Mode Selector",
            "Change presentation emphasis without duplicating or mutating source data.",
            _INTERACTIVE_STATES + (ComponentState.SELECTED,),
            "Arrow or tab navigation plus explicit activation.",
            "Current mode and effect on presentation are described.",
        ),
        ComponentDefinition(
            "empty-state",
            "Empty State",
            "Explain why content is absent and provide one safe next step.",
            (ComponentState.DEFAULT, ComponentState.EMPTY),
            "Primary recovery or creation action is keyboard reachable.",
            "Reason, scope, and next action are clear.",
            mascot_policy="Allowed when warmth or onboarding improves comprehension; use once.",
        ),
        ComponentDefinition(
            "loading-state",
            "Loading State",
            "Communicate background work without freezing the entire workspace.",
            (ComponentState.DEFAULT, ComponentState.LOADING, ComponentState.ERROR),
            "Cancel action is reachable when cancellation is safe.",
            "Current task, progress when known, and status changes are announced.",
            mascot_policy="Allowed for meaningful processing moments; motion must respect reduced-motion settings.",
        ),
        ComponentDefinition(
            "error-state",
            "Error State",
            "Explain a failure, preserve user data, and provide recovery or diagnostics.",
            (ComponentState.DEFAULT, ComponentState.ERROR),
            "Retry, details, copy diagnostics, and close actions are reachable.",
            "Failure, affected scope, data-safety status, and recovery options are clear.",
        ),
        ComponentDefinition(
            "confirmation-dialog",
            "Confirmation Dialog",
            "Guard destructive, external, irreversible, or high-impact actions.",
            _INTERACTIVE_STATES + (ComponentState.ERROR,),
            "Focus is trapped, Escape follows policy, and the safe action receives initial emphasis.",
            "Action, consequence, affected records, and cancellation path are explicit.",
        ),
        ComponentDefinition(
            "detail-drawer",
            "Detail Drawer",
            "Reveal evidence and supporting detail without losing workspace context.",
            _DATA_STATES,
            "Focus enters and returns predictably; Escape closes when safe.",
            "Drawer title, relationship to selected item, and close action are named.",
        ),
        ComponentDefinition(
            "mascot-guidance-panel",
            "Mascot Guidance Panel",
            "Provide optional contextual guidance using the permanent MarketDEX mascot.",
            (ComponentState.DEFAULT, ComponentState.LOADING, ComponentState.SUCCESS),
            "Dismiss, learn-more, and assistant actions are keyboard reachable.",
            "Guidance is available as text and is never conveyed only by the image.",
            mascot_policy="Must use only the canonical mascot asset and remain dismissible/non-obstructive.",
        ),
        ComponentDefinition(
            "assistant-launcher",
            "Assistant Launcher",
            "Open the controlled MarketDEX assistant experience.",
            _INTERACTIVE_STATES + (ComponentState.LOADING, ComponentState.ERROR),
            "Global shortcut and button activation are supported.",
            "Availability, permissions, connection state, and unread attention are described.",
            mascot_policy="Compact canonical mascot or lightning identity is allowed.",
        ),
        ComponentDefinition(
            "progress-card",
            "Progress / Achievement Card",
            "Show optional meaningful progress, level, badge, quest, or milestone status.",
            _DATA_STATES + (ComponentState.SUCCESS,),
            "Details and opt-out settings are keyboard reachable.",
            "Progress value, goal, basis, reward meaning, and optional nature are explicit.",
            "Requires authoritative activity; no superficial or transaction-pressure scoring.",
        ),
    )

    identifiers: set[str] = set()
    for component in components:
        component.validate()
        if component.component_id in identifiers:
            raise ValueError(f"Duplicate component id: {component.component_id}")
        identifiers.add(component.component_id)

    return components
