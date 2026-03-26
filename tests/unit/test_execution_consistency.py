from pathlib import Path
import unittest

from _support import make_temp_dir
from common.config import load_app_config
from gnss_trust.trust_service import GnssTrustService
from localization_fusion import LocalizationFusionService
from mission_continuity.state_machine import MissionStateMachine
from scenario_orchestrator.main import run_scenario
from scenario_orchestrator.manifest_loader import load_manifest
from scenario_orchestrator.orchestrator import ScenarioOrchestrator
from trust_engine import TrustEngineService
from vio_health.scoring import resolve_effective_vio_state


ROOT_DIR = Path(__file__).resolve().parents[2]
DENIED_SCENARIO = ROOT_DIR / "scenarios" / "baseline" / "s3_gnss_denied_zone.yaml"
NOMINAL_SCENARIO = ROOT_DIR / "scenarios" / "baseline" / "s1_nominal.yaml"
WEAK_VIO_SCENARIO = ROOT_DIR / "scenarios" / "baseline" / "s5_denied_vio_weak.yaml"
LOST_VIO_SCENARIO = ROOT_DIR / "scenarios" / "baseline" / "s6_denied_vio_lost.yaml"
CONFIG_PATH = ROOT_DIR / "configs" / "sim" / "default.yaml"


def _execute_denied_scenario(
    vio_state: str = "good", vio_health_score: float = 1.0,
) -> tuple[str, float, float, str, str]:
    config = load_app_config(CONFIG_PATH)
    manifest = load_manifest(DENIED_SCENARIO)
    snapshot = ScenarioOrchestrator(manifest).build_snapshot()
    effective_vio_state = resolve_effective_vio_state(
        vio_state=vio_state,
        vio_health_score=vio_health_score,
        config=config.vio_health,
    )
    gnss_assessment = GnssTrustService(config.gnss_trust).evaluate(snapshot)
    fusion_assessment = LocalizationFusionService(config.localization_fusion).evaluate(
        gnss_trust=gnss_assessment.gnss_trust,
        gnss_state=gnss_assessment.gnss_state,
        vio_health_score=vio_health_score,
        effective_vio_state=effective_vio_state,
    )
    trust_assessment = TrustEngineService(config.trust_engine).evaluate(
        scenario_id=snapshot.scenario_id,
        gnss_trust=gnss_assessment.gnss_trust,
        gnss_state=gnss_assessment.gnss_state,
        vio_health_score=vio_health_score,
        effective_vio_state=effective_vio_state,
        localization_confidence=fusion_assessment.localization_confidence,
        mode_stable=fusion_assessment.mode_stable,
        sync_quality=snapshot.sync_quality,
    )
    mission_decision = MissionStateMachine(config=config.mission).update(
        mission_confidence=trust_assessment.mission_confidence,
        gnss_state=trust_assessment.gnss_state,
        effective_vio_state=effective_vio_state,
    )
    return (
        trust_assessment.gnss_state,
        trust_assessment.gnss_trust,
        trust_assessment.mission_confidence,
        mission_decision.final_state.value,
        mission_decision.primary_reason_code,
    )


class ExecutionConsistencyTests(unittest.TestCase):
    def test_denied_scenario_is_deterministic_for_same_inputs(self) -> None:
        first = _execute_denied_scenario(vio_state="lost", vio_health_score=0.0)
        second = _execute_denied_scenario(vio_state="lost", vio_health_score=0.0)

        self.assertEqual(first, second)
        self.assertEqual(first[0], "denied")
        self.assertEqual(first[1], 0.05)
        self.assertEqual(first[2], 0.013)
        self.assertEqual(first[3], "MISSION_ABORT")
        self.assertEqual(first[4], "mission_abort_vio_lost")

    def test_denied_scenario_changes_when_vio_health_changes(self) -> None:
        lost = _execute_denied_scenario(vio_state="lost", vio_health_score=0.0)
        good = _execute_denied_scenario(vio_state="good", vio_health_score=1.0)

        self.assertEqual(lost[0], good[0])
        self.assertEqual(lost[1], good[1])
        self.assertNotEqual(lost[2], good[2])
        self.assertNotEqual(lost[3], good[3])
        self.assertNotEqual(lost[4], good[4])

    def test_repeated_runs_produce_equivalent_artifact_logic(self) -> None:
        first_dir = make_temp_dir(self)
        second_dir = make_temp_dir(self)
        first = run_scenario(
            scenario_path=NOMINAL_SCENARIO,
            output_dir=first_dir,
            config_path=CONFIG_PATH,
            run_id="repeatable-run",
            vio_state="good",
            vio_health_score=1.0,
        )
        second = run_scenario(
            scenario_path=NOMINAL_SCENARIO,
            output_dir=second_dir,
            config_path=CONFIG_PATH,
            run_id="repeatable-run",
            vio_state="good",
            vio_health_score=1.0,
        )

        for key in (
            "scenario_id",
            "gnss_state",
            "gnss_trust",
            "vio_trust",
            "sync_quality",
            "mission_confidence",
            "trust_primary_reason_code",
            "mission_primary_reason_code",
            "mission_transition_count",
            "ew_risk_level",
            "ew_primary_reason_code",
            "ew_max_risk",
            "ew_affected_cell_count",
            "ew_corridor_cost",
            "tactical_primary_reason_code",
            "tactical_advisory_code",
            "tactical_summary_text",
            "mission_state",
            "config_id",
            "software_revision",
        ):
            self.assertEqual(first[key], second[key])

    def test_manifest_driven_pipeline_weak_vio_preserves_safe_hold(self) -> None:
        output_dir = make_temp_dir(self)
        result = run_scenario(
            scenario_path=WEAK_VIO_SCENARIO,
            output_dir=output_dir,
            config_path=CONFIG_PATH,
        )
        self.assertEqual(result["effective_vio_state"], "weak")
        self.assertEqual(result["mission_state"], "MISSION_SAFE_HOLD")
        self.assertEqual(
            result["mission_primary_reason_code"],
            "mission_safe_hold_vio_weak",
        )

    def test_manifest_driven_pipeline_lost_vio_preserves_abort(self) -> None:
        output_dir = make_temp_dir(self)
        result = run_scenario(
            scenario_path=LOST_VIO_SCENARIO,
            output_dir=output_dir,
            config_path=CONFIG_PATH,
        )
        self.assertEqual(result["effective_vio_state"], "lost")
        self.assertEqual(result["mission_state"], "MISSION_ABORT")
        self.assertEqual(result["mission_primary_reason_code"], "mission_abort_vio_lost")


if __name__ == "__main__":
    unittest.main()
