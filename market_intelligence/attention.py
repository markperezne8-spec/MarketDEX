from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum, StrEnum


class AttentionSeverity(IntEnum):
    INFO = 10
    OPPORTUNITY = 20
    WATCH = 30
    CRITICAL = 40


class SuggestedAction(StrEnum):
    REVIEW = 'review'
    SELL = 'sell'
    KEEP = 'keep'
    OPEN = 'open'
    KEEP_SEALED = 'keep-sealed'
    REPRICE = 'reprice'
    LIST = 'list'
    WAIT = 'wait'


@dataclass(frozen=True)
class AttentionSignal:
    signal_id: str
    subject_id: str
    severity: AttentionSeverity
    title: str
    explanation: str
    suggested_action: SuggestedAction
    confidence: float
    created_at: datetime
    evidence_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        for field_name in ('signal_id', 'subject_id', 'title', 'explanation'):
            value = getattr(self, field_name)
            if not value.strip():
                raise ValueError(f'{field_name} must not be empty')
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError('confidence must be between 0 and 1')
        if len(self.evidence_ids) != len(set(self.evidence_ids)):
            raise ValueError(f'duplicate evidence ids: {self.signal_id}')

    @property
    def priority(self) -> int:
        return int(self.severity)
