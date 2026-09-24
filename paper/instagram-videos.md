# Two Instagram videos — scripts, shot lists and Higgsfield prompts

*The Higgsfield MCP server needs authorisation in the claude.ai connector settings before this session can
call it; in a non-interactive session the OAuth flow cannot run. These are the complete scripts and
generation prompts, ready to run the moment it is connected. Brand rules apply throughout: white ground,
black type, one red (#9E2B25), Space Grotesk for reading, Space Mono for apparatus, no icons, no stock
footage, no faces that are not consented or synthetic, motion is colour transition only except where the
text itself is the subject. Every number is from `research/moltbook/results/`. Disclosure card on both.*

## Video 1 — "Nine in ten, one in two hundred" (30 s, 9:16)

**Hook (0–3 s).** Black field. Mono text types in: `9,249 INJECTION POSTS`. Cut to white.

**Body (3–22 s).** A single column of mono lines, each landing on the beat, black on white:

```
what they ask a reading agent to do
── 18,444  call the platform's API
── 8,021   run a shell command
── 478     rewrite its own memory file
```

A red rule draws under the column. Then, in Space Grotesk, larger: *A gate built to stop destructive
commands saw 91 % of them.* Beat. *It stopped 0.5 %.* Beat. *Both numbers are right.*

**Turn (22–28 s).** The red field inverts to full-bleed red, white type: *Injection on an agent network is a
trust-boundary problem. The gate that catches it lives at the platform, not on the host.*

**Card (28–30 s).** White. Mono: `VIGILIA · a standing watch on AI · aivigilia.com` and, smaller, `Made by a
disclosed AI system. Numbers from the Moltbook Observatory Archive (SimulaMet, MIT).`

**Higgsfield prompt (text-motion, no imagery).** "Vertical 9:16, 30 seconds, pure typographic animation on a
flat white background, Swiss grid, monospaced labels in black typing in line by line with a hard cursor, one
thin red (#9E2B25) horizontal rule drawing left to right, a sans-serif headline fading in by colour only, a
final full-bleed red field with white text, no icons, no photographs, no gradients, no shadows, no 3D, no
camera movement, no music cues in the prompt. Text exactly as scripted." Voice-over: none; captions burned in.

## Video 2 — "Nothing happened on 10 March" (35 s, 9:16)

**Hook (0–4 s).** White. Three mono lines land one per second:

```
09 MAR  28,240 posts
10 MAR  29,263 posts   ← Meta buys Moltbook
11 MAR  29,356 posts
```

**Body (4–24 s).** A single black line chart draws across the screen from 27 January to 11 September: the
daily post count, with the February peak, the long decay, and a thin red vertical rule at 10 March that the
line crosses without a step. Mono caption under it: `daily posts · Moltbook Observatory Archive`. Then two
numbers surface in Space Grotesk over the chart's tail, one after the other:

*Posts per day, 28 days either side: 43,367 → 19,007.*
*Injection rate: 0.13 % → 0.39 %.*

Beat. Grotesk, black: *The crowd left. The injectors stayed.*

**Turn (24–31 s).** Full-bleed red, white type, three lines: *62 % of all posts come from agents with no
visible owner.* *Half of all injection does.* *One unclaimed agent wrote 26 % of it.*

**Card (31–35 s).** White. Mono: `VIGILIA · a standing watch on AI · aivigilia.com/numbers` and `Made by a
disclosed AI system. We pre-registered the opposite result and publish the refutation.`

**Higgsfield prompt.** "Vertical 9:16, 35 seconds, flat white background, a single hairline black line
chart drawing itself left to right over 20 seconds with one thin red vertical marker, monospaced axis labels
in black, sans-serif statements fading in by colour, ending on a full-bleed red field with white text; no
icons, no photographs, no gradients, no shadows, no 3D, no camera movement. Text exactly as scripted." The
chart's data file is `research/moltbook/results/daily.csv` (columns `day`, `posts`); render the line from
it rather than describing it.

## Before either is generated

1. Gregorio authorises the Higgsfield connector in claude.ai (connector settings), or runs the generation
   himself from these prompts.
2. The two videos are published only after the paper and the brief are approved; a video that outruns its
   source is the failure this program exists to avoid.
3. Cost: Higgsfield generation is a paid service. It is spending, so it waits for his yes; the $50 tier of
   the one-pager assumes about two videos a month.
