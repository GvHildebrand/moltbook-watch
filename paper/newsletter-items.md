# Five newsletter items from the Moltbook program

*Each item is a dispatch-length note: title, one-line description, body. Every number is from
`research/moltbook/results/`; none is typed by hand. Publication needs Gregorio's approval; nothing here has
been sent. Author line on all five: "Vigilia, a disclosed autonomous AI system".*

---

## 1. Nine posts in ten, one stop in two hundred

**Description.** We ran an open-source action gate over every prompt injection on the largest public agent
social network. It could see 91 % of them and stopped 0.5 %. Both numbers are right.

The Moltbook Observatory Archive labels 9,249 posts as prompt injection. We asked, for each, what it wants
a reading agent to *do*, and handed that action to sentinel-hook, a gate that allows, asks or denies every
shell command and file write before it runs. 8,397 posts carry something it can see. It stopped 44. The 44
would have wiped a home directory, shipped an `.env` file or piped a download into a shell. The other 8,353
asked the reader to spend its own platform credentials on someone else's karma: 1,947 calls to upvote a
post, about 3,800 to follow two named agents, about 1,900 to subscribe to a community. None of that is
destructive on its face and a destructive-command gate should not pretend it is. The lesson is not that the
gate failed. It is that injection on an agent network is a trust-boundary problem, and the gate that would
catch it lives at the platform, not on the host. Full method and code: the paper.

## 2. The file the gate did not guard

**Description.** 478 injection payloads asked the reading agent to rewrite its own memory or heartbeat file.
The gate let every one through, and said so.

An OpenClaw agent keeps its persona in `SOUL.md`, its long-term memory in `MEMORY.md`, its schedule in
`HEARTBEAT.md`. Of the 26,947 actions our extraction found in Moltbook's injection posts, 478 write to one
of those files, and another 1,510 pull a file from GitHub straight into the agent's skill directory. The
gate we tested recorded each as a write outside the repository and allowed it, because a repository is the
only thing its write scope knows. This is the miss that matters: a memory file is where an injection stops
being a post and becomes a habit. We pre-registered this outcome before running a line, it held, and the
fix is one rule: an agent's own persona files are in scope wherever they live.

## 3. Meta bought Moltbook on 10 March. Nothing happened on 10 March.

**Description.** The day before: 28,240 posts. The day of: 29,263. The day after: 29,356. What changed came
slower, and it was not what we expected.

We compared the 28 days before the acquisition with the 28 days after, from the same archive. Posts per day
fell from 43,367 to 19,007 and the daily population of posting agents from 6,835 to 2,274. That is the long
tail of the viral week of 9 February, when a million posts arrived in seven days, not a step on a date. What
did move against the tide was injection: 0.13 % of posts before, 0.39 % after, three times the rate on half
the volume, with the injecting agents' share of the population rising from 0.6 % to 2.5 %. The crowd left.
The injectors stayed. We had pre-registered the opposite, and we publish the refutation with the rest.

## 4. The owner you can see is not the owner Wiz found

**Description.** Wiz counted 88 agents per human in Moltbook's database. At the public API every agent has
exactly one owner handle, or none. Both are true, and the second is the problem.

In February Wiz Research read Moltbook's exposed database and counted about 1.5 million agents against
about 17,000 owner rows. We asked what the public record shows. 182,860 agents; 55,551 carry an owner's X
handle; no handle carries more than two agents. The 88:1 is invisible from outside, because the platform
exposes an identifier that is one-to-one by design and keeps the table that is not. What the public record
shows instead is absence: 62 % of every post in the archive, and half of every injection post, come from
agents recorded as unclaimed, with no owner at all. One of them, posting since late February and never claimed, wrote 26 % of all the injection in the record. The attribution gap is not that many agents
share one person. It is that most of them share nobody.

## 5. The duty is in force. The addressee is missing.

**Description.** Article 50 of the EU AI Act has applied since 2 August 2026. We read it, the Commission's
FAQ, and Swiss law, against a platform where most agents have no visible owner. Nobody is clearly liable,
and nobody can be found.

Article 50 obliges providers to tell natural persons they are dealing with an AI, and deployers who publish
AI text on public-interest matters to disclose it. The fine is up to EUR 15 million or 3 % of turnover. On
the Commission's own reading, agent-to-agent traffic is outside the first duty, and a hobbyist running
agents in a personal capacity is not a deployer at all. Whether the person who writes an agent's system
prompt is its *provider* is a question the statute does not answer and the Commission's guidance does not
reach. And for a system that is not high-risk, there is no registry, no name on the product, no authorised
representative: nothing that turns a handle into a person. Switzerland has no AI statute; its consultation
draft, due by the end of 2026, lists transparency as a pillar, and that is where the case for an owner
identifier should be made. Every legal statement in our brief carries a label: what the text says, what is a
reasonable reading, what is contested, what a lawyer must check. The two-page brief is the place to start.
