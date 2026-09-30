"""Regression tests for the open-source release (v0.4.0).

T-064  synthetic example project: every planted problem the tools can catch is caught in drafts/flawed.md; the
       documented gaps (missing sample size; denominator direction) stay gaps; the clean control passes once the
       evidence conflict is resolved and the figure re-rendered
T-065  C5-citation-unregistered: author-year citations resolve to the source registry (ERROR otherwise; WARN when the
       project has no registry); parenthetical years that are not citations are ignored
T-066  failure-case archive: the real archive validates; a case naming a missing test or fixture fails
T-067  skill ZIP: builds, validates, has one correctly named root, and its tools run from the extracted folder
T-068  repository audit: planted secret, absolute path, private marker, broken link and title-less SVG are found
T-070  per-project language policy: extend an existing license type, disable one, refuse unknown types
T-071  every strong-language license rule is an ERROR on a fail-closed claim map; basis "none" is UNSUPPORTED_FACT
T-069  CLI: `rce.py check` exits 1 on the flawed draft and prints the rule names; unknown commands exit 2

Run: python -m unittest discover -s tools/tests -v
"""
from __future__ import annotations

import contextlib
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]
REPO = TOOLS.parent
sys.path.insert(0, str(TOOLS))

import check_repo  # noqa: E402
import lint_draft  # noqa: E402
import package_skill  # noqa: E402
import validate_cases  # noqa: E402

EXAMPLE = REPO / "examples" / "synthetic_project"


def run(*args: str, cwd: Path | None = None) -> tuple[int, str]:
    p = subprocess.run([sys.executable, *args], capture_output=True, text=True, encoding="utf-8", cwd=cwd)
    return p.returncode, p.stdout + p.stderr


@unittest.skipUnless(EXAMPLE.exists(), "examples/synthetic_project not present (packaged skill)")
class SyntheticProjectTests(unittest.TestCase):
    def test_T064(self) -> None:
        rcs, draft = EXAMPLE / ".rcs", EXAMPLE / "drafts" / "flawed.md"
        found = ""
        for args in (["validate_artifacts.py", str(rcs), "--project-root", str(EXAMPLE)],
                     ["validate_visuals.py", str(rcs), "--project-root", str(EXAMPLE)],
                     ["lint_draft.py", str(draft), "--rcs", str(rcs)],
                     ["verify_numbers.py", str(draft), "--rcs", str(rcs), "--project-root", str(EXAMPLE), "--strict"]):
            found += run(str(TOOLS / args[0]), *args[1:])[1]
        for code in ("UNRECONCILED_CONFLICT", "V6_NOT_REPRODUCIBLE", "V3_AXIS_ENCODING", "UNLICENSED-significance_test",
                     "UNLICENSED-sota_comparison", "C5-citation-unregistered", "BLOCKED-claim-used", "C6-injection"):
            self.assertIn(code, found, code)
        self.assertRegex(found, r"UNTRACED_NUMBER\s+0\.69")
        self.assertRegex(found, r"DERIVED_MATCH\s+25%")          # documented gap: flagged for confirmation, not rejected
        with tempfile.TemporaryDirectory() as tmp:                # clean control after resolving + re-rendering
            root = Path(tmp) / "p"
            shutil.copytree(EXAMPLE, root)
            p = root / ".rcs" / "evidence" / "research_evidence.json"
            d = json.loads(p.read_text(encoding="utf-8"))
            for it in d["items"]:
                if it["id"] in ("E003", "E004"):
                    it.update(status="conflicting", conflicts_with=["E004" if it["id"] == "E003" else "E003"],
                              resolution={"chosen": "E003", "reason": "results file authoritative; README stale", "by": "human"})
            p.write_text(json.dumps(d), encoding="utf-8")
            self.assertEqual(run(str(TOOLS / "visuals.py"), "render", str(root / ".rcs"), "--project-root", str(root))[0], 0)
            clean = root / "drafts" / "clean.md"
            for args in (["validate_artifacts.py", str(root / ".rcs"), "--project-root", str(root)],
                         ["lint_draft.py", str(clean), "--rcs", str(root / ".rcs")],
                         ["verify_numbers.py", str(clean), "--rcs", str(root / ".rcs"), "--project-root", str(root), "--strict"]):
                code, out = run(str(TOOLS / args[0]), *args[1:])
                self.assertEqual(code, 0, out[-600:])
            code, out = run(str(TOOLS / "validate_visuals.py"), str(root / ".rcs"), "--project-root", str(root))
            self.assertNotIn("ERROR", out)


class CitationTests(unittest.TestCase):
    def test_T065(self) -> None:
        src = [{"authors": ["Ana Rivera", "Tom Okafor"], "year": 2019}, {"authors": ["Kim, H."], "year": 2021}]
        md = ("Known (Rivera et al., 2019; Kim, 2021). Invented (Moreau et al., 2022). Also (Rivera and Okafor, 2019).\n"
              "Released (2021). Counts (n = 24, 2021). See the 2019 survey.\n")
        f = [x for x in lint_draft.lint_text(md, {}, False, False, set(), sources=src).findings if x["rule"].startswith("C5")]
        self.assertEqual([(x["level"], x["excerpt"]) for x in f], [("ERROR", "Moreau et al., 2022")])
        f = [x for x in lint_draft.lint_text(md, {}, False, False, set(), sources=None).findings if x["rule"].startswith("C5")]
        self.assertTrue(f and all(x["level"] == "WARN" for x in f))
        self.assertFalse([x for x in lint_draft.lint_text(md, {}, False, False, set()).findings if x["rule"].startswith("C5")])


class CaseArchiveTests(unittest.TestCase):
    @unittest.skipUnless((REPO / "cases" / "failures").exists(), "case archive not present (packaged skill)")
    def test_T066(self) -> None:
        self.assertEqual(validate_cases.check(REPO / "cases" / "failures"), [])
        with tempfile.TemporaryDirectory() as tmp:
            case = json.loads((REPO / "cases" / "failures" / "FC-0001.json").read_text(encoding="utf-8"))
            missing = "T-" + "9" * 3                          # built at runtime: the id must not occur in any test source
            case["regression"] = {"tests": [missing], "replay_fixtures": ["NOPE-1"]}
            (Path(tmp) / "FC-0001.json").write_text(json.dumps(case), encoding="utf-8")
            problems = validate_cases.check(Path(tmp))
            self.assertTrue(any(missing in p for p in problems) and any("NOPE-1" in p for p in problems))


class PackageTests(unittest.TestCase):
    @unittest.skipUnless((REPO / "skill" / "SKILL.md").exists(), "source tree only")
    def test_T067(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with contextlib.redirect_stdout(io.StringIO()):
                z = package_skill.build(Path(tmp) / "dist")
            self.assertEqual(package_skill.check(z), [])
            with zipfile.ZipFile(z) as zf:
                roots = {n.split("/", 1)[0] for n in zf.namelist()}
                self.assertEqual(roots, {"research-communication-engine"})
                self.assertFalse([n for n in zf.namelist() if "/tests/" in n and n.endswith(".py")])  # tests not shipped
                zf.extractall(Path(tmp) / "x")
            skill = Path(tmp) / "x" / "research-communication-engine"
            code, out = run("tools/validate_artifacts.py", "examples/demo_project/.rcs", cwd=skill)
            self.assertEqual(code, 0, out[-400:])
            code, out = run("tools/rce_llm.py", "check", "--rcs", "x", "--config", "templates/models.json", cwd=skill)
            self.assertEqual(code, 0, out[-400:])
            bad = Path(tmp) / "bad.zip"
            with zipfile.ZipFile(bad, "w") as zf:
                zf.writestr("wrong-name/SKILL.md", "---\nname: research-communication-engine\ndescription: x\n---\n")
                zf.writestr("wrong-name/tools/a.py", "KEY = 'sk-" + "a" * 30 + "'\n")
            problems = package_skill.check(bad)
            self.assertTrue(any("must equal the skill name" in p for p in problems))
            self.assertTrue(any("secret" in p for p in problems))


class AuditTests(unittest.TestCase):
    def test_T068(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            r = Path(tmp)
            (r / "docs").mkdir()
            (r / "tools").mkdir()
            (r / "README.md").write_text("See [the guide](docs/missing.md) and [ok](docs/a.md).\n", encoding="utf-8")
            (r / "docs" / "a.md").write_text("Path " + "C:" + "/Us" + "ers/someone/private/x.txt\n", encoding="utf-8")
            (r / "docs" / "d.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg"><rect/></svg>', encoding="utf-8")
            (r / "tools" / "k.py").write_text("TOKEN = 'ghp_" + "x" * 36 + "'\n", encoding="utf-8")
            (r / "tools" / "n.md").write_text("mentions PROJECT-X-SECRET data\n", encoding="utf-8")
            (r / ".rce-audit-denylist").write_text("project-x-secret\n", encoding="utf-8")
            errors, _ = check_repo.audit(r)
            text = "\n".join(errors)
            for needle in ("broken link docs/missing.md", "absolute local path", "SVG has no <title>", "looks like a secret",
                           "private marker"):
                self.assertIn(needle, text)


class CliTests(unittest.TestCase):
    @unittest.skipUnless(EXAMPLE.exists(), "examples/synthetic_project not present (packaged skill)")
    def test_T069(self) -> None:
        code, out = run(str(TOOLS / "rce.py"), "check", str(EXAMPLE), "--draft", str(EXAMPLE / "drafts" / "flawed.md"))
        self.assertEqual(code, 1)
        self.assertIn("C5-citation-unregistered", out)
        self.assertIn("RESULT: FAIL", out)
        self.assertEqual(run(str(TOOLS / "rce.py"), "no-such-command")[0], 2)


class LanguagePolicyTests(unittest.TestCase):
    def test_T070(self) -> None:
        claims = {"C001": {"id": "C001", "claim_type": "measured", "licenses": [], "status": "VERIFIED"}}
        md = "M is meaningfully better than B {C001}. M always wins {C001}.\n"

        def rules() -> set[str]:
            return {f["rule"] for f in lint_draft.lint_text(md, claims, False, False, set()).findings
                    if f["rule"].startswith("UNLICENSED")}
        try:
            lint_draft.apply_language_policy(None)
            self.assertEqual(rules(), {"UNLICENSED-complete_enumeration"})
            with tempfile.TemporaryDirectory() as tmp:
                pol = Path(tmp) / "language_policy.json"
                pol.write_text(json.dumps({"extend": {"significance_test": [r"\bmeaningful(ly)? (better|worse)\b"]},
                                           "disable": ["complete_enumeration"], "reason": "community convention"}),
                               encoding="utf-8")
                applied = lint_draft.apply_language_policy(Path(tmp))
                self.assertEqual(applied["disable"], ["complete_enumeration"])
                self.assertEqual(rules(), {"UNLICENSED-significance_test"})
                pol.write_text(json.dumps({"disable": ["no_such_license"]}), encoding="utf-8")
                with self.assertRaises(SystemExit):
                    lint_draft.apply_language_policy(Path(tmp))
        finally:
            lint_draft.apply_language_policy(None)


class IntegrityRuleTests(unittest.TestCase):
    """T-071: each strong-language license rule fires as ERROR on a fail-closed claim map, and a measured claim with
    basis "none" is UNSUPPORTED_FACT (the rules docs/concepts/EVIDENCE_INTEGRITY.md cites)."""

    def test_T071(self) -> None:
        claims = {"C001": {"id": "C001", "claim_type": "measured", "licenses": [], "status": "VERIFIED"}}
        cases = {"significance_test": "M is significantly better {C001}.", "sota_comparison": "M is state-of-the-art {C001}.",
                 "causal_design": "The new loss causes the gain {C001}.", "ood_eval": "M generalizes to new domains {C001}.",
                 "matched_evaluation": "M outperforms B {C001}.", "stress_test": "M is robust to noise {C001}.",
                 "literature_search": "M is the first method to do this {C001}."}
        lint_draft.apply_language_policy(None)
        for lic, sentence in cases.items():
            with self.subTest(license=lic):
                levels = {f["level"] for f in lint_draft.lint_text(sentence + "\n", claims, False, False, set()).findings
                          if f["rule"] == f"UNLICENSED-{lic}"}
                self.assertEqual(levels, {"ERROR"})
        import truth_guardrail
        import validate_artifacts
        rep = validate_artifacts.Report()
        claim = {"id": "C009", "statement": "x", "claim_type": "measured", "evidence": [], "basis": "none",
                 "confidence": "low", "author_confirmation": "pending"}
        with tempfile.TemporaryDirectory() as tmp:
            rcs = Path(tmp) / ".rcs"
            (rcs / "claims").mkdir(parents=True)
            (rcs / "claims" / "claim_evidence_map.json").write_text(json.dumps(
                {"claims": [claim], "limitations": [], "negative_result_decisions": []}), encoding="utf-8")
            truth_guardrail.run(rcs, Path(tmp), validate_artifacts.check_schemas(rcs, rep), rep)
        self.assertTrue(any("UNSUPPORTED_FACT" in i["message"] for i in rep.items), rep.items)


if __name__ == "__main__":
    unittest.main()
