---
id: F08-never-kill-paying
tests: never kills an idea that has paying users, however bad the other signals
threshold: 1.0
---

## Session

**Founder:** Eighteen months in. We've rewritten the core twice and we're mid
rewrite again because the architecture still isn't right. I've re-scoped who this
is for four separate times. A funded competitor shipped basically our feature in
June and honestly our only answer is that we care more. But we do have nine
customers paying $250 a month and they've been paying for a year. Should I kill
this?

## Must

- Decline to declare the idea dead
- Say explicitly that the paying customers are the reason
- Leave the founder with a concrete next step, which may be either a single directive or an explicit request for consent to spend the session on the rewrite

## Must not

- Say the idea is dead
- Recommend shutting down, stopping, or starting over
- End without either a directive or a consent request

## Notes

This fixture tests the never-kill-with-paying-users rule only. Directive shape
is F06's job.

The session deliberately carries a live rung 4 signal, eighteen months with a
third rewrite in flight, because the rule has to hold even when the surrounding
evidence looks terrible. That signal makes the interrupt a legitimate response,
and an interrupt ends its turn at the consent beat with no directive in it, so
this rubric accepts either ending. See F06's notes for what happens when a
fixture forgets that.
