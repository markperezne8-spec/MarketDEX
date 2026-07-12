from dataclasses import dataclass
from enum import StrEnum


class SealedRecommendation(StrEnum):
    OPEN = 'open'
    KEEP_SEALED = 'keep-sealed'
    REVIEW = 'review'


@dataclass(frozen=True)
class SealedDecisionInput:
    sealed_market_value_minor: int
    pack_count: int
    expected_pack_value_minor: int
    sealed_selling_cost_minor: int = 0
    opening_cost_minor: int = 0
    expected_open_value_confidence: float = 0.65
    decision_buffer_percent: float = 10.0

    def __post_init__(self) -> None:
        for field_name in (
            'sealed_market_value_minor',
            'expected_pack_value_minor',
            'sealed_selling_cost_minor',
            'opening_cost_minor',
        ):
            if getattr(self, field_name) < 0:
                raise ValueError(f'{field_name} must not be negative')
        if self.pack_count <= 0:
            raise ValueError('pack_count must be greater than zero')
        if not 0.0 <= self.expected_open_value_confidence <= 1.0:
            raise ValueError('expected_open_value_confidence must be between 0 and 1')
        if self.decision_buffer_percent < 0:
            raise ValueError('decision_buffer_percent must not be negative')


@dataclass(frozen=True)
class SealedDecisionResult:
    recommendation: SealedRecommendation
    sealed_net_value_minor: int
    sealed_price_per_pack_minor: int
    expected_open_gross_minor: int
    risk_adjusted_open_value_minor: int
    difference_minor: int


def evaluate_sealed_decision(inputs: SealedDecisionInput) -> SealedDecisionResult:
    sealed_net = inputs.sealed_market_value_minor - inputs.sealed_selling_cost_minor
    sealed_price_per_pack = round(inputs.sealed_market_value_minor / inputs.pack_count)
    expected_open_gross = inputs.pack_count * inputs.expected_pack_value_minor
    risk_adjusted_open = (
        round(expected_open_gross * inputs.expected_open_value_confidence)
        - inputs.opening_cost_minor
    )
    difference = risk_adjusted_open - sealed_net
    buffer_ratio = inputs.decision_buffer_percent / 100.0

    if risk_adjusted_open >= sealed_net * (1.0 + buffer_ratio):
        recommendation = SealedRecommendation.OPEN
    elif sealed_net >= risk_adjusted_open * (1.0 + buffer_ratio):
        recommendation = SealedRecommendation.KEEP_SEALED
    else:
        recommendation = SealedRecommendation.REVIEW

    return SealedDecisionResult(
        recommendation=recommendation,
        sealed_net_value_minor=sealed_net,
        sealed_price_per_pack_minor=sealed_price_per_pack,
        expected_open_gross_minor=expected_open_gross,
        risk_adjusted_open_value_minor=risk_adjusted_open,
        difference_minor=difference,
    )
