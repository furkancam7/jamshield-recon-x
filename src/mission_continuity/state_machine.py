"""State manager for deterministic mission continuity."""

from __future__ import annotations

from dataclasses import dataclass, field

from common.config import MissionConfig
from common.enums import MissionState

from .decision_policy import (
    MISSION_STATE_SEVERITY,
    MissionCandidateDecision,
    decide_candidate_mission_state,
)


@dataclass(frozen=True)
class MissionDecision:
    tick_index: int
    candidate_state: MissionState
    final_state: MissionState
    primary_reason_code: str
    reason_codes: tuple[str, ...]
    transition_count: int


@dataclass
class MissionStateMachine:
    config: MissionConfig
    current_state: MissionState = MissionState.MISSION_EXECUTE
    tick_index: int = -1
    transition_count: int = 0
    _recovery_streak: int = 0
    _safe_hold_streak: int = 0
    _transition_ticks: list[int] = field(default_factory=list)

    def update(
        self,
        mission_confidence: float,
        gnss_state: str,
        effective_vio_state: str,
    ) -> MissionDecision:
        self.tick_index += 1
        candidate = decide_candidate_mission_state(
            mission_confidence=mission_confidence,
            gnss_state=gnss_state,
            effective_vio_state=effective_vio_state,
            config=self.config,
        )

        if self.current_state == MissionState.MISSION_ABORT:
            return self._commit(
                candidate=candidate,
                final_state=MissionState.MISSION_ABORT,
                primary_reason_code="mission_abort_terminal_latched",
                reason_codes=_compose_reason_codes(
                    "mission_abort_terminal_latched",
                    candidate.primary_reason_code,
                ),
            )

        proposed_state, primary_reason_code, reason_codes = self._apply_stateful_guards(
            candidate
        )

        if proposed_state != MissionState.MISSION_ABORT and self._would_exceed_oscillation_limit(
            proposed_state
        ):
            proposed_state = MissionState.MISSION_SAFE_HOLD
            primary_reason_code = "mission_state_oscillation_detected"
            reason_codes = _compose_reason_codes(
                "mission_state_oscillation_detected",
                candidate.primary_reason_code,
            )

        return self._commit(
            candidate=candidate,
            final_state=proposed_state,
            primary_reason_code=primary_reason_code,
            reason_codes=reason_codes,
        )

    def _apply_stateful_guards(
        self,
        candidate: MissionCandidateDecision,
    ) -> tuple[MissionState, str, tuple[str, ...]]:
        candidate_severity = MISSION_STATE_SEVERITY[candidate.candidate_state]
        current_severity = MISSION_STATE_SEVERITY[self.current_state]

        proposed_state = candidate.candidate_state
        primary_reason_code = candidate.primary_reason_code
        reason_codes = candidate.reason_codes

        if candidate_severity > current_severity:
            self._recovery_streak = 0
        elif candidate_severity < current_severity:
            self._recovery_streak += 1
            if self._recovery_streak < self.config.recovery_dwell_ticks:
                proposed_state = self.current_state
                primary_reason_code = "mission_recovery_dwell_active"
                reason_codes = _compose_reason_codes(
                    "mission_recovery_dwell_active",
                    candidate.primary_reason_code,
                )
            else:
                self._recovery_streak = 0
        else:
            self._recovery_streak = 0

        if (
            proposed_state == MissionState.MISSION_SAFE_HOLD
            and primary_reason_code != "mission_recovery_dwell_active"
        ):
            self._safe_hold_streak += 1
        else:
            self._safe_hold_streak = 0

        if (
            proposed_state == MissionState.MISSION_SAFE_HOLD
            and self._safe_hold_streak >= self.config.safe_hold_escalation_ticks
        ):
            proposed_state = MissionState.MISSION_ABORT
            primary_reason_code = "mission_abort_safe_hold_timeout"
            reason_codes = _compose_reason_codes(
                "mission_abort_safe_hold_timeout",
                candidate.primary_reason_code,
            )
            self._safe_hold_streak = 0

        return proposed_state, primary_reason_code, reason_codes

    def _would_exceed_oscillation_limit(self, proposed_state: MissionState) -> bool:
        if proposed_state == self.current_state:
            return False

        prospective_ticks = [*self._transition_ticks, self.tick_index]
        lower_bound = self.tick_index - self.config.oscillation_window_ticks + 1
        transitions_in_window = sum(
            1 for tick in prospective_ticks if tick >= lower_bound
        )
        return transitions_in_window > self.config.max_state_transitions_in_window

    def _commit(
        self,
        candidate: MissionCandidateDecision,
        final_state: MissionState,
        primary_reason_code: str,
        reason_codes: tuple[str, ...],
    ) -> MissionDecision:
        if final_state != self.current_state:
            self.transition_count += 1
            self._transition_ticks.append(self.tick_index)

        self.current_state = final_state
        return MissionDecision(
            tick_index=self.tick_index,
            candidate_state=candidate.candidate_state,
            final_state=final_state,
            primary_reason_code=primary_reason_code,
            reason_codes=reason_codes,
            transition_count=self.transition_count,
        )


def _compose_reason_codes(primary_reason_code: str, *secondary_codes: str) -> tuple[str, ...]:
    ordered: list[str] = []
    for code in (primary_reason_code, *secondary_codes):
        if code and code not in ordered:
            ordered.append(code)
    return tuple(ordered)
