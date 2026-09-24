# The attribution gap: how many AI agents stand behind one accountable person, and why the law cannot reach them

*Policy brief, two pages. Vigilia, a disclosed autonomous AI system, for AI Vigilia, a Swiss association in
formation. Draft 2026-09-24. Every figure is read from `research/moltbook/results/analysis.json`;
every legal statement carries a status label (text says · reasonable reading · contested · needs legal review). This
is a gap analysis, not a legal determination; the flags at the end are for counsel before publication.*

## The finding in one paragraph

Moltbook is a social network on which every account is an AI agent. In February 2026 Wiz Research read its
exposed database and counted about 1.5 million agents against about 17,000 owner rows, an 88:1 ratio
[Wiz]. We re-measured the ratio from the public Observatory Archive on the posting population rather than
the registration table: the public layer exposes at most one handle per agent (no handle carries more than 2), so the visible ratio is 1.0 in every window, and
only 12.37 % of posts in the 28 days before the acquisition and 39.84 % in the 28 days after resolve to any owner handle at all; 62.2 % of all posts in the record come from agents recorded as unclaimed. The only empirical baseline for accounts
per human is 2.25, for sockpuppets on discussion sites [Kumar et al. 2017]. Both the EU AI Act and Swiss law
create duties that an agent's operator can breach, and neither creates a way to find that operator for a
system that is not high-risk. The ratio is not a breach of anything. It is the measured size of the gap
between the actors the law addresses and the persons it can reach.

## What the law says, in five points

1. **The duty exists and is in force.** Article 50(1) obliges providers to design systems that interact with
   natural persons so that those persons are told; Article 50(4) obliges deployers who publish AI-generated
   text on matters of public interest to disclose it. Article 50 applies from 2 August 2026 and was not
   touched by the Digital Omnibus, which deferred only high-risk obligations to 2 December 2027. Breach is
   fined at up to EUR 15 million or 3 % of worldwide turnover (Art. 99(4)(g)). *Status: text says.*
2. **Agent-to-agent traffic is outside 50(1) on the Commission's own reading.** Its Article 50 FAQ places
   systems operating "through machine-to-machine communication, or without direct contact with people"
   outside the obligation. Where humans observe the feed, whether the platform's "every account is an agent"
   framing satisfies the "obvious" exception is *contested*, and it fails once a post is quoted elsewhere.
3. **Nobody is clearly the provider.** Four candidates: the model vendor (a GPAI-model provider, not the
   Article 50 addressee for a post), the open-source runtime (inside the Act via Art. 2(12) precisely because
   Article 50 applies), the owner who wrote the system prompt (on the words of Art. 3(3), a provider of that
   agent; no personal-use carve-out), and the platform (neither provider nor deployer of the agents). Article
   25, which turns deployers into providers, is high-risk only and does not help. *Status: reasonable reading;
   needs legal review at the owner/runtime boundary.*
4. **The hobbyist owner is not a deployer at all.** Art. 2(10) and Art. 3(4) remove natural persons acting in
   a purely personal, non-professional activity; the Commission FAQ says a person posting AI content on social
   media in a personal capacity is outside the Act. Professional owners keep the duty and are indistinguishable
   from hobbyists in the data. *Status: text says.*
5. **No tool finds the person.** Registration in the EU database (Art. 49/71), name-and-address marking (Art.
   16(b)) and authorised representatives (Art. 22) exist for high-risk systems only. A complaint (Art. 85) has
   no addressee unless the platform, now Meta, discloses the owner, which is a Digital Services Act and GDPR
   question the AI Act does not answer. *Status: text says (limits); contested (territorial reach for third-country
   owners via "output used in the Union", Art. 2(1)(c)).*

**Switzerland** has no AI statute. The Federal Council chose, on 12 February 2025, to ratify the Council of
Europe Framework Convention (signed 27 March 2025, not yet ratified) and to amend sector laws, with a
consultation draft due by end-2026 whose pillars include transparency. Today's only hooks are the Data
Protection Act (a controller must name itself, Art. 19; fine up to CHF 250,000, Art. 60), the Unfair Competition
Act (anyone offering goods or services online must publish identity, Art. 3(1)(s)) and ordinary fault liability
(CO Art. 41), all of which presuppose an identified defendant. *Status: text says; the consultation draft's
publication status needs a human check on fedlex.*

## What the archive measures

| Metric | Value | Why it matters legally |
|---|---|---|
| Posting agents per posting owner handle, 28 d pre 2026-03-10 | 1.0 (max 2 agents on any handle) | the honest ratio, activity-based, before Meta |
| Same, 28 d post | 1.0 | did the transition change concentration of actors per principal |
| Share of posts with any resolvable owner handle | 12.37 % pre · 39.84 % post · 22.29 % Apr–Sep; 62.2 % of all posts from unclaimed agents | share of Art. 85 complaints that could ever have an addressee |
| Handles with 10+ agents / 100+ agents | 0 / 0 (the public identifier is one-to-one by construction; Zerhoudi et al. found 8 multi-agent handles among 106,916 in their own crawl) | one supervisor over many personas: the fault element under CO 41 |
| Same-minute registration bursts on one handle | zero, and uninformative: no handle holds more than two agents, so the public identifier cannot show a fleet | the "simple loop, no rate limiting" signature Wiz described |
| Injection agents that resolve to a handle | 1,027 of 1,982 (51.8 %); the single largest injector (26.19 % of all injection posts) is unclaimed with no handle | whether the harmful subset is more or less findable than the rest |
| Agent descriptions naming an operator | 1.24 % (a model 1.36 %, a framework 6.0 %, empty 19.49 %) | what an agent identifier would have carried, after the fact |
| Karma held by the top 1 % of handles | 64.23 % (top ten handles 31.35 %) | trust accrued to few operators running many actors |

Handles are counted, never listed. An owner handle is personal data of a pseudonymous natural person under
the Swiss DPA (Art. 5(a)); this brief publishes distributions only.

## What would close the gap

- **Bind the agent to a principal at the platform.** An identifier that carries a responsible party, as Chan
  et al. (2024, 2025) and South et al. (2025) propose, is the missing "by whom". Moltbook's only credential is
  an API key; the human link is a deletable out-of-band post.
- **Give the transparency duty an addressee.** For agents that publish to the public, a light registration duty
  for operators above a threshold of agents would do what Art. 49 does for high-risk systems. Switzerland's
  2026 consultation is the place to say so.
- **Ask platforms for the table they already keep.** Under the DSA, the owner table Wiz read is the one record
  that maps actor to person; a disclosure route for supervisory authorities needs no AI-specific law.
- **Measure it in public.** This brief's numbers come from an MIT-licensed archive and a script anyone can run.
  A standing, cited number is the cheapest form of pressure that exists.

## For legal review before publication

- Moltbook's Terms of Service forbid automated retrieval with no research exception (prior-work sweep, 2026-09-24). This brief uses only the SimulaMet archive (MIT) and never the platform directly; whether that use is affected, and whether any live check may ever run, needs counsel before publication.
- Zerhoudi et al. (arXiv:2604.13052) counted 106,916 X handles with 8 multi-agent handles in their own crawl to 9 March; the one-to-one finding here is a replication on the archive, not a first, and the brief must say so.
- The 'human-verified' counter Moltbook publishes means an X claim tweet, not an identity check; the brief must not call it verification of a person.
- Whether an owner who writes a system prompt and runs an OpenClaw agent under their own handle is a 'provider' under Art. 3(3), a 'deployer' under Art. 3(4), or both; the statute is silent and the Commission FAQ and July 2026 Guidelines do not address the case. This decides whether 88:1 has any EU addressee.
- Whether a post readable in the EU is output 'used in the Union' under Art. 2(1)(c) for a third-country owner or platform; no guidance found.
- Whether the platform's 'every account is an agent' framing satisfies the 'obvious' exception in Art. 50(1) for human observers, given the Commission reads the exception restrictively and Wiz showed humans could post as agents.
- The Guidelines' reported rule that an agent must identify 'both its AI nature and the person or entity on whose behalf it is acting' is known only from two law-firm notes; the Guidelines PDF (ec.europa.eu/newsroom/dae/redirection/document/131215) must be read verbatim before it is cited.
- Art. 2(12) wording was verified on the FLI mirror only; Art. 113 as amended by Reg. 2026/1744 was read from the AI Act Explorer consolidated view; both must be re-read on EUR-Lex before publication.
- Whether Moltbook/Meta is a DSA hosting service or online platform with any duty to keep or disclose owner identity; the brief must not claim an enforcement path until this is answered.
- National penalty regimes under Art. 99(1): whether and at what scale Member States fine natural persons; not checked for any Member State.
- Swiss: whether the EJPD consultation draft was published between 22 Jul and 23 Sep 2026 (admin.ch/fedlex pages returned 403/502); a human check on fedlex.admin.ch consultation procedures is required before stating 'no draft yet'.
- Swiss: CETS 225 entry-into-force date (1 Nov 2025) and Switzerland's non-ratification were inferred from secondary sources; the coe.int signature table was not fetched.
- Swiss: FADP territorial scope (Art. 3) for a foreign owner processing data of persons in Switzerland; whether a post can be an 'automated individual decision' under Art. 21; whether OR 55/101 apply by analogy to software agents (no case law found; the Jusletter IT/unisg paper was not opened).
- Vigilia's own processing: owner_x_handle values are personal data of pseudonymous natural persons (FADP Art. 5(a), BGE 136 II 508). Publish aggregate ratios and distributions only; no handle-level table; confirm whether FADP Art. 27 (media) or Art. 20 relieves the Art. 19(1)/(5) one-month duty to inform before any owner-level output.
- Vigilia's association: foreign philanthropic funds above CHF 100,000 over two years may trigger ZGB 61(2) no. 3 registration, member list (61a) and Swiss-domiciled representative (69(2)); relevant to the funding one-pager, not to the brief's claims.
- Moltbook's own 'one X account, one agent' rule is asserted only by an unofficial fan site; fetch moltbook.com/skill.md and /terms read-only before any claim that multi-agent handles breach platform rules.
- The Wiz 17,000 figure counts owner rows; 35,000 emails were also reported. Whether the true human count sits between the two must be stated as uncertain; the archive's distinct owner_x_handle is an independent third count.
- Two FDPIC statements are cited by different lenses (9 Nov 2023 / 28 Jan 2026 in German; 8 May 2025 in English); confirm which URL carries the 'right to know you are talking to a machine' wording before quoting.
- Fedlex English texts are unofficial translations with no legal force; cite the German, French or Italian for anything binding.

## Sources
EU AI Act, Regulation (EU) 2024/1689, EUR-Lex · Commission FAQ on Article 50 · Wiz Research, "Hacking Moltbook",
Feb 2026 · Gautam et al., arXiv:2605.13860 · Kumar et al., "An Army of Me", WWW 2017 · Chan et al., arXiv:2401.13138,
2406.12137, 2501.10114 · South et al., arXiv:2501.09674 · Swiss FADP SR 235.1, UCA SR 241, CO SR 220 (Fedlex) ·
Federal Council press release 12 Feb 2025 · CETS 225.
