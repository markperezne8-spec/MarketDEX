from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


TodaysTop3State = Literal['ready', 'unavailable', 'partial', 'error']
TodaysTop3Rank = Literal[1, 2, 3]

TODAYS_TOP3_RANK_ORDER: tuple[TodaysTop3Rank, ...] = (1, 2, 3)

UNAVAILABLE_TEXT = 'Evidence unavailable.'
UNAVAILABLE_AREA = 'Unassigned'
UNAVAILABLE_PREPARATION = 'No safe local preparation available.'


@dataclass(frozen=True, slots=True)
class TodaysTop3Evidence:
    rank: TodaysTop3Rank
    state: TodaysTop3State
    title: str
    reason: str
    evidence_summary: str
    affected_area: str
    next_safe_preparation: str


@dataclass(frozen=True, slots=True)
class TodaysTop3ViewModel:
    state: TodaysTop3State
    headline: str
    items: tuple[TodaysTop3Evidence, ...]
    error_text: str | None = None


def build_todays_top3_view_model(
    *,
    evidence: tuple[TodaysTop3Evidence, ...] = (),
    error_text: str | None = None,
) -> TodaysTop3ViewModel:
    _validate_evidence_tuple(evidence)
    _validate_error_text(error_text)

    evidence_by_rank = {item.rank: item for item in evidence}
    if len(evidence_by_rank) != len(evidence):
        raise ValueError('evidence must contain each Today\'s Top 3 rank at most once')

    ordered_items = tuple(
        evidence_by_rank.get(rank) or _unavailable_item(rank)
        for rank in TODAYS_TOP3_RANK_ORDER
    )

    if error_text is not None:
        return TodaysTop3ViewModel(
            state='error',
            headline='Today\'s Top 3 unavailable',
            items=ordered_items,
            error_text=error_text,
        )

    if not evidence:
        return TodaysTop3ViewModel(
            state='unavailable',
            headline='Today\'s Top 3 unavailable',
            items=ordered_items,
        )

    if any(item.state in ('unavailable', 'partial', 'error') for item in ordered_items):
        return TodaysTop3ViewModel(
            state='partial',
            headline='Today\'s Top 3 partially available',
            items=ordered_items,
        )

    return TodaysTop3ViewModel(
        state='ready',
        headline='Today\'s Top 3 ready',
        items=ordered_items,
    )


def todays_top3_evidence(
    rank: TodaysTop3Rank,
    *,
    state: TodaysTop3State,
    title: str,
    reason: str,
    evidence_summary: str,
    affected_area: str,
    next_safe_preparation: str,
) -> TodaysTop3Evidence:
    if rank not in TODAYS_TOP3_RANK_ORDER:
        raise ValueError('rank must be 1, 2, or 3')
    _validate_state(state)
    _validate_text(title, 'title')
    _validate_text(reason, 'reason')
    _validate_text(evidence_summary, 'evidence_summary')
    _validate_text(affected_area, 'affected_area')
    _validate_text(next_safe_preparation, 'next_safe_preparation')
    return TodaysTop3Evidence(
        rank=rank,
        state=state,
        title=title,
        reason=reason,
        evidence_summary=evidence_summary,
        affected_area=affected_area,
        next_safe_preparation=next_safe_preparation,
    )


def _unavailable_item(rank: TodaysTop3Rank) -> TodaysTop3Evidence:
    return TodaysTop3Evidence(
        rank=rank,
        state='unavailable',
        title=f'Priority {rank} unavailable',
        reason=UNAVAILABLE_TEXT,
        evidence_summary=UNAVAILABLE_TEXT,
        affected_area=UNAVAILABLE_AREA,
        next_safe_preparation=UNAVAILABLE_PREPARATION,
    )


def _validate_evidence_tuple(evidence: tuple[TodaysTop3Evidence, ...]) -> None:
    if not isinstance(evidence, tuple) or any(
        not isinstance(item, TodaysTop3Evidence) for item in evidence
    ):
        raise TypeError('evidence must be a tuple of TodaysTop3Evidence values')
    for item in evidence:
        if item.rank not in TODAYS_TOP3_RANK_ORDER:
            raise ValueError('evidence contains an unsupported rank')
        _validate_state(item.state)
        _validate_text(item.title, 'title')
        _validate_text(item.reason, 'reason')
        _validate_text(item.evidence_summary, 'evidence_summary')
        _validate_text(item.affected_area, 'affected_area')
        _validate_text(item.next_safe_preparation, 'next_safe_preparation')


def _validate_error_text(error_text: str | None) -> None:
    if error_text is not None:
        _validate_text(error_text, 'error_text')


def _validate_state(state: str) -> None:
    if state not in ('ready', 'unavailable', 'partial', 'error'):
        raise ValueError('state must be ready, unavailable, partial, or error')


def _validate_text(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{field_name} must be non-empty text')
