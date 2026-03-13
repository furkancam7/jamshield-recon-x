import unittest

from common.config import load_app_config
from ew_risk_map import EwRiskMapService, EwRiskTickInput, build_grid_bounds, interpolate_route_position
from scenario_orchestrator.manifest_loader import Position3D, ScenarioManifest


class EwRiskMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = load_app_config("configs/sim/default.yaml").ew_risk_map

    def test_grid_bounds_include_route_padding(self) -> None:
        route_points = [
            Position3D(0.0, 0.0, 30.0),
            Position3D(100.0, 40.0, 30.0),
        ]

        origin, width_cells, height_cells = build_grid_bounds(route_points, self.config)

        self.assertLessEqual(origin.x_m, -20.0)
        self.assertLessEqual(origin.y_m, -20.0)
        self.assertGreaterEqual(width_cells, 7)
        self.assertGreaterEqual(height_cells, 4)

    def test_route_progress_interpolation_is_deterministic(self) -> None:
        route_points = [
            Position3D(0.0, 0.0, 30.0),
            Position3D(100.0, 0.0, 30.0),
        ]

        self.assertEqual(interpolate_route_position(route_points, 0, 5), (0.0, 0.0))
        self.assertEqual(interpolate_route_position(route_points, 2, 5), (50.0, 0.0))
        self.assertEqual(interpolate_route_position(route_points, 4, 5), (100.0, 0.0))

    def test_service_is_deterministic_and_clamps_risk(self) -> None:
        manifest = self._manifest()
        tick_inputs = [
            EwRiskTickInput(
                tick_index=index,
                gnss_state="denied",
                sync_quality=1.0,
                localization_mode="VIO_PRIMARY",
                localization_confidence=0.4,
                trust_primary_reason_code="gnss_denial_suspected",
                trust_reason_codes=("gnss_denial_suspected", "localization_confidence_low"),
            )
            for index in range(6)
        ]

        service = EwRiskMapService(self.config)
        first = service.evaluate(manifest=manifest, tick_period_s=1.0, tick_inputs=tick_inputs)
        second = service.evaluate(manifest=manifest, tick_period_s=1.0, tick_inputs=tick_inputs)

        self.assertEqual(first.risk_cells_hash, second.risk_cells_hash)
        self.assertEqual(first.primary_reason_code, "ew_gnss_denial_hotspot")
        self.assertLessEqual(first.max_risk, 1.0)
        self.assertGreater(first.max_risk, self.config.risk_medium_floor)

    def test_decay_lowers_corridor_cost_after_recovery(self) -> None:
        manifest = self._manifest()
        service = EwRiskMapService(self.config)
        sustained = service.evaluate(
            manifest=manifest,
            tick_period_s=1.0,
            tick_inputs=[
                EwRiskTickInput(
                    tick_index=index,
                    gnss_state="denied",
                    sync_quality=1.0,
                    localization_mode="VIO_PRIMARY",
                    localization_confidence=0.4,
                    trust_primary_reason_code="gnss_denial_suspected",
                    trust_reason_codes=("gnss_denial_suspected",),
                )
                for index in range(4)
            ],
        )
        recovered = service.evaluate(
            manifest=manifest,
            tick_period_s=1.0,
            tick_inputs=[
                EwRiskTickInput(
                    tick_index=0,
                    gnss_state="denied",
                    sync_quality=1.0,
                    localization_mode="VIO_PRIMARY",
                    localization_confidence=0.4,
                    trust_primary_reason_code="gnss_denial_suspected",
                    trust_reason_codes=("gnss_denial_suspected",),
                ),
                *[
                    EwRiskTickInput(
                        tick_index=index,
                        gnss_state="nominal",
                        sync_quality=1.0,
                        localization_mode="GNSS_PRIMARY",
                        localization_confidence=0.95,
                        trust_primary_reason_code="trust_inputs_nominal",
                        trust_reason_codes=(),
                    )
                    for index in range(1, 4)
                ],
            ],
        )

        self.assertLess(recovered.max_risk, sustained.max_risk)
        self.assertLess(recovered.corridor_cost, sustained.corridor_cost)

    def _manifest(self) -> ScenarioManifest:
        return ScenarioManifest(
            scenario_id="ew_test",
            map_name="test_map",
            vehicle_spawn=Position3D(0.0, 0.0, 30.0),
            route_waypoints=[Position3D(100.0, 0.0, 30.0)],
            gnss_condition="nominal",
            run_seed=1,
            evaluation_profile="baseline_nominal_profile_v1",
            metadata={"title": "EW Test", "description": "EW test manifest", "owner": "test-suite"},
        )


if __name__ == "__main__":
    unittest.main()
