"""Wheelhouse index builder: one link per wheel filename (PEP 503)."""
from __future__ import annotations

import importlib.util
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load():
    spec = importlib.util.spec_from_file_location(
        "build_wheelhouse_index",
        os.path.join(ROOT, "scripts", "build-wheelhouse-index.py"),
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


class DedupeByFilename(unittest.TestCase):
    def test_same_filename_same_digest_is_one_link_without_warning(self):
        mod = _load()
        w = {"name": "odfpy-1.4.1-py2.py3-none-any.whl", "digest": "sha256:aa", "url": "u1"}
        out, notes = mod.dedupe_by_filename([w, dict(w, url="u2")])
        self.assertEqual([x["url"] for x in out], ["u1"])
        self.assertEqual(notes, [])

    def test_same_filename_other_digest_keeps_first_and_reports(self):
        mod = _load()
        a = {"name": "odfpy-1.4.1-py2.py3-none-any.whl", "digest": "sha256:aa", "url": "u1"}
        b = {"name": a["name"], "digest": "sha256:bb", "url": "u2"}
        out, notes = mod.dedupe_by_filename([a, b])
        self.assertEqual([x["url"] for x in out], ["u1"])
        self.assertEqual(len(notes), 1)
        self.assertIn(a["name"], notes[0])

    def test_distinct_filenames_are_all_kept(self):
        mod = _load()
        ws = [
            {"name": "numpy-2.5.4-cp312-cp312-netbsd_11_1_amd64.whl", "digest": "sha256:aa", "url": "u1"},
            {"name": "numpy-2.5.4-cp312-cp312-freebsd_15_1_release_p6_amd64.whl", "digest": "sha256:bb", "url": "u2"},
        ]
        out, notes = mod.dedupe_by_filename(ws)
        self.assertEqual(len(out), 2)
        self.assertEqual(notes, [])


if __name__ == "__main__":
    unittest.main()
