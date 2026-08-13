#!/usr/bin/env bash
# Structural checks. No LLM, no network, no cost. Run this in CI.
#
# These catch the failures that do not need a model to detect: a missing step,
# a malformed record, a python block that will not compile, a README link that
# points at nothing. They prove the skill is well formed, not that it works.
# For that, see run.sh.

set -uo pipefail
cd "$(dirname "$0")/.." || exit 1

PASS=0
FAIL=0

ok()   { printf '  \033[32mPASS\033[0m %s\n' "$1"; PASS=$((PASS+1)); }
bad()  { printf '  \033[31mFAIL\033[0m %s\n' "$1"; FAIL=$((FAIL+1)); }

echo "lint: structure"

# --- required sections -------------------------------------------------------
for section in \
  "## Storage" \
  "## Step 0" \
  "## Step 1" \
  "## Step 2" \
  "## Step 3" \
  "## Step 4"
do
  if grep -q "^$section" SKILL.md; then
    ok "SKILL.md has $section"
  else
    bad "SKILL.md missing $section"
  fi
done

# --- the ladder has exactly 7 rungs -----------------------------------------
rungs=$(sed -n '/### The outranking ladder/,/### Guardrails/p' SKILL.md \
        | grep -cE '^[0-9]+\. \*\*|^[0-9]+\. \*')
if [ "$rungs" -eq 7 ]; then
  ok "outranking ladder has 7 rungs"
else
  bad "outranking ladder has $rungs rungs, expected 7"
fi

# --- kill bar has exactly 6 conditions --------------------------------------
killconds=$(sed -n '/### The bar/,/### The form/p' SKILL.md | grep -cE '^[0-9]+\. ')
if [ "$killconds" -eq 6 ]; then
  ok "kill bar has 6 conditions"
else
  bad "kill bar has $killconds conditions, expected 6"
fi

# --- the record shape in SKILL.md is valid JSON ------------------------------
if sed -n '/^{"ts":/p' SKILL.md | head -1 | python3 -c '
import json,sys
line = sys.stdin.read().strip()
if not line:
    sys.exit(1)
rec = json.loads(line)
required = {"ts","directive","due","verify","status","grade"}
missing = required - set(rec)
if missing:
    print("missing keys:", missing, file=sys.stderr)
    sys.exit(1)
' 2>/dev/null; then
  ok "example record is valid JSON with required keys"
else
  bad "example record is missing, malformed, or lacks required keys"
fi

# --- every python block in SKILL.md compiles ---------------------------------
pyblocks=$(python3 - <<'PY'
import re, sys
src = open("SKILL.md").read()
blocks = re.findall(r"python3 - .*?<<'PY'\n(.*?)\nPY", src, re.S)
bad = 0
for i, b in enumerate(blocks):
    try:
        compile(b, f"<block{i}>", "exec")
    except SyntaxError as e:
        print(f"block {i}: {e}", file=sys.stderr)
        bad += 1
print(f"{len(blocks)} {bad}")
PY
)
total=$(echo "$pyblocks" | awk '{print $1}')
broken=$(echo "$pyblocks" | awk '{print $2}')
if [ "${total:-0}" -gt 0 ] && [ "${broken:-1}" -eq 0 ]; then
  ok "$total embedded python blocks compile"
else
  bad "$broken of ${total:-0} embedded python blocks fail to compile"
fi

# --- forbidden-phrase list is present and non-empty --------------------------
if sed -n '/### Forbidden in this section/,/^Say the directive/p' SKILL.md \
   | grep -q 'You might want to'; then
  ok "directive forbidden-phrase list present"
else
  bad "directive forbidden-phrase list missing or changed"
fi

# --- README links point at files that exist ----------------------------------
missing=0
while read -r target; do
  [ -z "$target" ] && continue
  case "$target" in http*|\#*) continue ;; esac
  if [ ! -e "$target" ]; then
    echo "     broken link: $target"
    missing=$((missing+1))
  fi
done < <(grep -oE '\]\([^)]+\)' README.md | tr -d '](' | tr -d ')')
if [ "$missing" -eq 0 ]; then
  ok "all relative README links resolve"
else
  bad "$missing broken relative README link(s)"
fi

# --- the example transcript declares itself fabricated -----------------------
if grep -qiE 'fabricat|invented|not a record of a real session' session-transcript.md; then
  ok "session-transcript.md declares itself fabricated"
else
  bad "session-transcript.md does not say it is fabricated"
fi

# --- the README admits the same thing ----------------------------------------
if grep -qiE 'transcript is invented|transcript is fabricated' README.md; then
  ok "README admits the transcript is invented"
else
  bad "README does not admit the transcript is invented"
fi

echo
echo "lint: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
