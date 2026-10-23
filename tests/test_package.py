"""Guard the scientific inputs that must survive the repository cleanup."""
import importlib.util
import json
from pathlib import Path
import unittest

from emv import scenarios
from emv.params import TUNED_NORMAL, bluelight_params
from emv.reference import REFERENCE


class PackageTests(unittest.TestCase):
    def test_stage_two_matches_archived_fit(self):
        record = json.loads((REFERENCE / "ev_calibration.json").read_text())
        params = bluelight_params()
        for key, value in {**TUNED_NORMAL, **record["theta"]}.items():
            self.assertEqual(getattr(params, key), value, key)

    def test_measured_geometry_is_available_without_raw_data(self):
        for regime in scenarios.HIGHD_REGIMES:
            spec = scenarios.highd_regime(regime, str(REFERENCE / "highd_recordings.json"))
            self.assertTrue(spec["measured"])
            self.assertGreater(spec["lane_width"], 0)
            self.assertEqual(len(spec["lane_speeds"]), spec["n_lanes"])

    def test_game_integration_is_absent(self):
        self.assertIsNone(importlib.util.find_spec("emv.ue"))
        self.assertFalse(hasattr(scenarios, "game_params"))
        self.assertFalse(hasattr(scenarios, "GAME"))


if __name__ == "__main__":
    unittest.main()
