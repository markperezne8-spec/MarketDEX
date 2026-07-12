from __future__ import annotations

from enum import Enum
from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class StatusTone(str, Enum):
    INFORMATION = "information"
    POSITIVE = "positive"
    WARNING = "warning"
    NEGATIVE = "negative"
    COLLECTION = "collection"


class ComparisonDirection(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


def _refresh_style(widget: QWidget) -> None:
    style = widget.style()
    style.unpolish(widget)
    style.polish(widget)
    widget.update()


class MarketDEXStatusBadge(QLabel):
    """Compact text-first status indicator with non-color-only meaning."""

    def __init__(
        self,
        text: str,
        tone: StatusTone = StatusTone.INFORMATION,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(text, parent)
        self.setObjectName("marketdexStatusBadge")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        self.set_tone(tone)
        self.setAccessibleName(f"Status: {text}")

    def set_tone(self, tone: StatusTone) -> None:
        self.setProperty("tone", tone.value)
        _refresh_style(self)

    def set_status(self, text: str, tone: StatusTone) -> None:
        self.setText(text)
        self.setAccessibleName(f"Status: {text}")
        self.set_tone(tone)


class MarketDEXWorkspaceHeader(QFrame):
    """Reusable workspace identity, context, and primary-action header."""

    def __init__(
        self,
        title: str,
        subtitle: str = "",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("marketdexWorkspaceHeader")
        self.setAccessibleName(f"{title} workspace header")

        root = QHBoxLayout(self)
        root.setContentsMargins(16, 14, 16, 14)
        root.setSpacing(12)

        copy_layout = QVBoxLayout()
        copy_layout.setSpacing(3)

        self.title_label = QLabel(title, self)
        self.title_label.setObjectName("marketdexWorkspaceTitle")
        self.title_label.setAccessibleName(f"Workspace: {title}")

        self.subtitle_label = QLabel(subtitle, self)
        self.subtitle_label.setObjectName("marketdexWorkspaceSubtitle")
        self.subtitle_label.setWordWrap(True)

        copy_layout.addWidget(self.title_label)
        copy_layout.addWidget(self.subtitle_label)
        root.addLayout(copy_layout, 1)

        self.context_layout = QHBoxLayout()
        self.context_layout.setSpacing(8)
        root.addLayout(self.context_layout)

        self.action_layout = QHBoxLayout()
        self.action_layout.setSpacing(8)
        root.addLayout(self.action_layout)

    def set_title(self, title: str) -> None:
        self.title_label.setText(title)
        self.title_label.setAccessibleName(f"Workspace: {title}")
        self.setAccessibleName(f"{title} workspace header")

    def set_subtitle(self, subtitle: str) -> None:
        self.subtitle_label.setText(subtitle)
        self.subtitle_label.setVisible(bool(subtitle.strip()))

    def add_context_widget(self, widget: QWidget) -> None:
        self.context_layout.addWidget(widget)

    def add_action_widget(self, widget: QWidget) -> None:
        self.action_layout.addWidget(widget)


class MarketDEXKpiCard(QFrame):
    """One important metric with comparison, evidence, and drill-down support."""

    def __init__(
        self,
        label: str,
        value: str = "—",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("marketdexKpiCard")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(4)

        self.label_widget = QLabel(label, self)
        self.label_widget.setObjectName("marketdexKpiLabel")

        self.value_widget = QLabel(value, self)
        self.value_widget.setObjectName("marketdexKpiValue")

        self.comparison_widget = QLabel("", self)
        self.comparison_widget.setObjectName("marketdexKpiComparison")
        self.comparison_widget.setProperty("direction", ComparisonDirection.NEUTRAL.value)

        self.evidence_widget = QLabel("", self)
        self.evidence_widget.setObjectName("marketdexKpiEvidence")
        self.evidence_widget.setWordWrap(True)

        layout.addWidget(self.label_widget)
        layout.addWidget(self.value_widget)
        layout.addWidget(self.comparison_widget)
        layout.addWidget(self.evidence_widget)

        self._update_accessible_name()

    def set_value(self, value: str) -> None:
        self.value_widget.setText(value)
        self._update_accessible_name()

    def set_comparison(
        self,
        text: str,
        direction: ComparisonDirection = ComparisonDirection.NEUTRAL,
    ) -> None:
        self.comparison_widget.setText(text)
        self.comparison_widget.setVisible(bool(text.strip()))
        self.comparison_widget.setProperty("direction", direction.value)
        _refresh_style(self.comparison_widget)
        self._update_accessible_name()

    def set_evidence(self, text: str) -> None:
        self.evidence_widget.setText(text)
        self.evidence_widget.setVisible(bool(text.strip()))
        self._update_accessible_name()

    def _update_accessible_name(self) -> None:
        parts = [self.label_widget.text(), self.value_widget.text()]
        if self.comparison_widget.text().strip():
            parts.append(self.comparison_widget.text())
        if self.evidence_widget.text().strip():
            parts.append(self.evidence_widget.text())
        self.setAccessibleName(". ".join(parts))


class MarketDEXDashboardPanel(QFrame):
    """Reusable container for one business question and its evidence surface."""

    def __init__(
        self,
        title: str,
        description: str = "",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("marketdexDashboardPanel")
        self.setAccessibleName(f"Panel: {title}")

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 10, 12, 12)
        root.setSpacing(8)

        header = QHBoxLayout()
        header.setSpacing(8)

        copy_layout = QVBoxLayout()
        copy_layout.setSpacing(2)

        self.title_label = QLabel(title, self)
        self.title_label.setObjectName("marketdexPanelTitle")

        self.description_label = QLabel(description, self)
        self.description_label.setObjectName("marketdexPanelDescription")
        self.description_label.setWordWrap(True)
        self.description_label.setVisible(bool(description.strip()))

        copy_layout.addWidget(self.title_label)
        copy_layout.addWidget(self.description_label)
        header.addLayout(copy_layout, 1)

        self.header_actions = QHBoxLayout()
        self.header_actions.setSpacing(6)
        header.addLayout(self.header_actions)

        root.addLayout(header)

        self.content_widget = QWidget(self)
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(8)
        root.addWidget(self.content_widget, 1)

    def add_header_action(self, widget: QWidget) -> None:
        self.header_actions.addWidget(widget)

    def add_content_widget(self, widget: QWidget, stretch: int = 0) -> None:
        self.content_layout.addWidget(widget, stretch)

    def set_description(self, description: str) -> None:
        self.description_label.setText(description)
        self.description_label.setVisible(bool(description.strip()))


class MarketDEXStatePanel(QFrame):
    """Shared empty, loading, success, warning, and error presentation."""

    def __init__(
        self,
        title: str,
        detail: str,
        tone: StatusTone = StatusTone.INFORMATION,
        action_text: str | None = None,
        action: Callable[[], None] | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("marketdexStatePanel")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.badge = MarketDEXStatusBadge(tone.value.replace("-", " ").title(), tone, self)
        self.title_label = QLabel(title, self)
        self.title_label.setObjectName("marketdexPanelTitle")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.detail_label = QLabel(detail, self)
        self.detail_label.setObjectName("marketdexStateDetail")
        self.detail_label.setWordWrap(True)
        self.detail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.badge, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)
        layout.addWidget(self.detail_label)

        self.action_button: QPushButton | None = None
        if action_text:
            self.action_button = QPushButton(action_text, self)
            self.action_button.setObjectName("marketdexPrimaryButton")
            if action is not None:
                self.action_button.clicked.connect(action)
            layout.addWidget(self.action_button, 0, Qt.AlignmentFlag.AlignCenter)

        self.setAccessibleName(f"{title}. {detail}")
