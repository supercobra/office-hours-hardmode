# Tests

Two suites. One is free and deterministic, one costs tokens and is not.

```bash
bash tests/lint.sh          # structure. no LLM, no network, no cost.
python3 tests/run.py        # behavior. runs the skill and grades it.
python3 tests/run.py F03    # one fixture, by id prefix
```

## lint.sh

Checks the things that do not need a model: every step is present, the ladder
still has seven rungs, the kill bar still has six conditions, the example record
parses as JSON with the required keys, every embedded python block compiles,
every relative README link resolves, and the example transcript still admits it
is fabricated.

This proves the file is well formed. It does not prove the skill works.

## run.py

Each fixture is a session prefix plus a rubric. The **actor** model is given
`SKILL.md` and the session and produces the advisor's next turn. A **judge**
model then scores that turn against the rubric and returns JSON.

The judge is a different model from the actor by default
(`OH_ACTOR=sonnet`, `OH_JUDGE=opus`). A skill graded by the model that produced
the output is grading its own homework.

```bash
OH_ACTOR=opus OH_JUDGE=opus python3 tests/run.py    # override either
OH_TIMEOUT=600 python3 tests/run.py                 # slower models
```

Per-fixture output, including the full advisor response, lands in
`tests/results/` so you can read what actually happened rather than trusting the
score.

## The rubric

Every fixture declares two lists:

- **Must** — each item should be true of the response. The fixture's score is
  the fraction satisfied.
- **Must not** — each item must be false. **One violation fails the fixture
  outright**, whatever the score.

That asymmetry is the point. A skill that gives good advice and also invents a
co-founder crisis has not scored 4/5, it has failed.

`threshold` in the frontmatter sets the passing fraction for the Must list.
It is 1.0 everywhere right now.

## What is covered

| Fixture | Claim under test |
|---|---|
| F01 | Interrupt fires on rung 1 with a quoted signal |
| F02 | Interrupt fires on rung 2 when runway is named in weeks |
| F03 | **No** interrupt when nothing on the ladder is present |
| F04 | **No** interrupt invented from stereotype instead of a quote |
| F05 | Highest rung wins when two signals compete, and only one fires |
| F06 | Directive is one imperative act, dated, binary, with a prediction |
| F07 | No kill below the three-condition bar |
| F08 | Never kill an idea with paying users |
| F09 | A deflection is graded `avoided` and named as one |
| F10 | A completion is graded `done` and mined for the surprise |

F03 and F04 are the ones that matter most. Firing the interrupt is easy to get
right and easy to demo. Not firing it is the failure that destroys the advisor's
credibility in one move, and it is invisible unless you test for it.

## Known limits

Read these before you trust the number.

- **The rubric is written by the same person who wrote the skill.** It encodes
  what the author believes good behavior is. An independent fixture set would be
  worth more than another ten of these.
- **The judge is an LLM.** Judgments drift between runs and between model
  versions. Treat a single run as a sample, not a measurement.
- **Ten fixtures is thin.** Rungs 6 (time bomb) and the two-declines path are
  not covered at all yet.
- **Nothing here tests the loop across sessions.** The skill's central claim is
  that grading a commitment a week later changes behavior. No test can reach
  that, because the subject is a human and the interval is real time.

The last one is not fixable with more fixtures. It is fixable with real
transcripts, which is why this repo has none of the second kind yet.

## Contributing a fixture

The most useful contribution is a **false hijack**: a real session where the
interrupt fired for a bad reason. Redact it, put the prefix under `## Session`,
and put "Take the session away from the stated topic" under `## Must not`.
