import unittest

from runtime.node_runner import (
    FORBIDDEN_RUNTIME_TOPIC_FAMILIES,
    MISSION_DECISION_AUTHORITY,
    RUNTIME_TOPIC_FAMILIES,
    validate_runtime_boundaries,
)


class TruthBoundaryTests(unittest.TestCase):
    def test_runtime_topics_do_not_include_truth_or_evaluation(self) -> None:
        runtime_topics = set(RUNTIME_TOPIC_FAMILIES)
        forbidden_topics = set(FORBIDDEN_RUNTIME_TOPIC_FAMILIES)
        self.assertEqual(runtime_topics.intersection(forbidden_topics), set())

    def test_runtime_boundary_guard_passes(self) -> None:
        validate_runtime_boundaries()

    def test_mission_decision_authority_is_locked(self) -> None:
        self.assertEqual(MISSION_DECISION_AUTHORITY, "mission_continuity_node")


if __name__ == "__main__":
    unittest.main()
