# office-hours-hardmode

A Claude Code skill that lets your AI advisor **interrupt you** and **give you one order with a deadline** — the two things real startup office hours do that AI advice normally doesn't.

Works standalone, or as a layer on top of [gstack](https://github.com/garrytan/gstack)'s `/office-hours`.

---

## What it does (the difference)

AI advisors answer the question you asked. Good human advisors often refuse to.

### Difference #1: it can take the session away from you

**Normal AI office hours**

> **You:** I want to figure out our pricing page — three tiers or usage-based?
>
> **AI:** Great question. Let's think through both. Usage-based aligns cost with value and tends to work well when consumption varies a lot across customers. Three tiers is simpler to communicate and easier to forecast. A few things to consider…

You get a thoughtful answer to the wrong question, and you leave feeling productive.

**With this skill**

> **You:** I want to figure out our pricing page — three tiers or usage-based?
>
> **AI:** We're not doing pricing today. You said your co-founder "hasn't really been around since March," and you're still split 50/50. That decides whether the pricing page ever matters — nobody funds that cap table and nobody buys that company, so a perfect pricing page just builds something no one can acquire. Twenty minutes on this, then pricing. Yes?

The skill carries a fixed list of six things that outrank whatever you came in with: a co-founder situation, money running out, nobody having talked to a real customer, months of building without shipping, saying two things that can't both be true, and legal time bombs. If one of them shows up in your own words, the AI takes the session.

It can only do this **once per conversation**, only in the **first two exchanges**, and only when it can **quote you saying it**. If it can't point at something you actually said, it isn't allowed to bring it up. And if you say no twice, it drops it and goes back to your question.

### Difference #2: it gives you one instruction, not a document

**Normal AI office hours**

> **AI:** Here's a summary of our discussion, with recommendations across three areas: (1) customer discovery — you might want to consider talking to more users; (2) positioning — it could be worth clarifying your value proposition; (3) pricing — one option would be to test…

Nine things to do means zero things done.

**With this skill**

> **DIRECTIVE:** Call the three customers who cancelled in July and ask what they're using instead.
> **BY:** August 20
> **VERIFY:** You can say all three replacements out loud.
> **EXPECT:** At least two of them went back to a spreadsheet, which means your real competitor isn't a company.
> **KILL:** If none of them can name a replacement, nobody was solving this problem, including you.

One sentence. A date. A test someone else could check. And a prediction — so if the AI is wrong, you'll know, and so will it.

### Difference #3: it remembers, and it asks

The next time you open office hours, the **first thing** it says isn't "what are you working on?" It's:

> Last time you said you'd call the three customers who cancelled in July, by August 20. The test was: you can name all three replacements out loud. Did you?

Then it grades the answer as **done**, **partial**, **not done**, or **avoided** — and says which one out loud. "Avoided" means you changed the subject, and it will tell you that's what you did.

Skip two in a row and that pattern becomes the next session's topic, whether you like it or not.

### Difference #4: it's allowed to say the idea is dead

Most AI will not tell you to stop. This skill can — but only when it can count **three or more** specific conditions and show you the evidence for each. Below three, it's required to give you a hard instruction instead.

It's never allowed to kill something with paying customers. And when it does say it, it has to name what's worth carrying out of the wreckage, and hand you the one piece of evidence that would change its mind.

---

## Why

Real startup office hours work because of things that aren't in the advice.

The partner has seen thousands of companies, so they know the base rate. They have money in your company, so you can't just ignore them. They see you again next week, so the thing you promised is real. And they'll cut you off in the first ninety seconds, because they've already spotted the actual problem and it isn't the one you booked the meeting about.

When you turn that into a text file, almost all of it evaporates. Garry Tan, who open-sourced his version, put it at [about 90% of the power lost](https://x.com/garrytan/status/2052836328862277805).

Most of that loss is unrecoverable in software. You can't give an AI a decade of pattern-matched priors, and you can't give it equity in your company.

But two of the missing pieces are just **permissions and memory**:

1. Advisors interrupt. AI is trained to be helpful, and being helpful means answering what you asked. That's a rule you can change.
2. Advisors commit you to one thing and then check. That's a text file with a date in it.

That's the whole idea here. Not a smarter model — a rude one with a calendar.

---

## How

### Install (30 seconds)

```bash
git clone https://github.com/YOUR_USERNAME/office-hours-hardmode.git \
  ~/.claude/skills/office-hours-hardmode
```

That's it. Claude Code picks up skills in that folder automatically.

### Use it

Open Claude Code in your project and say any of:

- `/office-hours-hardmode`
- "office hours"
- "is this worth building?"
- "help me think through this idea"

Then talk normally. Describe what you're building and what you're stuck on. The skill handles the rest.

**A session looks like this:**

1. It asks whether you did last week's thing (skipped if it's your first time)
2. It either engages with your topic, or takes the session somewhere else and tells you why
3. You talk
4. It gives you one instruction with a date
5. It writes that down and stops talking

Sessions run 15–30 minutes. If it feels comfortable the whole way through, something has gone wrong.

### Where your commitments are stored

Plain text on your machine, nowhere else:

```
~/.gstack/projects/<your-repo>/commitments.jsonl     # if you have gstack
~/.office-hours/<your-repo>/commitments.jsonl        # if you don't
```

One line per session. Readable, editable, deletable. Nothing is uploaded anywhere.

### Using it with gstack

If you already run [gstack](https://github.com/garrytan/gstack), this wraps its `/office-hours` rather than replacing it. It takes over the opening and the ending, and leaves the six forcing questions in the middle alone.

Full instructions are in the **"Grafting onto gstack /office-hours"** section of [`SKILL.md`](SKILL.md) — three small edits.

---

## What this does *not* fix

Being honest about the limits, since the whole point is honesty:

- **It has no track record.** It can't tell you "I've seen forty teams try this, two made it." That knowledge isn't public and can't be written into a file.
- **It has no stake in your company.** A YC partner's advice lands partly because they wrote you a check. This one didn't.
- **You can delete the file.** The accountability loop only works if you don't cheat, and you can cheat in about two seconds. If you're going to do that, this won't help you and neither will anything else.
- **It reads text, not people.** It can't see you hesitate before answering the co-founder question.

What's left is still worth having: an advisor that won't let you spend the hour on the comfortable question, and one instruction you have to answer for next week.

---

## Contributing

The most useful contributions are **rungs and patterns**, not features.

- Add a signal to the outranking ladder that catches a real failure you've seen
- Sharpen a directive template so it's more binary
- Report a false hijack — a time it interrupted you for a bad reason. Those matter most.

Open an issue with the transcript (redact freely) and what it should have done instead.

---

## Credits

Builds on the office-hours skill from [garrytan/gstack](https://github.com/garrytan/gstack) (MIT). The forcing questions are Garry's; the interrupt and the commitment loop are the missing pieces this adds.

MIT licensed. See [LICENSE](LICENSE).
