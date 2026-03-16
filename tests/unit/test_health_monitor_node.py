import json
from pathlib import Path
import unittest

from _support import make_temp_dir
from evaluation.artifact_schema import validate_fault_events, validate_mission_health_timeline
from health_monitor.service import HealthMonitorService
from runtime.node_runner import run_node_scenario


ROOT_DIR = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT_DIR / "configs" / "sim" / "default.yaml"
NOMINAL_SCENARIO = ROOT_DIR / "scenarios" / "baseline" / "s1_nominal.yaml"
SYNC_LOW_SCENARIO = ROOT_DIR / "scenarios" / "baseline" / "s13_sync_low_nominal.yaml"


class HealthMonitorNodeTests(unittest.TestCase):
    def test_health_monitor_service_nominal_tick_has_no_fault(self) -> None:
        service = HealthMonitorService(
            sync_low_threshold=0.6,
            degraded_confidence_threshold=0.5,
            abort_confidence_threshold=0.2,
        )
        assessment = service.evaluate(
            scenario_id="s1_nominal",
            tick_index=0,
            timestamp_ns=0,
            sync_quality=1.0,
            mission_confidence=0.95,
            gnss_state="nominal",
            effective_vio_state="good",
            localization_mode="GNSS_PRIMARY",
            mission_state="MISSION_EXECUTE",
        )
        self.assertEqual(assessment.health_status.severity, "nominal")
        self.assertEqual(assessment.health_status.primary_reason_code, "trust_inputs_nominal")
        self.assertEqual(assessment.health_status.reason_codes, ())
        self.assertIsNone(assessment.fault_event)

    def test_health_monitor_service_sync_low_emits_warning_fault(self) -> None:
        service = HealthMonitorService(
            sync_low_threshold=0.6,
            degraded_confidence_threshold=0.5,
            abort_confidence_threshold=0.2,
        )
        assessment = service.evaluate(
            scenario_id="s13_sync_low_nominal",
            tick_index=4,
            timestamp_ns=4_000_000_000,
            sync_quality=0.2,
            mission_confidence=0.41,
            gnss_state="nominal",
            effective_vio_state="good",
            localization_mode="BLENDED",
            mission_state="MISSION_DEGRADED",
        )
        self.assertEqual(assessment.health_status.severity, "warning")
        self.assertIn("sync_quality_low", assessment.health_status.reason_codes)
        self.assertIsNotNone(assessment.fault_event)
        assert assessment.fault_event is not None
        self.assertEqual(assessment.fault_event.severity, "warning")

    def test_node_runtime_writes_health_monitor_artifacts(self) -> None:
        run_dir = make_temp_dir(self)
        run_node_scenario(
            scenario_path=SYNC_LOW_SCENARIO,
            output_dir=run_dir,
            config_path=CONFIG_PATH,
            run_id="health-node",
        )

        health_path = run_dir / "s13_sync_low_nominal_mission_health.json"
        faults_path = run_dir / "s13_sync_low_nominal_fault_events.json"
        self.assertTrue(health_path.exists())
        self.assertTrue(faults_path.exists())

        health_payload = json.loads(health_path.read_text(encoding="utf-8"))
        fault_payload = json.loads(faults_path.read_text(encoding="utf-8"))
        validate_mission_health_timeline(health_payload)
        validate_fault_events(fault_payload)
        self.assertGreater(len(health_payload["entries"]), 0)
        self.assertGreater(len(fault_payload["events"]), 0)

    def test_node_runtime_nominal_fault_events_can_be_empty(self) -> None:
        run_dir = make_temp_dir(self)
        run_node_scenario(
            scenario_path=NOMINAL_SCENARIO,
            output_dir=run_dir,
            config_path=CONFIG_PATH,
            run_id="health-node-nominal",
        )

        faults_path = run_dir / "s1_nominal_fault_events.json"
        payload = json.loads(faults_path.read_text(encoding="utf-8"))
        validate_fault_events(payload)
        self.assertEqual(payload["events"], [])

    def test_mission_health_schema_rejects_invalid_nominal_reasoning(self) -> None:
        payload = {
            "schema_version": "1.0",
            "run_id": "run",
            "scenario_id": "s1_nominal",
            "entries": [
                {
                    "tick_index": 0,
                    "timestamp_ns": 0,
                    "subsystem": "navigation_runtime",
                    "severity": "nominal",
                    "stale_duration_ms": 0.0,
                    "primary_reason_code": "sync_quality_low",
                    "reason_codes": ["sync_quality_low"],
                }
            ],
        }
        with self.assertRaises(ValueError):
            validate_mission_health_timeline(payload)


if __name__ == "__main__":
    unittest.main()
