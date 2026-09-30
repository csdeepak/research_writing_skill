"""Regression tests for proposal 20260929-visual-intelligence (skill 0.3.0 candidate, vNext Stage 2).

T-029  value labels round half-up on the written decimal (0.4155 -> 0.416), matching prose rounding
T-030  axis ticks are evenly spaced round numbers inside a declared domain; bars start at zero
T-031  rendering is deterministic (V6) and refuses unsupported/invalid input instead of drawing
T-032  planner (M04/M06/M10): prose for <= 3 values, trend -> line, intervals -> dot_ci, adverse must-show
T-033  sample selection (M08): deterministic for a seed, never picks unconsented/identifying samples
T-034  V gates in state.json: passed needs a fresh report; V5 needs a human review; stale registry blocks
T-035  every Stage 2 replay fixture (VIS-*) passes
T-050  V3_AXIS_ENCODING: marks must sit where the labelled value axis puts them. Fixture: a synthetic reproduction of the real line
       chart from the Stage 4 e2e run, whose value ticks were drawn on the x axis; fresh renders pass

Run: python -m unittest discover -s tools/tests -v
"""
from __future__ import annotations

import contextlib
import io
import json
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

import plan_visuals  # noqa: E402
import replay_fixtures  # noqa: E402
import select_samples  # noqa: E402
import validate_artifacts  # noqa: E402
import validate_visuals  # noqa: E402
import visuals  # noqa: E402

FIX = Path(__file__).resolve().parent / "fixtures" / "replay"


def _entry(rep="bar_h", **kw):
    e = {"id": "V001", "representation": rep, "title": "t", "alt_text": "a b c d e f g h", "value_label": "score",
         "data": {"file": "d.csv", "x": "x", "y": "y"}}
    e.update(kw)
    return e


def _pts(*ys, err=False):
    return {"points": [{"x": f"c{i}", "y": y, "series": "", **({"err_low": y - 0.1, "err_high": y + 0.1} if err else {})}
                       for i, y in enumerate(ys)], "universe": [], "excluded": []}


class RenderTests(unittest.TestCase):
    def test_T029_half_up_labels(self) -> None:
        self.assertEqual([visuals.value_label(v) for v in (0.4155, 0.4329, 1.4975, 52.5, 325, 0.0001)],
                         ["0.416", "0.433", "1.5", "52.5", "325", "0.0001"])

    def test_T030_ticks_and_domain(self) -> None:
        svg = visuals.render_svg(_entry("dot_ci", domain=[0, 1]), _pts(0.33, 0.71, 0.17, 0.63, err=True))
        ticks = [float(t) for t in re.findall(r'<text class="tick"[^>]*>([-\d.]+)</text>', svg)]
        self.assertGreaterEqual(min(ticks), 0)
        self.assertLessEqual(max(ticks), 1)
        steps = {round(b - a, 9) for a, b in zip(ticks, ticks[1:])}
        self.assertEqual(len(steps), 1)
        bar = visuals.render_svg(_entry(), _pts(52.5, 325, 96, 270))
        self.assertIn('data-domain-lo="0"', bar)

    def test_T031_deterministic_and_fail_closed(self) -> None:
        a = visuals.render_svg(_entry(), _pts(1, 2, 3, 4))
        self.assertEqual(a, visuals.render_svg(_entry(), _pts(1, 2, 3, 4)))
        with self.assertRaises(ValueError):
            visuals.render_svg(_entry("pie"), _pts(1, 2))
        with self.assertRaises(ValueError):
            visuals.render_svg(_entry("dot_ci", domain=[0, 1]), _pts(0.5, 1.2))
        with self.assertRaises(ValueError):
            visuals.render_svg(_entry(), _pts(1, -2))            # bars cannot encode negatives


class PlannerTests(unittest.TestCase):
    def test_T032_decisions(self) -> None:
        d = lambda vals: plan_visuals.decide(plan_visuals.shape(vals))[0]  # noqa: E731
        self.assertEqual(d([{"metric": "mae", "mean": 0.41, "std": 0.01}, {"metric": "mae", "mean": 0.40, "std": 0.01}]), "PROSE")
        self.assertEqual(d([{"metric": "mae", "by_shift": {"0.2": [0.47, 0.01], "0.4": [0.55, 0.01], "0.6": [0.64, 0.01]}},
                            {"metric": "mae", "by_shift": {"0.2": [0.42, 0.01], "0.4": [0.43, 0.01], "0.6": [0.45, 0.01]}}]),
                         "line")
        self.assertEqual(d([{"A": [0.3, 0.1, 0.5], "B": [0.7, 0.5, 0.9], "C": [0.2, 0.0, 0.3], "D": [0.6, 0.4, 0.8]}]), "dot_ci")
        self.assertEqual(d([{"A": 1.5, "B": 1.7, "C": 1.9, "D": 2.0}]), "bar_h")
        self.assertEqual(d([{"value": 0.34, "ci": [0.15, 0.52], "test": "bootstrap"}]), "PROSE")


class SampleTests(unittest.TestCase):
    ROWS = [{"id": f"s{i}", "correct": str(i % 2), "confidence": str(i / 20), "permission": "granted",
             "identifying_data": "false"} for i in range(20)]

    def test_T033_rule_and_consent(self) -> None:
        rows = self.ROWS + [{"id": "p1", "correct": "1", "confidence": "0.5", "permission": "unknown"},
                            {"id": "p2", "correct": "0", "confidence": "0.5", "permission": "granted", "identifying_data": "true"}]
        a = select_samples.select(rows, 2, 7, 0.5)
        self.assertEqual(a, select_samples.select(rows, 2, 7, 0.5))
        ids = {s["id"] for s in a["samples"]}
        self.assertNotIn("p1", ids)
        self.assertNotIn("p2", ids)
        self.assertEqual(a["excluded"], {"no_permission": 1, "identifying_data": 1})
        self.assertEqual(len(ids), 8)
        self.assertIn("seed 7", a["selection_rule"])


class VGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        fx = next(f for f in replay_fixtures.load_fixtures(FIX) if f["id"] == "VIS-00")
        replay_fixtures.materialise(fx["files"], self.tmp)
        self.rcs = self.tmp / ".rcs"
        with contextlib.redirect_stdout(io.StringIO()):
            visuals.cmd_render(self.rcs, self.tmp, None)
            validate_visuals.main([str(self.rcs), "--project-root", str(self.tmp), "--draft", str(self.tmp / "paper.md"),
                                   "--out", str(self.rcs / "audits/gates/V_visuals.json")])

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def eff(self) -> dict:
        (self.rcs / "state.json").write_text(json.dumps({"gates": {g: "passed" for g in ("V1", "V2", "V3", "V4", "V5", "V6")}}),
                                             encoding="utf-8")
        return validate_artifacts.check_gates(self.rcs, self.tmp, validate_artifacts.Report())

    def test_T034_v_gates(self) -> None:
        e = self.eff()
        self.assertEqual({g: e[g] for g in ("V1", "V2", "V3", "V4", "V6")}, dict.fromkeys(("V1", "V2", "V3", "V4", "V6"), "PASSED"))
        self.assertEqual(e["V5"], "NOT_RUN")          # no human review recorded
        reg = self.rcs / "plan" / "visual_registry.json"
        reg.write_text(reg.read_text(encoding="utf-8").replace("Which system", "Which one"), encoding="utf-8")
        self.assertEqual(self.eff()["V1"], "STALE")


class ReplayStage2Tests(unittest.TestCase):
    def test_T035_visual_fixtures(self) -> None:
        fixtures = [f for f in replay_fixtures.load_fixtures(FIX) if f["id"].startswith("VIS-")]
        self.assertGreaterEqual(len(fixtures), 16)
        for fx in fixtures:
            with self.subTest(fixture=fx["id"]):
                r = replay_fixtures.run_fixture(fx)
                self.assertTrue(r["ok"], json.dumps(r["checks"], indent=1)[:1500])


class AxisEncodingTests(unittest.TestCase):
    def test_T050(self) -> None:
        old = (Path(__file__).resolve().parent / "fixtures" / "visual" / "SYNTH-line_value_axis_on_x.svg").read_text(encoding="utf-8")
        self.assertGreaterEqual(len(validate_visuals.axis_encoding(old)), 30)
        line = {"points": [{"x": str(x), "y": y, "series": s} for s in ("a", "b") for x, y in
                           zip(range(0, 11), [0.0, 0.1, 0.3, 0.3, 0.5, 0.6, 0.6, 0.8, 0.9, 1.0, 1.0])],
                "universe": [], "excluded": []}
        svg = visuals.render_svg(_entry("line", domain=[0, 1], data={"file": "d.csv", "x": "step", "y": "y"}), line)
        self.assertEqual(validate_visuals.axis_encoding(svg), [])
        self.assertEqual(set(re.findall(r'<text class="tick" data-axis="(\w)"', svg)), {"y"})
        self.assertIn(">step</text>", svg)
        self.assertIn("rotate(-90", svg)
        for rep in ("bar_h", "dot_ci"):
            with self.subTest(rep=rep):
                self.assertEqual(validate_visuals.axis_encoding(
                    visuals.render_svg(_entry(rep), _pts(0.33, 0.71, 0.17, 0.63, err=rep == "dot_ci"))), [])
        # the same line chart with its value ticks moved to the x axis is caught
        bad = re.sub(r'<text class="tick" data-axis="y" data-pos="[^"]*" x="[^"]*" y="[^"]*"',
                     lambda m: '<text class="tick" y="300"', svg)
        bad = re.sub(r'(<text class="tick" y="300")', lambda m, c=iter(range(100, 700, 100)): f'{m.group(1)} x="{next(c)}"', bad)
        self.assertTrue(validate_visuals.axis_encoding(bad))


if __name__ == "__main__":
    unittest.main()
