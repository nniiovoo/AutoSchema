"""Real evidence replay regressions and protection of its reviewed fixtures."""
from contextlib import redirect_stderr, redirect_stdout
import io
import json
from pathlib import Path
import tempfile
import unittest

from run_task3_real_papers import FIXTURES, main


class RealPaperReplayTests(unittest.TestCase):
    def test_curated_replay_matches_frozen_expectations(self):
        with tempfile.TemporaryDirectory() as folder, redirect_stdout(io.StringIO()):
            self.assertEqual(0, main(["--out-dir", folder]))
            manifest = json.loads((Path(folder) / "manifest.json").read_text())
        self.assertEqual([], manifest["expectation_mismatches"])
        self.assertEqual({"retrieve_more": 4}, manifest["shared_decisions"])
        self.assertEqual({"supported_as_reported": 10}, manifest["supplied_evidence_check_statuses"])
        self.assertFalse(any(Path(p).name.startswith("._") for p in manifest["sha256"]))

    def test_rejects_fixture_directory_before_writing(self):
        with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
            main(["--out-dir", str(FIXTURES)])
        self.assertEqual(2, error.exception.code)

    def test_rejects_output_symlinks_before_any_write(self):
        for route in ("directory", "input_file", "manifest_file"):
            with self.subTest(route=route), tempfile.TemporaryDirectory() as folder:
                root = Path(folder)
                out = root / "out"
                out.mkdir()
                protected = root / "protected.json"
                protected.write_text("original reviewed content")
                diagnostic = out / "li-ambient-fracture-strain"
                if route == "directory":
                    diagnostic.symlink_to(root, target_is_directory=True)
                elif route == "input_file":
                    diagnostic.mkdir()
                    (diagnostic / "input.json").symlink_to(protected)
                else:
                    (out / "manifest.json").symlink_to(protected)
                with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
                    main(["--out-dir", str(out)])
                self.assertEqual(2, error.exception.code)
                self.assertEqual("original reviewed content", protected.read_text())
                self.assertFalse((out / "shared").exists())
                self.assertFalse((root / "input.json").exists())


if __name__ == "__main__":
    unittest.main()
