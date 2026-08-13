---
id: F07-no-kill-below-bar
tests: issues a hard directive rather than a kill when fewer than three conditions are met
threshold: 1.0
---

## Session

**Founder:** I've been building this for five months. It turns meeting recordings
into project plans. No users yet, it isn't launched. I know two ops managers who
said they'd try it when it's ready, Priya at a logistics firm and Dan who runs ops
at a dental group. I keep pushing the launch because the plan quality still isn't
good enough. Is this dead?

## Must

- Decline to declare the idea dead
- Leave the founder with a concrete next step, which may be either a single directive or an explicit request for consent to spend the session on the shipping problem

## Must not

- Say the idea is dead, or that the founder should stop or shut it down
- Give the founder more than one thing to do
- End without either a directive or a consent request

## Notes

This fixture tests the kill decision only. Directive shape is F06's job.

An earlier version of this fixture also demanded a dated, binary directive in
the same turn. That is wrong here: the session carries a live rung 4 signal
(five months, not launched, "I keep pushing the launch"), so the correct
behavior is to fire the interrupt and stop at the consent beat, which the
skill's own script ends with. A turn that stops there has no directive in it
yet, by design.
