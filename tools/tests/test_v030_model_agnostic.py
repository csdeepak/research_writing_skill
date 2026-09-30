"""Regression tests for the model-agnostic runtime (skill 0.3.0 candidate, Stage 5: tools/rce_llm.py, tools/rce_roles.py).

T-052  config + data policy: hosted endpoints refused unless allowed; loopback/command/manual/mock local; keys never in
       the config; a missing key env var is an error
T-053  provider requests: OpenAI-compatible, Anthropic and Gemini request shapes; the key travels only in a header
T-054  JSON roles: extraction from fenced/prose replies; validation errors are sent back and the retry succeeds; the
       call log is content-free
T-055  REVIEW_AGENT through any provider: calibration replayed from real review outputs reproduces 0.933 / 0.05;
       `review` writes schema-valid diagnostics, records the ledger as REVIEW and reports the calibration status
T-056  manual provider (any chat UI) and command provider (any CLI)
T-057  run-tasks executes task folders with a role's model and skips finished ones
T-062  review normalisation shortens over-long location quotes only (never scores or findings) and reports it
T-058  transient provider failures (rate limits, overloads, timeouts) are retried with backoff; real errors are not

Run: python -m unittest discover -s tools/tests -v
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

import rce_llm  # noqa: E402
import rce_roles  # noqa: E402
from rce_common import SKILL_DIR  # noqa: E402

REVIEWS = Path(__file__).resolve().parent / "fixtures" / "review_outputs"


def quiet(fn, *a):
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return fn(*a)


def cfg_with(role_cfg: dict, allowed: list[str] | None = None) -> dict:
    return {"roles": {"default": role_cfg}, "data_policy": {"allowed_hosts": allowed or []}, "keep_transcripts": False}


class _Tmp(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp())
        rce_llm.MOCK_REPLIES.clear()

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)
        rce_llm.MOCK_REPLIES.clear()


class PolicyTests(_Tmp):
    def test_T052(self) -> None:
        hosted = {"provider": "openai", "base_url": "https://api.example.com/v1", "model": "m"}
        with self.assertRaises(rce_llm.PolicyError):
            rce_llm.check_policy(cfg_with(hosted), rce_llm.role_config(cfg_with(hosted), "REVIEW_AGENT"))
        self.assertEqual(rce_llm.check_policy(cfg_with(hosted, ["api.example.com"]),
                                              rce_llm.role_config(cfg_with(hosted), "REVIEW_AGENT")), "api.example.com")
        for local in ({"provider": "openai", "base_url": "http://localhost:11434/v1", "model": "m"},
                      {"provider": "openai", "base_url": "http://127.0.0.1:8000/v1", "model": "m"},
                      {"provider": "command", "command": ["x"]}, {"provider": "manual"}, {"provider": "mock"}):
            self.assertEqual(rce_llm.check_policy(cfg_with(local), rce_llm.role_config(cfg_with(local), "R")), "local")
        with self.assertRaises(rce_llm.PolicyError):          # anthropic/gemini default hosts are hosted, too
            c = cfg_with({"provider": "anthropic", "model": "m", "api_key_env": "X"})
            rce_llm.check_policy(c, rce_llm.role_config(c, "R"))
        p = self.tmp / "models.json"
        p.write_text(json.dumps({"roles": {"R": {"provider": "openai", "base_url": "http://localhost/v1", "api_key": "sk-x"}}}),
                     encoding="utf-8")
        with self.assertRaises(rce_llm.LLMError):
            rce_llm.load_config(path=p)
        tpl = rce_llm.load_config(path=SKILL_DIR / "templates" / "models.json")
        for role in ("REVIEW_AGENT", "RECON_GRADER", "READER"):
            self.assertEqual(rce_llm.check_policy(tpl, rce_llm.role_config(tpl, role)), "local")
        os.environ.pop("RCE_TEST_MISSING_KEY", None)
        with self.assertRaises(rce_llm.LLMError):
            rce_llm._key({"role": "R", "api_key_env": "RCE_TEST_MISSING_KEY"})


class ProviderRequestTests(_Tmp):
    def test_T053(self) -> None:
        seen = []

        def fake_post(url, headers, body, rc):
            seen.append((url, headers, body))
            if "anthropic" in url:
                return {"content": [{"type": "text", "text": "A"}]}
            if "generativelanguage" in url:
                return {"candidates": [{"content": {"parts": [{"text": "G"}]}}]}
            return {"choices": [{"message": {"content": "O"}}]}
        orig = rce_llm.http_post
        rce_llm.http_post = fake_post
        os.environ["RCE_TEST_KEY"] = "secret-123"
        try:
            base = {"role": "R", "model": "m-1", "api_key_env": "RCE_TEST_KEY", "temperature": 0}
            self.assertEqual(rce_llm._openai({**base, "base_url": "https://h.example/v1/", "json_mode": True}, "S", "U"), "O")
            self.assertEqual(rce_llm._anthropic(base, "S", "U"), "A")
            self.assertEqual(rce_llm._gemini(base, "S", "U"), "G")
        finally:
            rce_llm.http_post = orig
            os.environ.pop("RCE_TEST_KEY", None)
        (u1, h1, b1), (u2, h2, b2), (u3, h3, b3) = seen
        self.assertEqual(u1, "https://h.example/v1/chat/completions")
        self.assertEqual(h1["Authorization"], "Bearer secret-123")
        self.assertEqual(b1["messages"][0], {"role": "system", "content": "S"})
        self.assertEqual(b1["response_format"], {"type": "json_object"})
        self.assertEqual(u2, "https://api.anthropic.com/v1/messages")
        self.assertEqual((h2["x-api-key"], b2["system"], b2["messages"][0]["content"]), ("secret-123", "S", "U"))
        self.assertTrue(u3.endswith("/v1beta/models/m-1:generateContent"))
        self.assertEqual(h3["x-goog-api-key"], "secret-123")
        for url, _, body in seen:                      # the key is never in a URL or a body
            self.assertNotIn("secret-123", url + json.dumps(body))


class JsonRepairTests(_Tmp):
    def test_T054(self) -> None:
        self.assertEqual(rce_llm.extract_json('Sure! Here it is:\n```json\n{"a": 1}\n```\nThanks'), {"a": 1})
        self.assertEqual(rce_llm.extract_json('{"a": [1, 2]} trailing words {"b": 2}'), {"a": [1, 2]})
        # truncated closers (seen from a non-Claude reviewer on the benchmark): only missing closers are added
        self.assertEqual(rce_llm.extract_json('{"d": {"f": [1, {"x": "a}b"}]'), {"d": {"f": [1, {"x": "a}b"}]}})
        self.assertEqual(rce_llm.extract_json('{"n": "unterminated'), {"n": "unterminated"})
        schema = {"type": "object", "required": ["n"], "properties": {"n": {"type": "integer"}}}
        prompts = []

        def second(system, user):
            prompts.append(user)
            return '```json\n{"n": 3}\n```'
        rce_llm.MOCK_REPLIES["R"] = [lambda s, u: prompts.append(u) or '{"n": "three"} SECRET-PROMPT-ECHO', second]
        rcs = self.tmp / ".rcs"
        rcs.mkdir()
        obj, meta = rce_llm.complete_json(cfg_with({"provider": "mock"}), "R", "sys", "USER-SENTINEL-7", rcs=rcs, schema=schema)
        self.assertEqual(obj, {"n": 3})
        self.assertEqual(meta["attempts"], 2)
        self.assertIn("failed validation", prompts[1])
        self.assertIn("USER-SENTINEL-7", prompts[1])
        log = (rcs / "audits" / "llm_calls.jsonl").read_text(encoding="utf-8")
        self.assertEqual(len(log.splitlines()), 2)
        self.assertNotIn("USER-SENTINEL-7", log)            # content-free: hashes and sizes only
        self.assertNotIn("SECRET-PROMPT-ECHO", log)
        rce_llm.MOCK_REPLIES["R"] = ["not json"] * 3
        with self.assertRaises(rce_llm.LLMError):
            rce_llm.complete_json(cfg_with({"provider": "mock"}), "R", "s", "u", schema=schema, retries=2)


def replay(variant_of_paper):
    """Mock reviewer: returns the real review for whichever benchmark paper is in the prompt, with its packet id."""
    def reply(system, user):
        pid = re.search(r"packet_id: (pkt-[0-9a-f]+)", user).group(1)
        obj = json.loads((REVIEWS / f"{variant_of_paper(user)}.json").read_text(encoding="utf-8"))
        obj["reconstruction"]["packet_id"] = obj["diagnostics"]["packet_id"] = pid
        return json.dumps(obj)
    return reply


class ReviewRoleTests(_Tmp):
    def test_T055(self) -> None:
        firsts = {}
        for v in sorted(json.loads((rce_roles.PERT / "EXPECTED.json").read_text(encoding="utf-8"))["variants"]):
            body = (rce_roles.PERT / v).read_text(encoding="utf-8")
            firsts[v.replace(".md", "")] = next(l for l in body.splitlines()[5:] if len(l) > 60)[:60]

        def which(user):
            return next(v for v, line in firsts.items() if line in user)
        rcs = self.tmp / ".rcs"
        rcs.mkdir()
        (rcs / "models.json").write_text(json.dumps({"roles": {"REVIEW_AGENT": {"provider": "mock", "model": "replay"}},
                                                     "keep_transcripts": False}), encoding="utf-8")
        rce_llm.MOCK_REPLIES["REVIEW_AGENT"] = [replay(which) for _ in range(7)]
        code = quiet(rce_roles.main, ["calibrate", "--rcs", str(rcs)])
        cal = json.loads((rcs / "audits" / "reviewer_calibration.json").read_text(encoding="utf-8"))
        self.assertEqual(code, 0)
        self.assertEqual((cal["mean_dimension_sensitivity"], cal["false_alarm_rate_on_A"], cal["calibrated"]), (0.933, 0.05, True))
        self.assertEqual(len(set(r["packet_id"] for r in cal["runs"].values())), 7)     # blinded: fresh random ids
        # review on a real packet built by build_review_packet, with the ledger in use
        pk = rcs / "packets" / "review_v001_1"
        pk.mkdir(parents=True)
        (pk / "paper.md").write_text((rce_roles.PERT / "A_clean.md").read_text(encoding="utf-8"), encoding="utf-8")
        (pk / "audience.md").write_text("a", encoding="utf-8")
        (pk / "objective.md").write_text("o", encoding="utf-8")
        (pk / "packet_manifest.json").write_text(json.dumps({"packet_id": "pkt-0000abcd"}), encoding="utf-8")
        (rcs / "provenance.jsonl").write_text("", encoding="utf-8")
        rce_llm.MOCK_REPLIES["REVIEW_AGENT"] = [replay(lambda u: "A_clean")]
        self.assertEqual(quiet(rce_roles.main, ["review", "--rcs", str(rcs), "--round", "v001_1"]), 0)
        d = rcs / "diagnostics" / "v001_1"
        self.assertEqual(json.loads((d / "diagnostics.json").read_text(encoding="utf-8"))["packet_id"], "pkt-0000abcd")
        log = json.loads((d / "reviewer_log.json").read_text(encoding="utf-8"))
        self.assertEqual((log["calibration"], log["files_read"]), ("passed", ["audience.md", "objective.md", "paper.md"]))
        ledger = [json.loads(l) for l in (rcs / "provenance.jsonl").read_text(encoding="utf-8").splitlines()]
        self.assertEqual({r["role"] for r in ledger}, {"REVIEW"})
        self.assertIn("diagnostics/v001_1/diagnostics.json", {r["path"] for r in ledger})
        import g4_check                                  # the reviewer log must satisfy G4's isolation check
        g4 = g4_check.check(rcs, "v001_1", None)
        self.assertEqual([i for i in g4["items"] if i["code"] == "G4_ISOLATION"], [])


class ManualAndCommandTests(_Tmp):
    def test_T056(self) -> None:
        rc = {"role": "READER", "provider": "manual", "dir": str(self.tmp / "manual")}
        with self.assertRaises(rce_llm.ManualPending):
            rce_llm._manual(rc, "S", "U")
        d = next((self.tmp / "manual" / "READER").iterdir())
        self.assertIn("# USER\n\nU", (d / "prompt.md").read_text(encoding="utf-8"))
        (d / "reply.md").write_text("pasted answer", encoding="utf-8")
        self.assertEqual(rce_llm._manual(rc, "S", "U"), "pasted answer")
        cmd = {"role": "READER", "provider": "command",
               "command": [sys.executable, "-c", "import sys; print(sys.stdin.read().upper()[-5:])"]}
        self.assertEqual(rce_llm._command(cmd, "s", "hello").strip(), "HELLO")


class RunTasksTests(_Tmp):
    def test_T057(self) -> None:
        rcs = self.tmp / ".rcs"
        rcs.mkdir()
        (rcs / "models.json").write_text(json.dumps({"roles": {"READER": {"provider": "mock"}}, "keep_transcripts": False}),
                                         encoding="utf-8")
        tasks = self.tmp / "tasks"
        for name in ("t1", "t2", "t3"):
            (tasks / name).mkdir(parents=True)
            (tasks / name / "prompt.md").write_text(f"answer for {name}", encoding="utf-8")
        (tasks / "t3" / "output.txt").write_text("already done", encoding="utf-8")
        rce_llm.MOCK_REPLIES["READER"] = [lambda s, u: '{"answers": ["' + u.split()[-1] + '"]}'] * 2
        self.assertEqual(quiet(rce_roles.main, ["run-tasks", str(tasks), "--rcs", str(rcs), "--json"]), 0)
        self.assertEqual(json.loads((tasks / "t1" / "output.txt").read_text(encoding="utf-8")), {"answers": ["t1"]})
        self.assertEqual((tasks / "t3" / "output.txt").read_text(encoding="utf-8"), "already done")


class TransientRetryTests(_Tmp):
    def test_T058(self) -> None:
        calls, waits = [], []

        def flaky(rc, system, user):
            calls.append(1)
            if len(calls) == 1:
                raise rce_llm.LLMError('provider error: {"code": 429, "message": "temporarily rate-limited upstream"}')
            return "ok"
        rce_llm.PROVIDERS["flaky"] = flaky
        try:
            rc = {"role": "R", "provider": "flaky", "retry_wait": 5}
            self.assertEqual(rce_llm._call(rc, "s", "u", sleep=waits.append), "ok")
            self.assertEqual((len(calls), waits), (2, [5.0]))
            rce_llm.PROVIDERS["flaky"] = lambda rc, s, u: (_ for _ in ()).throw(rce_llm.LLMError("HTTP 401 unauthorized"))
            with self.assertRaises(rce_llm.LLMError):
                rce_llm._call(rc, "s", "u", sleep=waits.append)
            self.assertEqual(len(waits), 1)                  # a real error is not retried
        finally:
            rce_llm.PROVIDERS.pop("flaky", None)


class ReviewNormalizeTests(_Tmp):
    def test_T062(self) -> None:
        obj = json.loads((REVIEWS / "A_clean.json").read_text(encoding="utf-8"))
        before = json.loads(json.dumps(obj))
        long_q = " ".join(f"w{i}" for i in range(40))
        obj["diagnostics"]["findings"][0]["location"]["quote"] = long_q
        self.assertEqual(rce_roles.normalize_review(obj), 1)
        q = obj["diagnostics"]["findings"][0]["location"]["quote"]
        self.assertTrue(q.startswith("w0 w1") and q.endswith("…") and len(q.split()) == 20 and len(q) <= 200)
        for a, b in zip(obj["diagnostics"]["findings"], before["diagnostics"]["findings"]):
            self.assertEqual((a["dimension"], a["score"], a["observed"]), (b["dimension"], b["score"], b["observed"]))
        self.assertEqual(obj["reconstruction"], before["reconstruction"])
        self.assertEqual(rce_roles.normalize_review(obj), 0)


if __name__ == "__main__":
    unittest.main()
