import tempfile
import unittest
from pathlib import Path
from resolver.controller import initialise, record_check, next_task, begin_repair, save, load

class ControllerTests(unittest.TestCase):
    def test_each_kind_independent(self):
        state = initialise(["site"])
        self.assertEqual(len(state["tasks"]), 2)
        record_check(state, "site", "movie", [{"provider":"site","kind":"movie","error":"http_404"}])
        self.assertEqual(state["tasks"][0]["state"], "needs_repair")
        self.assertEqual(state["tasks"][1]["state"], "pending")
        self.assertEqual(next_task(state)["kind"], "series")
    def test_bounded_repair(self):
        state = initialise(["site"])
        bad = [{"provider":"site","kind":"movie","error":"decoder_failure"}]
        record_check(state,"site","movie",bad)
        self.assertTrue(begin_repair(state,"site","movie",max_attempts=1))
        record_check(state,"site","movie",bad)
        self.assertFalse(begin_repair(state,"site","movie",max_attempts=1))
        self.assertEqual(state["tasks"][0]["state"], "failed")
    def test_no_repair_of_working(self):
        state = initialise(["site"])
        with self.assertRaises(ValueError):
            begin_repair(state,"site","movie")
    def test_checkpoint(self):
        state = initialise(["site"])
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/"checkpoint.json"
            save(state,path)
            self.assertEqual(load(path),state)
    def test_reject_wrong_evidence(self):
        state = initialise(["site"])
        with self.assertRaises(ValueError):
            record_check(state,"site","movie",[{"provider":"other","kind":"movie"}])
if __name__ == "__main__":
    unittest.main()
