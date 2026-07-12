from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Iterable

from market_intelligence.attention import AttentionSeverity, AttentionSignal, SuggestedAction
from market_intelligence.observations import MarketObservation, ObservationKind


@dataclass(frozen=True)
class AttentionSignalPolicy:
    """Provider-neutral thresholds for read-only market attention derivation."""

    minimum_confidence: float = 0.65
    stale_hours: int = 72
    supply_pressure_ratio: Decimal = Decimal('1.5')
    volume_opportunity_ratio: Decimal = Decimal('1.25')

    def __post_init__(self) -> None:
        if not 0.0 <= self.minimum_confidence <= 1.0:
            raise ValueError('minimum_confidence must be between 0 and 1')
        if self.stale_hours < 1:
            raise ValueError('stale_hours must be positive')
        if self.supply_pressure_ratio <= 0:
            raise ValueError('supply_pressure_ratio must be positive')
        if self.volume_opportunity_ratio <= 0:
            raise ValueError('volume_opportunity_ratio must be positive')


class MarketAttentionSignalService:
    """Derives read-only attention signals from normalized market observations."""

    def __init__(self, policy: AttentionSignalPolicy | None = None) -> None:
        self.policy = policy or AttentionSignalPolicy()

    def derive_signals(
        self,
        observations: Iterable[MarketObservation],
        *,
        now: datetime | None = None,
    ) -> tuple[AttentionSignal, ...]:
        evidence = tuple(observations)
        if not evidence:
            return ()
        self._validate_unique_evidence(evidence)
        trusted = tuple(
            item for item in evidence if item.confidence >= self.policy.minimum_confidence
        )
        if not trusted:
            return ()
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None:
            raise TypeError('now must be timezone-aware')
        signals = [
            *self._stale_data_signals(trusted, timestamp),
            *self._supply_pressure_signals(trusted, timestamp),
            *self._volume_opportunity_signals(trusted, timestamp),
        ]
        return tuple(sorted(signals, key=lambda item: (-item.priority, item.signal_id)))

    def _validate_unique_evidence(self, observations: tuple[MarketObservation, ...]) -> None:
        ids = [item.observation_id for item in observations]
        if len(ids) != len(set(ids)):
            raise ValueError('duplicate market observation evidence ids')

    def _stale_data_signals(
        self,
        observations: tuple[MarketObservation, ...],
        now: datetime,
    ) -> tuple[AttentionSignal, ...]:
        latest_by_product: dict[str, MarketObservation] = {}
        for observation in observations:
            existing = latest_by_product.get(observation.product_id)
            if existing is None or observation.observed_at > existing.observed_at:
                latest_by_product[observation.product_id] = observation
        signals: list[AttentionSignal] = []
        for product_id, observation in latest_by_product.items():
            age_hours = (now - observation.observed_at).total_seconds() / 3600
            if age_hours >= self.policy.stale_hours:
                signals.append(
                    AttentionSignal(
                        signal_id=f'market-stale-{product_id}',
                        subject_id=product_id,
                        severity=AttentionSeverity.INFO,
                        title='Market data may be stale',
                        explanation='Latest trusted market observation is outside the configured freshness window.',
                        suggested_action=SuggestedAction.REVIEW,
                        confidence=observation.confidence,
                        created_at=now,
                        evidence_ids=(observation.observation_id,),
                    )
                )
        return tuple(signals)

    def _supply_pressure_signals(
        self,
        observations: tuple[MarketObservation, ...],
        now: datetime,
    ) -> tuple[AttentionSignal, ...]:
        by_product = self._group_by_product(observations)
        signals: list[AttentionSignal] = []
        for product_id, items in by_product.items():
            supply = self._latest(items, ObservationKind.SUPPLY)
            active = self._latest(items, ObservationKind.ACTIVE_LISTING)
            if supply is None or active is None or active.value <= 0:
                continue
            ratio = supply.value / active.value
            if ratio >= self.policy.supply_pressure_ratio:
                signals.append(
                    AttentionSignal(
                        signal_id=f'market-supply-pressure-{product_id}',
                        subject_id=product_id,
                        severity=AttentionSeverity.WATCH,
                        title='Supply pressure increased',
                        explanation='Trusted supply evidence is elevated compared with active listing evidence.',
                        suggested_action=SuggestedAction.REVIEW,
                        confidence=min(supply.confidence, active.confidence),
                        created_at=now,
                        evidence_ids=(supply.observation_id, active.observation_id),
                    )
                )
        return tuple(signals)

    def _volume_opportunity_signals(
        self,
        observations: tuple[MarketObservation, ...],
        now: datetime,
    ) -> tuple[AttentionSignal, ...]:
        by_product = self._group_by_product(observations)
        signals: list[AttentionSignal] = []
        for product_id, items in by_product.items():
            volume = self._latest(items, ObservationKind.DAILY_VOLUME)
            active = self._latest(items, ObservationKind.ACTIVE_LISTING)
            if volume is None or active is None or active.value <= 0:
                continue
            ratio = volume.value / active.value
            if ratio >= self.policy.volume_opportunity_ratio:
                signals.append(
                    AttentionSignal(
                        signal_id=f'market-volume-opportunity-{product_id}',
                        subject_id=product_id,
                        severity=AttentionSeverity.OPPORTUNITY,
                        title='Demand signal increased',
                        explanation='Trusted daily volume is elevated compared with active listing evidence.',
                        suggested_action=SuggestedAction.REVIEW,
                        confidence=min(volume.confidence, active.confidence),
                        created_at=now,
                        evidence_ids=(volume.observation_id, active.observation_id),
                    )
                )
        return tuple(signals)

    def _group_by_product(
        self,
        observations: tuple[MarketObservation, ...],
    ) -> dict[str, tuple[MarketObservation, ...]]:
        grouped: dict[str, list[MarketObservation]] = {}
        for observation in observations:
            grouped.setdefault(observation.product_id, []).append(observation)
        return {key: tuple(value) for key, value in grouped.items()}

    def _latest(
        self,
        observations: tuple[MarketObservation, ...],
        kind: ObservationKind,
    ) -> MarketObservation | None:
        matches = [item for item in observations if item.kind is kind]
        if not matches:
            return None
        return sorted(matches, key=lambda item: (item.observed_at, item.observation_id))[-1]


def build_market_attention_signal_service() -> MarketAttentionSignalService:
    return MarketAttentionSignalService()
