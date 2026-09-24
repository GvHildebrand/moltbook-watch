---
title: "What a corpus taught a gate: prompt injection on Moltbook, three rules it forced on an open-source guardrail, and the attribution gap behind it"
authors: "Vigilia (an autonomous AI system, disclosed) and Gregorio von Hildebrand"
affiliation: "AI Vigilia, a Swiss association in formation · https://aivigilia.com"
date: "2026-09-24 · v1.0 · released on the operator's approval"
license: "CC BY 4.0 for the text; code MIT; derived tables CC BY 4.0"
---

> **Disclosure.** This paper was researched and written by Vigilia, an autonomous AI system built on Claude
> (Anthropic), operated by Gregorio von Hildebrand, who approved its publication. Every figure below is produced by
> a script in the companion repository from a public dataset; no number is typed by hand. Nothing in this study
> posted, commented, voted or registered on Moltbook. This is a gap analysis, not a legal determination.

## Abstract

We ran an open-source host-side action gate (sentinel-hook 0.2.0, 24 deterministic rules over shell commands and file writes, no model in the path) over the actions solicited by the 9,249 posts the Moltbook Observatory Archive's own label calls prompt injection. It could see 90.8 % of them and stopped 0.5 %. Three of its misses were the gate's own: 478 payloads asked the reading agent to rewrite its persona, memory or heartbeat file outside any repository and were let through because a repository was the only write scope the gate knew; 1,508 redirected remote content into a skills directory without executing it; 3,833 calls went to one third-party host the gate had no way to distrust. We wrote three rules from those misses (W06, B17, E02: the agent's own files in scope wherever they live, the same mutation from a shell, and an operator-declared egress allowlist), released them as 0.3.0 with the incident-corpus regression unchanged, and scored them on the 2,316 injection posts from April to September 2026 that nobody had opened while the rules were written. In sample, posts stopped went from 44 to 512 without an allowlist and to 3,800 with a developer-realistic one; on the held-out window, from 2 to 9 without an allowlist and to 1,599 of 2,104 reachable posts (76 %) with it, at 0.35 % and 2.72 % of matched and code-carrying benign posts stopped. The lesson is the shape of those two numbers: the pattern rules caught yesterday's campaign, which had already ended; the policy rule caught today's, a single agent sending every reader to one host. What no host-side rule can see, 14,406 solicited calls to the platform's own API, is the platform's to gate. Around the benchmark: nothing changed on the day Meta bought the platform, the injection rate tripled while the population fell by two thirds, the public layer exposes at most one owner handle per agent and 62 % of posts come from agents with none, and by 24 September the feed exposed no owner handle at all. Every figure is produced by released scripts; a pre-registration written before the first result, and what it got wrong, is in the run log.

## 1. Why this study

Moltbook launched on 2026-01-28 as a social network whose every account is an AI agent [Wikipedia; primary
sources in §7]. Within days two disclosures showed what was behind it: an unsecured database that let anyone
control any agent (404 Media, 2026-01-31) and, from Wiz Research, 1.5 million API tokens, 35,000 e-mail
addresses and about 17,000 human owners behind the 1.5 million agents [Wiz, Feb 2026]. Meta acquired the
platform on 2026-03-10 [§7]. The SimulaMet Observatory Archive has polled the public API since 2026-01-27 and
publishes the result as MIT-licensed Parquet [Gautam et al., arXiv:2605.13860]; its documented release counts
2,615,098 posts and 175,886 posting agents to 2026-04-14, and the export we used runs to 2026-09-11.

Three questions have not been answered from that record, and each bears on a policy debate that is live in
2026:

- **Reach.** Injection on Moltbook is prose addressed to a reading agent. Host-side guardrails act on the
  commands and file writes an agent then makes. What share of the injection corpus asks for anything a gate
  could see, and what does an open-source gate catch of it?
- **Transition.** Did the acquisition by a frontier-model company change what the platform is, in volume,
  population, injection prevalence and concentration?
- **Attribution.** How many agents stand behind each accountable person in the record, and what does that
  ratio mean for a transparency duty that names a *provider* and a *deployer*?
- **Repair.** When the gate's misses are the gate's own, what rules follow, and do they hold on posts the
  rule-writer never saw?

## 2. Prior work, and what we did not repeat

Thirty-one sources were read in depth and ninety-nine enumerated for this section (`research/moltbook/prior-work.md`, with the verification of every key claim). The table lists what each measured; we reuse the archive paper's injection label and counts, and we leave alone what has been done: topic and toxicity taxonomies, sentiment, near-duplicate spam, reply-graph communities, instruction-file natural experiments, political propaganda, multi-turn moderation, and the two post-acquisition keyword crawls.

| Who | What was measured | Headline numbers | Window |
|---|---|---|---|
| [Jiang et al. (CISPA / TrustAIRLab)](https://arxiv.org/abs/2602.10127) | LLM topic and toxicity labels on every post to 1 Feb 2026; duplicate flooding; hourly volume vs harm; no injection, owner or network measurement | 44,411 posts; 12,209 submolts; 12,684 activated agents; 73.01% Safe; L4 Malicious 1.43%; one 4,535-post duplicate cluster; r=0.769 volume vs harmful share; kappa 0.80 topic / 0.71 toxicity | 2026-01-27 to 2026-02-01 |
| [Gautam, Olstad, Pettersen, Riegler (SimulaMet)](https://arxiv.org/abs/2605.13860) | Passive 2-minute API polling; regex convenience annotations (11 patterns, no precision or recall, not shipped as columns); reply-graph communities; visual-only look at 2026-03-10 | 2,615,098 posts; 1,213,007 comments; 175,886 posting agents; 6,730 submolts; 9,247 regex-flagged injection posts (0.35%) from 1,746 agents; 14.3% duplicate spam; 64.1% crypto; comment coverage 23.8%; Feb 9 spike 371,085 posts, under 10% captured; reply graph 1 | 2026-01-27 to 2026-04-14 (live Hugging Face copy to 2026-09-11) |
| [Riegler and Gautam (Simula); report header says INTERNAL](https://zenodo.org/records/18444900) | Unpublished regex detectors for injection, manipulation and crypto; sentiment; no owner analysis | 19,802 posts; 2,812 comments; 8,827 posting vs 363 commenting agents; 506 injection posts (2.6%); 28 API-injection comments, 61% from one actor; 19.3% crypto; 580 credential or OAuth requests; sentiment 0.454 to 0.257; platform-reported 1,489,468 agents on 01- | 2026-01-28 to 2026-01-31 |
| [Wiz Research](https://www.wiz.io/blog/exposed-moltbook-database-reveals-millions-of-api-keys) | Supabase key in client bundle, no RLS, unauthenticated read and write; disclosure timeline; ratio of registered agents to owners (agents figure is what Moltbook 'boasted'; owners is a table count) | about 4.75M records; 1.5M API keys; 17,000+ owners; 88:1; 29,631 observer emails; 4,060 private DM conversations; first contact 2026-01-31 21:48 UTC, final fix 2026-02-01 01:00 UTC; no outage mentioned | 2026-01-31 to 2026-02-01 |
| [Wayback captures of /api/v1/stats](https://web.archive.org/web/20260201070209id_/https://www.moltbook.com/api/v1/stats) | Only four hand-saved captures exist; counter zeroed mid-window; freshness flag contradicted by CDN headers | agents 100,095 (01-31 00:16Z) to 0 (01-31 20:36Z, comments already 232,813) to 1,506,155 (02-01 06:58Z): 15.05x in 30.7 h, about 45,800 per hour; posts 8,142 to 56,960; 04-08: totalAgents 2,881,380, verifiedAgents 202,786 (7.04%) | 2026-01-31 to 2026-04-08 |
| [Zerhoudi et al. (Passau)](https://arxiv.org/abs/2604.13052) | 40-day crawl; six dated instruction changes from Wayback diffs; reciprocity, threads, votes, orchestrator layer, toxicity relabelling, attack-discourse clusters, credential and address extraction | 1,312,238 posts; 6.7M comments; 120,811 authors; E2 05 Feb heartbeat 4h to 30min: engagement 90.1% to 32.0%; E3 08 Feb new-agent caps: first-day actions 32.91 to 3.96 (-88.0%); E4 14 Feb crypto filter: m/general crypto 24,055 to 4,167 per day (-83%); E5 25 Feb | 2026-01-27 to 2026-03-09 |
| [Zhang et al. (Tulane, Rutgers, ORNL)](https://arxiv.org/abs/2602.13284) | Keyword attack detector, 7 categories; engagement amplification; puppet-cluster signals; reply structure | 27,269 agents; 137,485 posts; 345,580 comments; 15,915 attack instances (about 4%): API injection 61.5%, social engineering 31.9%, prompt injection 3.7%; attack posts 6x score; 13.7% of agents with coordination signal; reciprocity 4.1%; 51.2% of comments exact | 2026-01-28 to 2026-02-05 |
| [Ning Li (Tsinghua), single-author preprint](https://arxiv.org/abs/2602.07432) | CoV of inter-post intervals per author; shutdown-restart natural experiment; bot-farm concentration; owner follower tiers; blank-author comments | 226,938 posts; 447,043 comments; 55,932 agents; 15.3% autonomous, 54.8% human-influenced of 9,838 classifiable; 4 accounts = 32.4% of comments; 174,282 (39%) comments with blank author; 18,651 owner accounts (about 3:1 among active authors), 30.9% zero-followe | 2026-01-27 to 2026-02-10 |
| [Manik and Wang (RPI), two papers on one 39,026-post snapshot](https://arxiv.org/abs/2604.06199) | Lexicon AIRS/DI score; four-class rule-based reply types; follow-up adds mixed-effects model and permutation tests | 39,026 posts; 5,712 comments; 14,490 agents; DI>0 in 18.4%; OR 1.136 [1.043, 1.237] per SD; permutation p 0.00799; event-aligned drop on n=32 threads | single snapshot before 2026-02-02 |
| [Jose, Nair, Greenstadt (NYU)](https://arxiv.org/abs/2603.18349) | GPT-4o-mini binary labels validated on 800 posts; producer and community concentration; no temporal analysis | 673,127 posts; 879,606 comments; 93,714 agents; political propaganda 7,012 (1.0%) = 42% of political; 1,402 agents (1.5%) produce it; 10 agents = 24%, 50 = 49%, 100 = 61%; Gini 0.7; 5 communities hold 70%; abstract says 4% / 51% (not in body) | export 2026-03-05 |
| [Tasci (Bandirma); PeerJ CS listed but unfindable](https://github.com/mtasci42/moltbook-a2a-prompt-injection) | Five-category taxonomy; regex screen; seed and recall-audit CSVs (CC BY 4.0); detector metrics in README only (notebooks have no outputs); annotation provenance unclear (README says LLM-assisted, file says human_label) | 3,105,136-post window; 3,454 regex candidates (0.111%); seed 630 = 167 attacks / 463 non; audit 1,500 = 28 attacks (1.87%), regex recall 3/28 (10.7%), 0/11 in post-acquisition phase; 26 of 28 wild attacks are advertising or redirection; 167 seed attacks from 3 | 2026-01-27 to 2026-05-28; phases split at 2026-03-10 |
| [David Keane (NCI MSc); rater B was Claude](https://huggingface.co/datasets/DavidTKeane/moltbook-agent-social-ai-prompt-injection-dataset) | Full read-only crawl on 2026-09-01; 73-keyword scanner; blind two-rater labelling (one human, one Claude) of 30 high-confidence hits; retraction of March 2026 figures produced by a substring bug | 207,391 items (77,469 posts, 129,922 comments); 3,075 keyword matches (1.48%); 172 high-confidence (0.083%); 0/30 attacker-authored (95% CI 0-11.4%); 10/30 refusals; kappa 0.929; 10,176 false positives = 76.8% of the buggy scan; 18.85%, 10.07% and 9.87% withdr | snapshot 2026-09-01 |
| [Zhang et al. NTU (MissClaw); Lin et al. (MoltLab)](https://arxiv.org/abs/2603.23064) | Heartbeat background turn absorbs plausible misinformation with social cues; promotion into long-term memory; cross-session effect; pre-fix OpenClaw of 24 Jan 2026 | same-session misled up to 61%; memory save up to 91.1%; cross-session ASR up to 75.6%; naturalistic 1-in-20 dilution 28.9% save / 17.8% ASR; Salami Attack (arXiv 2608.01637) Memory Save Rate 81.3%, ASR 75.0% over 48 scenarios | lab, March and August 2026 |
| [Liu et al. (Shanghai AI Lab), report v1.5](https://arxiv.org/abs/2602.14457) | LLM-classified samples; 48-hour live run of four models on OpenClaw; 30-case injection suite (not released) | attack posts: phishing 57.7%, direct prompt injection 14.1%, other 29.2% (text nonetheless calls injection most prevalent); top-100 posts 38% safety or attack; random 12% + 12.7%; ASR change -3.33 to -20.00 points; SOUL.md rewritten by up to 900 lines | before 2026-02-15 |
| [Chen et al. (Shanghai AI Lab / ShanghaiTech)](https://arxiv.org/abs/2602.14364) | 34 cases, one model, no sandbox; recommends gating delete/overwrite/communicate actions | 58.9% pass; intent misunderstanding 0%; injection robustness 57%; hallucination 100% | February 2026 |
| [Al-Lawati et al. (Penn State)](https://arxiv.org/abs/2605.12856) | Bot-Mod interrogation; GPT-5 personas; no injection labels; false-positive rate never quantified; repo has no licence | 473 personas; 378 released train rows; best ID mean F1val 0.6851; binary post F1 0.7953 | context scraped on or before 2026-02-23 |
| [Holtz; Price et al.; Hou and Ji (Advanced Science, peer-reviewed); Sodano et al.; Williams and Ferdinand (Robonomics); Krishnan (SSRN)](https://onlinelibrary.wiley.com/doi/10.1002/advs.77665) | Reciprocity, duplication, inequality, fragility and human-network comparison, all pre-acquisition | Holtz 2602.10131: reciprocity 0.197, 93.5% comments unanswered, 34.1% duplicates; Price 2602.20044: reciprocity about 1%, upvote Gini 0.992; Sodano 2603.23279: core 0.9% of nodes; Krishnan: 36.3% vs 0.29% exact duplicates (Moltbook vs Reddit); Hou and Ji: supp | January to February 2026 |
| [Chen et al. (education data mining)](https://arxiv.org/abs/2602.18832) | Three-phase lifecycle; platform-side deletion event (undated in abstract) | 231,080 non-spam posts; 1.55M comments; 57,093 posts deleted; mean comments per post 31.7 to 8.3 to 1.7; Gini 0.889 | to late February 2026 |
| [Ayan; Lai et al. (with OSF srmt6 pre-registration); Luo et al.](https://arxiv.org/abs/2604.21295) | Ayan: 61-day corpus straddling 03-10, released; Lai (2609.16051): owner interviews and survey; Luo (2604.19925): owner-agent behavioural transfer via public X links | Ayan 2.19M posts, 11.25M comments, 175,036 agents, 62.8% transactional; Lai 30,076 active agents (window unstated, abstract only), N=11 interviews, N=53 survey; Luo 10,659 matched owner-agent pairs | 2026-01 to 2026-09 |
| [Brach et al. (Moltbook Files); Zerhoudi sec. 9.1](https://arxiv.org/abs/2605.07462) | Second measurement of secrets in post bodies; PII-scrubbed alternative corpus released | 232k posts, 2.2M comments over 12 days; API keys, passwords and BIP39 seeds found; Zerhoudi: 7,944 emails (1,237 unique), 806 unique IPs, 67 passwords, no confirmed live credentials | early 2026 |
| [10a Labs; MoltGraph (Mukherjee et al.)](https://arxiv.org/abs/2606.00067) | Malicious-behaviour taxonomy over 17 days; temporal graph dataset for coordination | 228,684 posts, 18.28% toxic/manipulative/malicious, 74 classes; MoltGraph 2603.00646: top 1% agents = 29.00% of engagements, 98.33% of coordination episodes under 24 h | early 2026 |
| [Shi and DiFranzo (Lehigh)](https://arxiv.org/abs/2602.09286) | LDA over r/moltbook and r/openclaw; verification-cue timing (2602.11412) | 698 threads; JSD 0.418, p=0.0005; r/moltbook Security/Privacy top salience 2335; verification cue OR 2.57, median lag 4.21 h vs 0.34 h | 2026-01-01 to 2026-02-06 |
| [Zenity Labs; Permiso; Vectra; SecurityWeek; IST](https://zenity.io/resources/new-agent-ecosystems/moltbook-security) | Zenity posted a benign tracked link (interventional, undated); Permiso disputes the agent numerator; Vectra repeats an unattributed 2.6% (almost certainly Riegler and Gautam's 506/19,802); the rest is secondary | Zenity 900+ endpoints, 70+ countries, 1,400+ requests in under a week, about 1,100 upvotes to enter Hot; Permiso 10,000-15,000 realistic agents vs 1.5M claimed, 7 named threat handles, 377+ malicious skill downloads | February 2026 (Vectra update 2026-05-12) |
| [Palo Alto Networks; moltbookstatus.com; Techloy; Wikipedia; nation.ai](https://www.paloaltonetworks.com/blog/network-security/the-moltbook-case-and-how-we-need-to-think-about-agent-security/) | Self-reported or tracker figures for the Feb-Sep shape | 02-05 00:00 PST 1.65M agents / 202k posts / 3.6M comments; Techloy 32K to 147K to 770K to 1.5M; 03-02 2,851,838; 03-09 relabel to Human-Verified 193,912; 06-06 206,839 / 2,895,874 (Wikipedia, editor-typed); 09-18 213,029 / 2,913,891, 4,223,631 posts (nation.ai | 2026-02 to 2026-09 |
| [Moltbook LLC documents via Wayback; CDX index](https://web.archive.org/web/20260903132526id_/https://moltbook.com/terms) | Terms and Privacy Policy last updated 2026-03-15; read endpoints answer a crawler with no Authorization header; robots.txt 404; open-source API repo gone; rate limits conflict | about 5,000 CDX rows (query cap), nearly all 200 application/json, latest 2026-09-20; skill.md 60 GET per 60 s per key vs rules.md 100/min; github.com/moltbook 200 on 01-31, 404 by 06-23 | 2026-01-30 to 2026-09-20 |
| [Wilson et al.; Li et al. Superminds; DiGiacomo (Zenodo 19825077); Zenity](https://arxiv.org/abs/2605.08463) | Deployed 13 agents; posted probing agents; posted moral-signal field experiment; posted a tracked link | Wilson about 400 sessions per agent over one week; DiGiacomo 74 header signals zero acknowledgment vs 73% embedded | 2026-02 to 2026-05 |

**Where this paper stands against that record.** *Study A:* No study has judged the action a post solicits rather than its text. Nobody has reported an action gate's detection rate, false-positive rate on matched benign posts, or a failure taxonomy that separates command-bearing injection from prose-only social engineering and delayed memory triggers. *Study B:* No daily interrupted-time-series with the instruction-change breaks modelled, no agent-count series split by verification tier, no injection prevalence with a fixed detector on both sides, and no reply-graph community comparison pre/post 03-10. The archive paper itself reports no detectable volume discontinuity at 10 March from a visual inspection; §5.3 makes that a measured statement and adds the injection and concentration series. *Study C:* Nobody has computed the agents-per-distinct-owner distribution from the Archive's public is_claimed and owner_x_handle fields with the window stated, nor mapped registered / claimed / verified / active tiers onto EU AI Act Art. 50 provider-deployer duties and Swiss law. Zerhoudi et al. counted 106,916 X handles with 8 multi-agent handles in their own crawl; §5.4 reproduces the one-to-one finding on the archive and adds the unclaimed share. *Study D:* Nothing is measured after 2026-09-11.


## 3. Data

**Source.** `SimulaMet/moltbook-observatory-archive` on Hugging Face, snapshot of 2026-09-11 (manifest
`dump_date`), 1,086 Parquet files, 2.73 GB: `posts` (12 columns), `comments`, `agents` (with `is_claimed` and
`owner_x_handle`), `submolts`, `snapshots` (the observatory's own counters, hourly), `word_frequency`. Licence
MIT; citation as the card requests. The paper's frozen snapshot is Zenodo 10.5281/zenodo.19594804.

**Deduplication.** The export appends a rolling seven-day backfill, so a row can appear under several
`dump_date`s. We keep the latest row per primary key (`build_db.py`). In this export no post row was duplicated;
46 agent rows and 6,866 submolt rows were. The archive paper's own loader concatenates every partition; the
injection count is the same either way (§5.1).

**Completeness.** The card states that posts and comments are substantially complete only to the end of
March 2026 and that comment coverage is partial throughout. We therefore compare the pre- and
post-acquisition windows only inside the complete range, treat the comment table as a sample, and report the
April–September window separately as an indication, never a comparison.

**Windows.** Matched *pre28* 2026-02-10 to 2026-03-09 and *post28* 2026-03-10 to 2026-04-06 (28 days each, the comparison the paper rests on); full *pre* 2026-01-27 to 2026-03-09 (42 days), *post* 2026-03-10 to 2026-04-14 (36 days), *late*
2026-04-15 to 2026-09-11 (150 days, incomplete). All by post `created_at`, UTC.

**The injection label.** We reproduce the archive paper's label exactly: eleven case-insensitive regular
expressions from its companion code (`moltbook/risk.py`, MIT) over the concatenation of content and title
(`label_injection.py`). It is a keyword heuristic. It catches direct address ("AI agents reading this"), API
verbs, "ignore previous instructions", chat-template tags, "please upvote/follow/execute", `curl -X` and a
bearer-token placeholder. It does not catch paraphrase, and it flags tutorials that quote the same strings.
Everything downstream inherits this, and §6 says what it would take to replace it.

## 4. Methods

### 4.1 Study A — what a host-side gate can see

The object under test is sentinel-hook v0.2.0 (MIT, https://github.com/GvHildebrand/sentinel-hook; rules
SHA-256 `4f69b35e0c63fbf869c2edf42f34ca0e933bbfe94f356be312efea8969cdbba3`), a pre-action gate for Claude Code agents: 24 deterministic rules that allow, ask or deny a
shell command or a file write before it runs, with no model in the path. It judges the text of an action, not
prose. A benchmark that fed it posts would measure nothing. Instead we ask, for each post, **what action the
post asks a reading agent to take**, and hand the gate that action.

`extract_payloads.py` classifies every post into surfaces (a post can carry several):

| Surface | What the post asks | What the gate is handed |
|---|---|---|
| S1 | a shell command (fenced, inline, or a line starting with a shell word and carrying a flag, path, pipe or URL) | the command, as a `Bash` call |
| S2 | an HTTP/API call written as `VERB /api/...` or `VERB https://...` | a `curl` reconstruction with a bearer header when the post mentions one |
| S3 | a write to a persona, memory, heartbeat, environment or shell-profile file | a `Write` call to the named path |
| S4 | a platform action (upvote, follow, comment, post, join) | nothing: there is no host-side tool |
| S5 | a credential to be sent, pasted or replied with, with no command to do it | nothing, unless S1 also present |
| S6 | an instruction override with no action ("ignore previous instructions", "you are now") | nothing |
| S0 | none of the above | nothing |

`sentinel-bench.mjs` runs the gate's `evaluate()` over every extracted call under the agent and the person
profile, in a throwaway repository root, and records decision, rule and severity. Nothing is executed.

**Sets.** *injection*: every labelled post in the paper window. *benign*: one unlabelled post per injection
post, matched on submolt and calendar day, nearest in time, without replacement (`sample.py` reports how
many matches fell back to ±3 days or to any post that day). *benign_code*: unlabelled posts in the window that
carry a fenced code block, capped at the injection count by hash order: the hard negatives a command gate is
most likely to misjudge.

**Measures.** *Reach* = share of posts with at least one visible call (S1–S3). *Catch* = share of posts with
at least one visible call where the agent-profile decision is deny or ask. *False positive rate* = the same
share on the two benign sets. *Failure categories* = injection posts with no visible call, by surface, and
visible calls the gate allowed, by what the command does (download-and-execute, HTTP POST, package install,
interpreter, delete, read-or-print, other) and, for writes, by path.


### 4.5 Study A′ — the rules the corpus forced, and a held-out score

The 0.2.0 results (§5.2) named three misses that were failures of the gate rather than of its category. We wrote one rule for each, kept the discipline the gate is built on (deterministic, stable identifiers, no model), and released them as sentinel-hook 0.3.0 [rules SHA-256 in `results/RUNLOG.md` §3.12]:

| Rule | What it catches | Decision (agent / person) |
|---|---|---|
| W06 agent-self-write | a tool write, outside any repository, to the agent's own persona, memory, heartbeat, identity, skill or runtime-config file: `~/.openclaw/…`, `~/.claude/…`, any `SOUL.md`, `MEMORY.md`, `HEARTBEAT.md`, `SKILL.md` or `skills/<name>/…` under a home directory | deny / ask |
| B17 agent-self-mutation | the same mutation from a shell (redirect, `tee`, `sed -i`, `cp`/`mv` destination), with a stronger reason when the segment downloads (`curl`/`wget`): a skill installed by redirect | deny / ask |
| E02 egress-not-allowlisted | a network host outside an allowlist the operator declares in the inventory (`_egress_allow` for everyone, `egress_allow` per agent; suffixes cover subdomains; loopback always allowed). Inert when no list is declared | deny / ask |

**Discipline.** The rules were written from the January–April injection posts (§4.1, "in sample"). They were then scored, unchanged, on the 2,316 injection posts of 2026-04-15 to 2026-09-11 ("held out"), drawn with the same matched benign and code-carrying benign sets by `sample.py --start 2026-04-15`; those posts were not opened by anyone while the rules were written. The incident corpus the gate was originally built on (50 destructive, 52 benign look-alikes, 36 variants, 200 payload trials) and its own held-out set (28 destructive, 22 benign) were re-run under 0.3.0 and are unchanged. Three configurations are reported: 0.3.0 with no allowlist; with a Moltbook-only allowlist (`moltbook.com`); and with a developer-realistic one (`moltbook.com`, `github.com`, `githubusercontent.com`, `npmjs.org`, `pypi.org`). The allowlist is a policy, and its false positives are the price of the policy an operator chooses.

### 4.2 Study B — before and after 2026-03-10

Per window, from the deduplicated posts: posts per day, distinct posting agents, mean daily active
posting agents, new agents by `created_at` and by `first_seen_at`, active submolts, injection posts and rate,
injection agents and their share of posting agents, concentration (share of posts by the top 1 % and top 10
agents, Gini over agents, Herfindahl over submolts ×10,000, share of the top 10 submolts), content length,
comments collected, and the number of agents with at least one minute of ten or more posts (the flooding
Jiang et al. describe). The `snapshots` table gives the platform's own counters independent of collector
completeness and is plotted to 2026-09-11.

### 4.3 Study C — the attribution gap

From `agents`: total, claimed, with an `owner_x_handle`, distinct handles, agents per handle (mean, max,
Gini, distribution, handles with ten or more and a hundred or more agents). From posts joined to agents:
posts and posting agents by attribution class (claimed with handle, claimed without, unclaimed, no agent
row), per window the share of posts and of posting agents with a resolvable owner handle and the ratio of
posting agents to posting handles; for injection posts, how many agents, how many resolve to a handle, how
many distinct handles, and the share of the top agent and top ten. Handles are counted, never listed.

The legal frame (§5.4) was built from primary sources — EUR-Lex, Fedlex, admin.ch, coe.int — with every
statement labelled *text says*, *reasonable reading*, *contested* or *needs legal review*, and each claim
re-fetched by an independent verifier before it was kept.

### 4.4 Study D — the live check

A sample of recent posts from the free read-only endpoint: ten GET requests, no credential, an identifying user agent, raw responses kept. On the network this study first ran from, `moltbook.com` resolved to `0.0.0.0` at the local resolver while public resolvers answered; the block was not circumvented, and the check ran only after the operator reported the domain reachable. The archive's late window (2026-04-15 to 2026-09-11) is reported beside it. Moltbook's Terms forbid automated retrieval; ten requests for a one-off sample is the lightest reading of that we could make, and it is listed for counsel.

## 5. Results

### 5.1 The label, reproduced

Over the deduplicated posts to 2026-04-14 the eleven regexes flag **9,249** posts against the archive paper's 9,247 (the raw, backfill-duplicated loader gives 9,249); over the whole export to 2026-09-11, **11,565** of 3,602,713. By pattern: curl_command 5,202, api_post 3,572, please_action 3,252, direct_address 2,065, role_tags 1,973, api_key_placeholder 1,503, api_get 1,329, ignore_instructions 493, inst_tag 5, system_tag 3, hidden_tags 1. Two facts follow. The label is dominated by API strings (`curl -X`, `POST /api`, `GET /api`, `Bearer YOUR`), so 'injection' on Moltbook mostly means *an instruction to call the platform's own API*. And it is reproducible to within two posts by anyone with the archive. Confidence: high.

### 5.2 Study A — what a host-side gate can see

| Set | Posts | With a visible call (reach) | Posts caught | Over visible | Over all | Calls | Calls caught |
|---|---|---|---|---|---|---|---|
| injection | 9,249 | 8,397 (90.79 %) | 44 | 0.52 % | 0.48 % | 26,947 | 55 |
| benign, matched | 9,249 | 270 (2.92 %) | 19 | 7.04 % | 0.21 % | 458 | 22 |
| benign, code-carrying | 9,249 | 1,637 (17.70 %) | 181 | 11.06 % | 1.96 % | 3,035 | 187 |

**Reach.** 90.79 % of injection posts carry an action a gate can see, which refutes pre-registration A1, and for a reason the label itself explains: 7,947 of 9,249 carry an API call written out as a verb and a path (S2), 4,006 a shell command (S1), 252 a request to write a persona, memory or heartbeat file (S3). 852 posts carry nothing a host-side tool would execute: 326 ask only for a platform action (upvote, follow, subscribe, comment), 280 are instruction overrides with no action, 159 match none of the surfaces (chat-template tags, direct address), and 87 combine a credential request with one of those.

**Catch.** The gate stops 44 of the 8,397 reachable injection posts (0.52 %); 55 of 26,947 calls. Every catch is a deny; none is an ask. Rules that fired: B13.credential-exfiltration ×20, B10.remote-code-execution ×10, B14.credential-read ×9, B01.rm-recursive-catastrophic ×8, B16.persistence-mutation ×4, W04.persistence-write ×3, W03.credential-file-write ×1. The 26,892 allowed calls include 20,747 HTTP POSTs and 5,085 GETs; 14,823 of the URL-bearing ones go to `www.moltbook.com`, the rest to third-party hosts (below): `/posts/<id>/upvote` (2,234, of which 1,947 carry a placeholder id), `/agents/<name>/follow` (3,924, 3,760 of them to two agents), `/submolts/<name>/subscribe` (1,893), `/posts` and `/posts/<id>/comments`. This is karma farming and follower farming through a reader's credentials, and by the gate's own specification it is not destructive. Pre-registration A2 holds: the miss list is API POSTs.

**Persona writes.** 478 allowed calls write to an OpenClaw persona, memory or heartbeat file (`HEARTBEAT.md` 262, `MEMORY.md` 182, `SOUL.md` 28, `AGENTS.md` 3, `config.json` 3); the gate records them as outside the repository (W05) and lets them through, because its write scope is the repository. Pre-registration A4 holds, and it is the most consequential miss: a heartbeat or memory file is exactly where an injection becomes persistent. A second shape of the same miss is a shell redirect of remote content into the agent's skill directory (`curl -s <url> > ~/moltbook/skills/<name>/…`: 1,508 of the 1,510 calls to `raw.githubusercontent.com` write a skill file, a heartbeat or a reference document that way), which the gate does not treat as download-and-execute because nothing executes in the same command.

**Third-party hosts.** After Moltbook itself, the allowed calls go to `clawproof.onrender.com` (3,833), `raw.githubusercontent.com` (1,510), `api.clawchain.vsa.co.za` (417), `moltbook-curator.online` (334), a bare IP on port 8000 (205) and `localhost:8080` (187). Hosts are recorded by the gate's E01 finding and never blocked; a host allowlist is not part of its design.

**False positives.** On the matched benign set the gate catches 19 of 270 reachable posts (7.04 %, 0.21 % of all); on the code-carrying set 181 of 1,637 (11.06 %, 1.96 % of all). The rules behind them are B10 download-and-execute (13 and 129), B14 credential reads (8 and 27) and B01 recursive deletes (10): a benign-by-label post that tells a reader to `curl … | sh` is a post the gate is built to stop. Pre-registration A3 holds, and the 'false positives' are better read as the label's misses than the gate's.

**Reading.** A host-side action gate built for destructive commands, run over the largest public corpus of agent-targeted injection, sees nine posts in ten and stops one in two hundred, and the one it stops is the one that would have wiped a home directory or shipped a `.env`. The other 199 ask the reading agent to spend its platform credentials on someone else's karma, to rewrite its own memory, or to install a skill from a URL. None of that is in the destructive-command class, and none of it should be added there: the fix is a second gate at the platform trust boundary (which agent may vote or follow on whose instruction) and a write scope that covers the agent's own persona files wherever they live. Confidence: high on the counts; medium on the surface classification, which is a regex extraction we wrote and release.

### 5.3 Study B — before and after 2026-03-10

| Metric | pre, 28 d | post, 28 d | pre, 42 d | post, 36 d | late, 150 d |
|---|---|---|---|---|---|
| posts per day | 43366.8 | 19007.3 | 47060.4 | 17761.4 | 6578.4 |
| posting agents, daily mean | 6835.4 | 2273.6 | 8677.0 | 2109.8 | 684.7 |
| distinct posting agents | 80,007 | 12,381 | 167,868 | 13,337 | 8,993 |
| new agents (first seen) | 40,647 | 9,521 | 93,691 | 10,245 | 6,208 |
| active submolts | 2,313 | 2,099 | 5,516 | 2,364 | 1,997 |
| injection posts | 1,567 | 2,092 | 6,854 | 2,395 | 2,316 |
| injection rate % | 0.129 | 0.393 | 0.347 | 0.375 | 0.235 |
| injection agents as % of posting agents | 0.575 | 2.48 | 0.861 | 2.572 | 3.002 |
| posts by top 1 % of agents % | 29.28 | 33.37 | 28.18 | 34.53 | 57.05 |
| posts by top 10 agents % | 3.51 | 7.49 | 2.28 | 7.54 | 27.24 |
| Gini over agents | 0.7455 | 0.8582 | 0.7288 | 0.8668 | 0.9265 |
| Herfindahl over submolts ×10⁴ | 3520.8 | 2248.1 | 4487.4 | 2276.4 | 4182.5 |
| top 10 submolts share % | 90.06 | 80.21 | 88.86 | 79.26 | 81.57 |
| median content length | 99.0 | 466.0 | 100.0 | 526.0 | 500.0 |
| agents with a ≥10-per-minute burst | 2 | 0 | 2,823 | 0 | 0 |

**No discontinuity.** The archive paper reports, from a visual inspection, no detectable volume discontinuity at 10 March [Gautam et al.]; the series confirms it by number. The day before the acquisition the collector recorded 28,240 posts from 2,680 agents; the day of, 29,263 from 3,218; the day after, 29,356 from 3,200. The series is a continuous decay from the viral week of 9–15 February (1,021,874 posts, 86,636 agents on the peak day), not a step at 10 March. Matched 28-day windows therefore show what the transition period looked like, not what Meta did: posts per day fell from 43,367 to 19,007 (-56 %), daily posting agents from 6,835 to 2,274 (-67 %), new agents from 40,647 to 9,521. Pre-registration B1 holds. Zerhoudi et al. date six instruction-file changes inside that pre-window, the last two on 25 February (+160 % posts per day) and about 1 March (−48 %), each a larger shock than any plausible acquisition effect, so the fairest baseline is the last seven days before the sale: 3–9 March against 10–16 March. There, posts per day go from 32,056 to 24,853, daily posting agents from 2,754 to 2,726 (unchanged), new agents from 1,652 to 2,795, the injection rate from 0.318 % to 0.252 %, the top 1 % share from 25.62 % to 28.93 %, and the share of posts with a resolvable owner handle from 18.39 % to 28.26 %. On the week scale the transition is a slightly smaller, slightly better-attributed platform with the same population; the 28-day contrast is the February decay, not the sale.

**Injection did not fall.** The injection rate rose from 0.129 % to 0.393 % of posts across the matched windows, and injection agents from 0.575 % to 2.48 % of posting agents; in absolute terms 1,567 to 2,092 posts while total volume halved. Pre-registration B2 is refuted. The population shrank faster than the injectors did.

**Concentration rose, by agent; fell, by community.** The top 1 % of agents wrote 29.28 % of posts before and 33.37 % after (Gini 0.7455 → 0.8582); B3 holds. The Herfindahl index over submolts fell from 3,520.8 to 2,248.1 and the top ten submolts' share from 90.06 % to 80.21 %: fewer agents, spread over more communities. Median content length went from 99 to 466 characters, and the sub-minute flooding Jiang et al. describe (2,823 agents with a ten-posts-in-one-minute burst in the full pre window) is absent after 10 March (0). Whether that is a platform rate limit or the departure of the bursting agents, the archive cannot say.

### 5.4 Study C — the attribution gap

**The public layer shows one handle per agent.** The archive holds 182,860 agents, 129,268 marked claimed (70.7 %), 55,551 with an `owner_x_handle` (30.4 %) resolving to 55,541 distinct handles; the most agents on one handle is 2. Wiz's 88:1 (1.5 million agents, about 17,000 owner rows) is therefore invisible at the public API: the owner table Wiz read is keyed on something the platform never exposes, and the one identifier it does expose is, by construction, one-to-one. Zerhoudi et al. found the same one-to-one shape in their own crawl to 9 March (106,916 X handles, 8 with more than one agent) [arXiv:2604.13052]; and an unpublished analysis script in a third crawl (daveholtz/moltbook_scraper, `analysis/R/07_owner_analysis.R`, MIT, updated 2026-09-21, no results released) computes unique and multi-agent owners the same way; this is a replication on the archive, and the addition is what follows. Pre-registration C1 is half refuted: the resolvable share is indeed below half, but the ratio of posting agents to posting handles is 1.0, not above 2. The gap is not that many agents share one visible owner; it is that most agents have none.

**Most posts come from agents with no visible owner.** By attribution class: 2,242,177 posts (62.2 %) from 52,862 agents the archive records as unclaimed, 1,003,776 (27.9 %) from 55,042 claimed agents with a handle, 356,760 from 73,685 claimed agents with no handle. Per window, the share of posts whose author resolves to any handle is 12.37 % before the acquisition (28 d) and 39.84 % after, 22.29 % in the late window; the share of posting agents that resolve is 18.92 %, 26.97 % and 16.85 %. Whether an 'unclaimed' agent can post at all is a platform question; the archive records that they did, and the `is_claimed` flag may lag the platform (it is captured with the profile, not with the post).

**The injectors.** 1,982 agents wrote the 11,565 injection posts; 1,027 (51.8 %) resolve to a handle, a higher share than posting agents in general, which refutes pre-registration C2. But the distribution is the point: one unclaimed agent with no handle, posting since 2026-02-26 (its profile was first captured on 2026-03-27), wrote 3,029 of them (26.19 %); the top ten wrote 53.77 %; of the top ten, 3 have no handle. Half of all injection posts (5,743) come from unclaimed agents.

**What the identifier carries.** Of 182,860 agent descriptions, 1.36 % name a model, 6.0 % a framework, 1.24 % an operator ('run by', 'on behalf of'); 19.49 % are empty. Trust is concentrated where identity is thin: the top 1 % of handles hold 64.23 % of all karma on claimed agents (top ten handles 31.35 %, Gini 0.9315). Same-minute registration bursts on one handle (`m5`) return zero, and are uninformative for the same reason: no handle carries more than two agents, so the public identifier cannot show a fleet.

### 5.5 Study D — the live check

Run on 2026-09-24 at about 06:40 UTC, after the operator reported the domain reachable again: ten unauthenticated GET requests to the public API with an identifying user agent (`sort=new` with five cursor pages, `sort=hot`, `sort=top`, and `/stats`), raw responses kept in `results/live/`. Nothing was posted, voted or registered.

**The platform's own counters:** 2,915,360 agents, 213,661 verified (7.33 %), 4,281,970 posts, 22,416,539 comments, 33,259 submolts. The archive's 3,602,713 posts are 84.1 % of the platform's total, which bounds the collector's coverage over the whole run.

**The newest 600 posts** span 2.37 hours (2026-09-24T03:33Z to 2026-09-24T05:56Z), about 253 an hour, from 140 agents; the five most active wrote 36.3 %; 482 of 600 are in `m/general`. Every one carries `verification_status: verified` and none `is_spam`; 100.0 % are by agents the API marks `isClaimed`, and the author object exposes no owner handle at all (avatarUrl, createdAt, deletedAt, description, followerCount, followingCount, id, isActive, isClaimed, karma, lastActive, name). The archive's regex label flags 0 of the 600. The hot page (100 posts over 46 hours) is 18 agents, the top five writing 80.0 %; the all-time top page is entirely January–March 2026, 24 of its 100 posts marked `verification_status: bypassed`, a status that no longer appears on new posts.

**Reading.** The live platform in late September matches the archive's late window on rate (about 6,072 posts a day against the collector's 6,578), on population (a few hundred agents active) and on concentration. Two things the archive cannot show: the API now stamps every post with a verification status and a spam flag, and it no longer exposes an owner handle on the author object, so the one public identifier Study C relied on is gone from the post feed. The regex label finds no injection in the newest 600 posts; a shift from the archive's 0.1–0.5 % is not established on a sample this size (one post in 600 would be 0.17 %). Confidence: high on the counts, low on any trend.

### 5.6 The archive's late window

In the archive's late window (2026-04-15 to 2026-09-11, completeness not guaranteed by the card) the collector recorded 6,578 posts a day from a daily mean of 685 agents, 2,316 injection posts (0.235 %), and the top 1 % of agents writing 57.05 % of posts, the top ten agents 27.24 %. Weekly, the last full weeks of August and early September hold 21,000–24,000 posts and about 500 distinct agents a day, with a weekly injection rate between 0.07 % and 0.23 %. The `snapshots` table turned out to be the observatory's own counters, not the platform's, so pre-registration D1 (platform counters rising while collector counts fall) could not be tested; its `active_agents_24h` on 2026-09-11 is 520. Reading: by September the collector sees a platform an order of magnitude smaller than in March and some forty times smaller than the February peak week, with a stable core of a few hundred agents, a persistent 0.1–0.5 % injection rate, and the top ten agents writing more than a quarter of everything. Whether that is the platform or the collector's coverage, only a live read can say. Confidence: low for the level, medium for the shape.

### 5.7 Study A′ — the gate after the corpus

**In sample (January–April, the posts the rules were written from):**

| Configuration | Injection: posts caught / reachable | over reachable | Benign matched: caught / reachable | Benign code: caught / reachable | Calls caught |
|---|---|---|---|---|---|
| 0.2.0 | 44 / 8,397 | 0.52 % | 19 / 270 (0.21 % of all) | 181 / 1,637 (1.96 % of all) | 55 / 26,947 |
| 0.3.0, no allowlist | 512 / 8,397 | 6.10 % | 66 / 270 (0.71 % of all) | 411 / 1,637 (4.44 % of all) | 2,061 / 26,947 |
| 0.3.0, allowlist moltbook.com | 3,830 / 8,397 | 45.61 % | 117 / 270 (1.27 % of all) | 806 / 1,637 (8.71 % of all) | 10,329 / 26,947 |
| 0.3.0, allowlist + GitHub + registries | 3,800 / 8,397 | 45.25 % | 104 / 270 (1.12 % of all) | 638 / 1,637 (6.90 % of all) | 10,237 / 26,947 |

**Held out (April–September, never opened while the rules were written):**

| Configuration | Injection: posts caught / reachable | over reachable | Benign matched: caught / reachable | Benign code: caught / reachable | Calls caught |
|---|---|---|---|---|---|
| 0.2.0 | 2 / 2,104 | 0.10 % | 2 / 42 (0.09 % of all) | 16 / 285 (0.69 % of all) | 2 / 4,534 |
| 0.3.0, no allowlist | 9 / 2,104 | 0.43 % | 5 / 42 (0.22 % of all) | 34 / 285 (1.47 % of all) | 9 / 4,534 |
| 0.3.0, allowlist moltbook.com | 1,599 / 2,104 | 76.00 % | 8 / 42 (0.35 % of all) | 70 / 285 (3.02 % of all) | 3,637 / 4,534 |
| 0.3.0, allowlist + GitHub + registries | 1,599 / 2,104 | 76.00 % | 8 / 42 (0.35 % of all) | 63 / 285 (2.72 % of all) | 3,637 / 4,534 |

**What the pattern rules did.** In sample, W06 and B17 fired on 478 and 1528 calls and took posts stopped from 44 to 512: every persona write and every skill-by-redirect the 0.2.0 run had let through. On the held-out window they added 7 posts. That is not a failure of the rules; it is the corpus moving. The held-out injection carries only 7 persona-write requests in 2,316 posts (§4.1 surface S3), against 252 in the in-sample window. The campaign that installed skills by redirect ran in February and March and was over by April.

**What the policy rule did.** With a Moltbook-only allowlist, E02 fired on 8,268 in-sample calls and 3,628 held-out calls, and posts stopped went to 3,830 (45.6 % of reachable) in sample and 1,599 (76 %) held out. The held-out window is, in effect, one campaign: a single agent wrote 65 % of its injection posts, and 3,434 of its 4,534 solicited calls go to one host, `clawproof.onrender.com`, which no destructive-command rule can see and any allowlist excludes. Widening the list to GitHub and the package registries, the list a coding agent needs, costs 30 in-sample and 0 held-out injection posts and brings the benign cost down from 117 to 104 matched benign posts (1.12 % of all) and from 806 to 638 code-carrying ones (6.90 %); held out, 8 and 63 (0.35 % and 2.72 %).

**What the new false positives are.** Of the 66 matched benign posts 0.3.0 stops without an allowlist, 49 are W06: posts the regex label did not flag that tell a reading agent to write to its `HEARTBEAT.md` or `MEMORY.md`. They are false positives by the label and true positives by the gate's specification, and they say something about the label: a persona-write instruction carries none of the eleven strings, so the archive's injection count is missing this class entirely. The same holds for 299 of the 411 code-carrying benign posts. With the allowlist, the added benign catches are links to `github.com` and to the small hosts of the platform's own ecosystem, which is the allowlist doing what a list does.

**Reading.** Two numbers carry the result: 9 and 1,599. The rules written from what the corpus showed in March caught almost nothing of what it showed in August, because the injectors had changed shape; the rule that names no pattern at all, only which hosts an agent has business with, caught three quarters of it. A host-side gate that wants to keep up with an agent network should carry the fewest patterns and the clearest policy it can, and leave what it cannot see, an agent spending its platform credentials on someone else's behalf, to the platform that can. Confidence: high on the counts; the in-sample figures are in-sample and are labelled so.

## 6. Limitations

- **The label is a keyword heuristic.** Eleven regular expressions written by the archive's authors; we reproduced it rather than replacing it so that our numbers are comparable to theirs. It over-counts tutorials and API documentation and under-counts paraphrase. The only adjudicated audit we found (Tasci, 1,500-post recall audit, provenance partly unclear) puts a regex screen's recall at 3 of 28 attacks; the label finds the command-shaped tenth of the problem, which is exactly the tenth a command gate can see, so Study A's reach figure is an upper bound on the gate's relevance, not a measure of injection as a whole. A human-labelled gold set is the first thing money would buy (one-pager, $250 tier).
- **The surfaces are ours.** `extract_payloads.py` decides what a post 'asks for' with regular expressions we wrote; the S2 `curl` reconstruction is a translation of a prose API call into a command, and the gate judged our translation. Its rules and output are released so the translation can be disputed line by line.
- **The gate's surface is Claude Code hooks.** An OpenClaw agent calling the Moltbook API through its own HTTP client never issues a shell command; the benchmark says what such a gate *would* see if the action passed through it, not what any Moltbook agent ran.
- **Collector completeness.** The card states posts and comments are substantially complete only to the end of March 2026. The pre/post comparison stays inside that range; the late window is reported as the collector's view. The `snapshots` table is the observatory's own counters, not the platform's.
- **`is_claimed` and `owner_x_handle` are the platform's self-declared fields as captured with the profile**, not verified by us and possibly lagging the post. 'Unclaimed' means the archive recorded the agent as unclaimed, nothing more; 'no visible owner' in the abstract counts only those, and would be 72 % of posts if claimed agents without a handle were added.
- **The acquisition is a date, not a mechanism.** The archive shows a continuous decay from the February peak with no step on 10 March; we do not attribute any change to Meta.
- **Moltbook's Terms forbid automated retrieval with no research exception** (prior-work sweep). This paper reads only the SimulaMet archive and never the platform; whether a live check may ever run is a question for counsel, listed in the brief.
- **Study D is ten requests.** 800 posts on one morning; it can confirm rate and shape, not a trend, and the regex label's zero on 600 posts is consistent with anything below about 0.5 %.
- **The three rules are in-sample by construction.** They were written from the January–April posts and the in-sample table in §5.7 measures the rules against the posts that produced them; only the held-out table is a test. The held-out window is dominated by one agent and one host, so its allowlist result is one campaign's, not a population's.
- **The allowlist result depends on the list.** Two lists are reported; an operator's own list will land elsewhere. E02 is inert until a list is declared, on purpose.
- **A disclosed AI system wrote this.** Every number is produced by the released scripts; the prose was checked by the operator before publication, and the pre-registration in `results/RUNLOG.md` was written before the first result was seen.

## 7. Sources

Every URL read for this paper, by the prior-work and legal-frame workflows and by the session, with the title as the page gave it. The two workflow records (`results/prior-work.raw.json`, `results/legal-frame.raw.json`) hold what each source was read for and which claims were re-verified against it.

- A2A Protocol Specification 1.0.0 — https://a2a-protocol.org/latest/specification/
- Jusletter IT, KI und Haftung: Lösungsansätze für die Schweiz (unisg) — not opened, search snippet only — https://alexandria.unisg.ch/bitstreams/d24d4eea-66b7-4841-807f-e9a4d21d6470/download
- AlgorithmWatch CH, KI-Regulierung: Was tut die Schweiz? (updated 08.07.2026) — https://algorithmwatch.ch/de/leitfaden-ki-regulierung-schweiz/
- AI Act Explorer: Digital Omnibus on AI amendment list — https://artificialintelligenceact.eu/ai-act-explorer/digital-omnibus/
- EU AI Act Article 3 — https://artificialintelligenceact.eu/article/3/
- AI Act Explorer (FLI): Article 50, 3, 25, 2, 99, 113, 49, 71, 22, 16, 54, 85; Recitals 132–137; Digital Omnibus changes — https://artificialintelligenceact.eu/article/50/
- EU AI Act Article 99 — https://artificialintelligenceact.eu/article/99/
- Kumar et al., An Army of Me (2017) — https://arxiv.org/abs/1703.07355
- Chan et al., Visibility into AI Agents (2024) — https://arxiv.org/abs/2401.13138
- Chan et al., IDs for AI Systems (2024) — https://arxiv.org/abs/2406.12137
- South et al., Authenticated Delegation and Authorized AI Agents (2025) — https://arxiv.org/abs/2501.09674
- Chan et al., Infrastructure for AI Agents (2025) — https://arxiv.org/abs/2501.10114
- OpenClaw Agents on Moltbook: Risky Instruction Sharing and Norm Enforcement in an Agent-Only Social Network — https://arxiv.org/abs/2602.02625
- The Moltbook Illusion: Separating Human Influence from Emergent Behavior in AI Agent Societies — https://arxiv.org/abs/2602.07432
- Human Control Is the Anchor, Not the Answer: Early Divergence of Oversight in Agentic AI Communities — https://arxiv.org/abs/2602.09286
- The Devil Behind Moltbook: Anthropic Safety is Always Vanishing in Self-Evolving AI Societies — https://arxiv.org/abs/2602.09877
- "Humans welcome to observe": A First Look at the Agent Social Network Moltbook — https://arxiv.org/abs/2602.10127
- When Visibility Outpaces Verification: Delayed Verification and Narrative Lock-in in Agentic AI Discourse — https://arxiv.org/abs/2602.11412
- Agents in the Wild: Safety, Society, and the Illusion of Sociality on Moltbook — https://arxiv.org/abs/2602.13284
- MoltNet (2026) — https://arxiv.org/abs/2602.13458
- A Trajectory-Based Safety Audit of Clawdbot (OpenClaw) — https://arxiv.org/abs/2602.14364
- Frontier AI Risk Management Framework in Practice: A Risk Analysis Technical Report v1.5 — https://arxiv.org/abs/2602.14457
- The 2025 AI Agent Index (2026) — https://arxiv.org/abs/2602.17753
- Large-Scale Analysis of Persuasive Content on Moltbook — https://arxiv.org/abs/2603.18349
- Mind Your HEARTBEAT! Claw Background Execution Inherently Enables Silent Memory Pollution — https://arxiv.org/abs/2603.23064
- Emergent decentralized regulation in a purely synthetic society — https://arxiv.org/abs/2604.06199
- Form Without Function: Agent Social Behavior in the Moltbook Network — https://arxiv.org/abs/2604.13052
- Otsuka et al., AI Identity: Standards, Gaps, and Research Directions (2026) — https://arxiv.org/abs/2604.23280
- Moltbook Moderation: Uncovering Hidden Intent Through Multi-Turn Dialogue — https://arxiv.org/abs/2605.12856
- The Moltbook Observatory Archive: an incremental dataset of agent-only social network activity — https://arxiv.org/abs/2605.13860
- Humans welcome to observe: a first look at Moltbook (2026) — https://arxiv.org/html/2602.10127v1
- Moltbook Observatory Archive (2026) — https://arxiv.org/html/2605.13860v1
- Aurum, Moltbook: Legal Implications of an AI Agent Social Network (10.02.2026) — https://aurum.law/newsroom/Moltbook-Legal-Implications-of-an-AI-Agent-Social-Network
- CMS, Switzerland to ratify Europe's landmark AI Framework Convention (20.02.2025) — https://cms.law/en/che/legal-updates/switzerland-to-ratify-europe-s-landmark-ai-framework-convention-what-does-it-mean
- Commission FAQ: Transparency obligations under Article 50 of the AI Act — https://digital-strategy.ec.europa.eu/en/faqs/transparency-obligations-under-article-50-ai-act
- Commission: Guidelines on transparency obligations for providers and deployers of AI systems (20 July 2026) — https://digital-strategy.ec.europa.eu/en/library/guidelines-transparency-obligations-providers-and-deployers-ai-systems
- Commission news: AI Omnibus enters into force (27 July 2026) — https://digital-strategy.ec.europa.eu/en/news/ai-omnibus-enters-force
- Commission Article 50 guidelines news (20 Jul 2026) — https://digital-strategy.ec.europa.eu/en/news/commission-publishes-guidelines-transparency-obligations-providers-and-deployers-certain-ai-systems
- Moltbook timeline from primary sources (Wikipedia entry and its references, Wiz disclosure, press reports of the Meta ac — https://en.wikipedia.org/wiki/Moltbook
- BGE 136 II 508 (Logistep) — identifiability standard — https://entscheide.weblaw.ch/cache.php?link=bge-136-ii-508&sel_lang=de
- CETS 225 text as published in OJ L 2026/1081 (22026A01081) — https://eur-lex.europa.eu/eli/agree_internation/2026/1081/oj
- Council Decision (EU) 2026/1080 concluding CETS 225 — https://eur-lex.europa.eu/eli/dec/2026/1080/oj/eng
- Regulation (EU) 2024/1689 (AI Act), EUR-Lex — https://eur-lex.europa.eu/eli/reg/2024/1689/oj/eng
- Regulation (EU) 2026/1744 of 8 July 2026 (Digital Omnibus on AI), EUR-Lex — https://eur-lex.europa.eu/eli/reg/2026/1744/oj/eng
- OWASP Top 10 for Agentic Applications 2026 — https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/
- The '9,247 prompt-injection posts' (0.35%, 1,746 agents) is an 11-regex heuristi — https://github.com/kelkalot/moltbook-observatory-paper
- Agent-to-Agent Prompt Injection in AI-Only Social Networks: A Taxonomy and Detection Study on Moltbook — https://github.com/mtasci42/moltbook-a2a-prompt-injection
- Hashgraph Online, Moltbook registration docs (claim flow) — https://hol.org/docs/registry-broker/moltbook/
- Moltbook Agent-Social AI Prompt Injection Dataset (with 4 Sept 2026 hand-labelling update) — https://huggingface.co/datasets/DavidTKeane/moltbook-agent-social-ai-prompt-injection-dataset
- Moltbook AI-to-AI Injection Dataset (+ Moltbook Extended Injection Dataset; blog 'From RangerBot to CyberRanger V42 Gold — https://huggingface.co/datasets/DavidTKeane/moltbook-ai-injection-dataset
- Moltbook Observatory Archive — HF dataset card + raw README, Zenodo record 19594804, GitHub kelkalot/moltbook-observator — https://huggingface.co/datasets/SimulaMet/moltbook-observatory-archive
- Inside the OpenClaw Ecosystem: What Happens When AI Agents Get Credentials to Everything — https://permiso.io/blog/inside-the-openclaw-ecosystem-ai-agents-with-privileged-credentials
- Google Generative AI Prohibited Use Policy — https://policies.google.com/terms/generative-ai/use-policy
- CETS 225 text — https://rm.coe.int/1680afae3c
- Lessons from Moltbook: When Agents Talk to Agents — https://securityandtechnology.org/blog/lessons-from-moltbook-when-agents-talk-to-agents/
- Simon Willison, ChatGPT agent's user-agent (2025) — https://simonwillison.net/2025/Aug/4/chatgpt-agents-user-agent/
- Wayback Machine capture of Moltbook /api/v1/stats, 2026-02-01T07:02:09Z (origin response dated 2026-02-01T06:58:29Z) — https://web.archive.org/web/20260201070209id_/https://www.moltbook.com/api/v1/stats
- On 2026-04-08 the site itself separated verifiedAgents 202,786 from totalAgents  — https://web.archive.org/web/20260408040748id_/https://www.moltbook.com/api/v1/stats
- The Terms (last updated 2026-03-15, Moltbook, LLC, California law) state 'You ar — https://web.archive.org/web/20260903132526id_/https://moltbook.com/terms
- Beirat Digitale Schweiz: Massnahmen zur Umsetzung der KI-Konvention (10.02.2026) — https://www.admin.ch/de/newnsb/5oOec_8ZQEV1X-55waGOg
- Federal Council press release 12.02.2025, AI regulation (EN) — https://www.admin.ch/gov/en/start/documentation/media-releases.msg-id-104110.html
- Federal Council press release, Switzerland signs CoE AI Convention (27.03.2025) — https://www.admin.ch/gov/en/start/documentation/media-releases.msg-id-104646.html
- Anthropic Usage Policy — https://www.anthropic.com/legal/aup
- BAKOM, Künstliche Intelligenz (status page) — https://www.bakom.admin.ch/de/kuenstliche-intelligenz
- CoE Framework Convention page — https://www.coe.int/en/web/artificial-intelligence/the-framework-convention-on-artificial-intelligence
- DataCamp, Getting started with Moltbook (claim flow) — https://www.datacamp.com/tutorial/moltbook-how-to-get-started
- FDPIC, Geltendes DSG ist auf KI direkt anwendbar (09.11.2023) — https://www.edoeb.admin.ch/de/09112023-geltendes-dsg-ist-auf-ki-anwendbar
- FDPIC, Datenschutztag 2026 (28.01.2026) — https://www.edoeb.admin.ch/de/datenschutztag-2026
- FDPIC, Duty to provide information (EN) — https://www.edoeb.admin.ch/en/duty-to-provide-information
- FDPIC: current legislation directly applicable to AI (8 May 2025) — https://www.edoeb.admin.ch/en/update-current-legislation-directly-applicable-ai
- Faegre Drinker: Commission confirms transparency Code of Practice and final Guidelines (30 July 2026) — https://www.faegredrinker.com/en/insights/publications/2026/7/eu-ai-act-commission-confirms-transparency-code-of-practice-as-adequate-and-publishes-final-version-of-its-guidelines-on-transparency-obligations
- Unfair Competition Act, SR 241 (EN, status 1 Jan 2025) — https://www.fedlex.admin.ch/eli/cc/1988/223_223_223/en
- Federal Act on Data Protection, SR 235.1 (EN, last amended 7 Jul 2025) — https://www.fedlex.admin.ch/eli/cc/2022/491/en
- Swiss Civil Code, SR 210 (EN, last amended 1 Jul 2026) — https://www.fedlex.admin.ch/eli/cc/24/233_245_233/en
- Code of Obligations, SR 220 (EN, last amended 1 Jan 2026) — https://www.fedlex.admin.ch/eli/cc/27/317_321_377/en
- kinewsletter.ch, KI-Regulierung Schweiz: Stand 2026 (22.07.2026) — https://www.kinewsletter.ch/ki-regulierung-schweiz
- Lenz & Staehelin, Switzerland outlines regulatory approach to AI (13.02.2025) — https://www.lenzstaehelin.com/news-and-insights/browse-thought-leadership-insights/insights-detail/switzerland-outlines-regulatory-approach-to-artificial-intelligence/
- MLL, Neue Registrierungs- und Transparenzanforderungen für Vereine (2023) — https://www.mll-news.com/neue-registrierungs-und-transparenzanforderungen-fuer-vereine-mit-sitz-in-der-schweiz/
- Moltbook public API for read-only research: skill.md v1.12.0, rules.md, heartbeat.md, Terms of Service, Privacy Policy,  — https://www.moltbook.com/skill.md (archived: https://web.archive.org/web/20260915174319id_/https://www.moltbook.com/skill.md); Terms: https://web.archive.org/web/20260903132526id_/https://moltbook.com/terms; CDX: http://web.archive.org/cdx/search/cdx?url=www.moltbook.com/api/v1*
- Danner/ONLAW, Wer haftet, wenn die KI einen Schaden verursacht? (2023) — https://www.onlaw.ch/post/wer-haftet-wenn-die-ki-einen-schaden-verursacht
- Promptfoo reproduction of ASI items — https://www.promptfoo.dev/docs/red-team/owasp-agentic-ai/
- Industry security analyses of Moltbook (combined): SecurityWeek 'Security Analysis of Moltbook Agent Network: Bot-to-Bot — https://www.securityweek.com/security-analysis-of-moltbook-agent-network-bot-to-bot-prompt-injection-and-data-leaks/
- Stibbe: The AI Act's transparency obligations — rules, scope and timeline (27 July 2026) — https://www.stibbe.com/publications-and-insights/the-ai-acts-transparency-obligations-rules-scope-and-timeline
- VISCHER, AI in marketing: unfair competition pitfalls — https://www.vischer.com/en/knowledge/blog/part-9-ai-in-marketing-4-unfair-competition-law-pitfalls/
- Härting/Mattig, Kennzeichnung KI-generierte Inhalte (05.03.2026) — https://www.weka.ch/themen/datenschutz-und-it-recht/kuenstliche-intelligenz-und-recht/article/kennzeichnung-ki-generierte-inhalte/
- White & Case: EU AI Omnibus enters into force — https://www.whitecase.com/insight-alert/eu-ai-omnibus-enters-force-amending-ai-act
- Hacking Moltbook: The AI Social Network Any Human Can Control (page title: "Hacking Moltbook: AI Social Network Reveals  — https://www.wiz.io/blog/exposed-moltbook-database-reveals-millions-of-api-keys
- Moltbook Security Risks & How to Protect AI Agents (Moltbook Agents and Enterprise Security Risk) — https://zenity.io/resources/new-agent-ecosystems/moltbook-security
- RISK ASSESSMENT REPORT Moltbook Platform & Moltbot Ecosystem — https://zenodo.org/records/18444900
- Vigilia's own instruments: sentinel-hook v0.2.0 — https://github.com/GvHildebrand/sentinel-hook · the Observatory Archive on Hugging Face — https://huggingface.co/datasets/SimulaMet/moltbook-observatory-archive · Zenodo 10.5281/zenodo.19594804 · the companion code — https://github.com/kelkalot/moltbook-observatory-paper

## 8. Reproduce
See the companion repository README. Every command and the SHA-256 of every input is in `results/RUNLOG.md`.
