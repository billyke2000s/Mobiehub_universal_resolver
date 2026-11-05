import unittest
from resolver.model import classify, route_passes

PASS = {k: True for k in ("identity_match", "runtime_plausible", "decoded_frames",
                         "smooth_progress", "opening_audio", "midpoint_audio",
                         "late_audio", "midpoint_seek", "late_seek")}

class EvidenceTests(unittest.TestCase):
    def test_complete_pass(self):
        self.assertTrue(route_passes(PASS))
    def test_link_alone_is_not_playback(self):
        self.assertFalse(route_passes({"url": "https://example.org/video.mp4"}))
    def test_missing_audio_rejects(self):
        self.assertFalse(route_passes({**PASS, "late_audio": False}))
    def test_separate_movie_series(self):
        rows = classify([{"provider": "demo", "kind": "movie", **PASS},
                         {"provider": "demo", "kind": "series", "error": "http_404"}])
        self.assertEqual([(r["kind"], r["status"]) for r in rows],
                         [("movie", "working"), ("series", "broken")])
    def test_failed_alternative_is_preserved(self):
        row = classify([{"provider": "demo", "kind": "movie", **PASS},
                        {"provider": "demo", "kind": "movie", "error": "decoder_failure"}])[0]
        self.assertEqual(row["status"], "partial")
        self.assertEqual(len(row["attempts"]), 2)
    def test_access_challenge_not_working(self):
        self.assertEqual(classify([{"provider": "demo", "kind": "movie",
                                    "error": "access_challenge"}])[0]["status"], "blocked")
    def test_no_evidence_is_unverified(self):
        self.assertEqual(classify([{"provider": "demo", "kind": "movie"}])[0]["status"], "unverified")

if __name__ == "__main__":
    unittest.main()
