# ROS2 Launch Plan

- Run: `p12f_smoke`
- Scenario: `s1_nominal`
- Config: `sim-v1`
- Decision authority: `mission_continuity_node`

| Node | Role | Enabled |
| --- | --- | --- |
| scenario_orchestrator_node | runtime_autonomy | True |
| vio_node | runtime_autonomy | True |
| gnss_trust_node | runtime_autonomy | True |
| fusion_node | runtime_autonomy | True |
| trust_engine_node | runtime_autonomy | True |
| mission_continuity_node | runtime_autonomy | True |
| health_monitor_node | runtime_autonomy | True |
| ew_risk_map_node | tactical_intelligence | True |
| tactical_summary_node | tactical_intelligence | True |
| logger_node | verification | False |
| evaluation_node | verification | False |
| operator_station_node | operator_interface | True |
