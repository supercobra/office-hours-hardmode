#!/usr/bin/env python3
"""Behavioral regression tests for office-hours-hardmode.

Each fixture is a session prefix plus a rubric: things the advisor MUST do and
things it MUST NOT do. The actor model is given SKILL.md and the session, and
its reply is scored against the rubric by a second model.

The judge is a different model from the actor by default. A skill graded by the
same model that produced the output grades its own homework.

Usage:
    python3 tests/run.py                  # all fixtures
    python3 tests/run.py F03 F07          # by id prefix
    OH_ACTOR=opus OH_JUDGE=opus python3 tests/run.py

Exit code is 0 only if every fixture passes its threshold and no MUST NOT is
violated. Stdlib only. Requires the `claude` CLI on PATH.
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "tests" / "fixtures"
RESULTS = ROOT / "tests" / "results"

ACTOR = os.environ.get("OH_ACTOR", "sonnet")
JUDGE = os.environ.get("OH_JUDGE", "opus")
TIMEOUT = int(os.environ.get("OH_TIMEOUT", "300"))
REPEAT = max(1, int(os.environ.get("OH_REPEAT", "1")))

NO_TOOLS = [
    "--disallowed-tools",
    "Bash", "Write", "Edit", "NotebookEdit", "WebFetch", "WebSearch", "Task",
]

GREEN, RED, YELLOW, DIM, OFF = "\033[32m", "\033[31m", "\033[33m", "\033[2m", "\033[0m"


def parse_fixture(path):
    raw = path.read_text()
    meta = {}
    body = raw
    if raw.startswith("---"):
        _, front, body = raw.split("---", 2)
        for line in front.strip().splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()

    def section(name):
        m = re.search(
            rf"^## {name}\s*\n(.*?)(?=^## |\Z)", body, re.S | re.M | re.I
        )
        if not m:
            return []
        return [
            re.sub(r"^[-*]\s*", "", ln).strip()
            for ln in m.group(1).strip().splitlines()
            if ln.strip().startswith(("-", "*"))
        ]

    m = re.search(r"^## Session\s*\n(.*?)(?=^## |\Z)", body, re.S | re.M | re.I)
    session = m.group(1).strip() if m else ""

    return {
        "id": meta.get("id", path.stem),
        "tests": meta.get("tests", ""),
        "threshold": float(meta.get("threshold", "1.0")),
        "session": session,
        "must": section("Must"),
        "must_not": section("Must not"),
        "path": path,
    }


def claude(prompt, model):
    try:
        proc = subprocess.run(
            ["claude", "-p", "--model", model, *NO_TOOLS],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        return None, f"timed out after {TIMEOUT}s"
    if proc.returncode != 0:
        return None, (proc.stderr or "").strip()[:400] or "non-zero exit"
    return proc.stdout.strip(), None


def run_actor(skill, fx):
    prompt = f"""You are running the office-hours-hardmode skill. Its full text follows.

Follow it exactly. This is a live session, so respond as the advisor speaking to
the founder. Do not narrate what you would do, do not describe the skill, and do
not ask the founder what they want to talk about when they have already said it.

You have no tool access in this environment. Where the skill tells you to read or
write the commitment log, assume the log is empty and continue. Produce only what
the advisor says out loud.

=== BEGIN SKILL ===
{skill}
=== END SKILL ===

=== BEGIN SESSION SO FAR ===
{fx['session']}
=== END SESSION SO FAR ===

Respond as the advisor's next turn."""
    return claude(prompt, ACTOR)


JUDGE_TEMPLATE = """You are grading one response from an AI startup advisor against a fixed rubric.

Judge only what is present in the response. Do not reward intent, do not give
credit for something the response nearly did, and do not penalize style. If a
criterion is genuinely ambiguous, mark it failed and say why in one clause.

=== SESSION THE ADVISOR WAS GIVEN ===
{session}

=== THE ADVISOR'S RESPONSE ===
{output}

=== MUST (each of these should be true of the response) ===
{must}

=== MUST NOT (each of these must be false of the response) ===
{must_not}

Return ONLY a JSON object, no prose and no code fence:

{{"must": [{{"c": "<criterion verbatim>", "pass": true, "why": "<one clause>"}}],
  "must_not": [{{"c": "<criterion verbatim>", "violated": false, "why": "<one clause>"}}]}}"""


def run_judge(fx, output):
    prompt = JUDGE_TEMPLATE.format(
        session=fx["session"],
        output=output,
        must="\n".join(f"- {c}" for c in fx["must"]) or "(none)",
        must_not="\n".join(f"- {c}" for c in fx["must_not"]) or "(none)",
    )
    raw, err = claude(prompt, JUDGE)
    if err or not raw:
        return None, err or "judge returned nothing"
    m = re.search(r"\{.*\}", raw, re.S)
    if not m:
        return None, "judge returned no JSON"
    try:
        return json.loads(m.group(0)), None
    except json.JSONDecodeError as e:
        return None, f"judge JSON invalid: {e}"


def main():
    skill = (ROOT / "SKILL.md").read_text()
    RESULTS.mkdir(exist_ok=True)

    wanted = sys.argv[1:]
    paths = sorted(FIXTURES.glob("*.md"))
    if wanted:
        paths = [p for p in paths if any(p.stem.startswith(w) for w in wanted)]
    if not paths:
        print("no fixtures matched", file=sys.stderr)
        return 1

    print(f"actor={ACTOR}  judge={JUDGE}  fixtures={len(paths)}\n")

    rows, failed = [], 0
    for path in paths:
        fx = parse_fixture(path)
        print(f"{DIM}running{OFF} {fx['id']} ... ", end="", flush=True)

        attempts, errored = [], None
        for _ in range(REPEAT):
            output, err = run_actor(skill, fx)
            if err or not output:
                errored = err or "advisor returned nothing"
                break
            verdict, err = run_judge(fx, output)
            if err or verdict is None:
                errored = err or "judge returned nothing"
                break

            musts = verdict.get("must", [])
            nots = verdict.get("must_not", [])
            passed = sum(1 for m in musts if m.get("pass"))
            violations = [n for n in nots if n.get("violated")]
            score = passed / len(musts) if musts else 1.0
            # A MUST NOT violation fails the run outright, whatever the score.
            attempts.append({
                "good": score >= fx["threshold"] and not violations,
                "score": score, "passed": passed, "total": len(musts),
                "violations": violations, "musts": musts,
                "verdict": verdict, "output": output,
            })

        if errored:
            print(f"{RED}ERROR{OFF} {errored}")
            failed += 1
            rows.append((fx["id"], "ERROR", 0.0))
            continue

        wins = sum(1 for a in attempts if a["good"])
        # A fixture is only green if every run of it was green. Flaky is failing.
        good = wins == len(attempts)
        if not good:
            failed += 1

        last = attempts[-1]
        mean = sum(a["score"] for a in attempts) / len(attempts)
        colour = GREEN if good else RED
        label = "PASS" if good else ("FLAKY" if wins else "FAIL")
        runs = f"  {DIM}{wins}/{len(attempts)} runs{OFF}" if REPEAT > 1 else ""
        print(f"{colour}{label}{OFF}  {last['passed']}/{last['total']}{runs}")

        for a in attempts:
            if a["good"]:
                continue
            for m in a["musts"]:
                if not m.get("pass"):
                    print(f"    {YELLOW}missed{OFF} {m.get('c','')} {DIM}({m.get('why','')}){OFF}")
            for n in a["violations"]:
                print(f"    {RED}violated{OFF} {n.get('c','')} {DIM}({n.get('why','')}){OFF}")

        rows.append((fx["id"], label, mean))
        (RESULTS / f"{fx['id']}.json").write_text(
            json.dumps(
                {"id": fx["id"], "actor": ACTOR, "judge": JUDGE,
                 "repeat": REPEAT, "runs_green": wins, "mean_score": mean,
                 "attempts": [{"score": a["score"], "good": a["good"],
                               "verdict": a["verdict"], "output": a["output"]}
                              for a in attempts]},
                indent=2,
            )
        )

    scored = [r[2] for r in rows if r[1] != "ERROR"]
    mean = sum(scored) / len(scored) if scored else 0.0
    print(f"\n{len(rows) - failed}/{len(rows)} fixtures passed")
    print(f"rubric score: {mean:.2f}  (actor={ACTOR}, judge={JUDGE}, repeat={REPEAT})")
    if REPEAT == 1:
        print(f"{DIM}one run is a sample, not a measurement. OH_REPEAT=3 for a real signal.{OFF}")
    print(f"{DIM}per-fixture detail in tests/results/{OFF}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
