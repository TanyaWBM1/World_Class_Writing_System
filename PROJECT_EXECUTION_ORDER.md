PROJECT_EXECUTION_ORDER.md

I read both uploaded files thoroughly and used the later “WORLD CLASS WRITING SYSTEM — PROJECT SOURCE OF TRUTH” as the controlling document, since it is the most complete and newest articulation of the project. It defines the mission, core laws, tool roles, project structure, subagents, runtime controls, research pipeline, self-improvement loop, cadence priority, and immediate execution order.

Master answer: the correct order

There are really four different orders you need:

Tool order
Codex build order
Subagent creation order
Subagent runtime / operational order

You need all four, because “order” means something different depending on whether you are:

setting up the repo,
creating agent definitions,
ingesting research,
running the writing system,
or improving it over time.
1. Tool order

This is the highest-level order and it is already clearly defined in your notes:

Perplexity = researcher
Codex = builder
Claude Code = breaker
You = architecture + invention + approvals

So the correct tool sequence is:

Tool sequence
Step 1 — You define the source of truth

You lock the worldview first:

mission
core laws
invention direction
what counts as “world class”
what must never be automated
what must remain governed

This is explicitly your role: architecture, invention layer, pillar structure, and approval of runtime changes.

Step 2 — Perplexity researches

Perplexity comes before deep building. Its role is:

hard AI writing failure modes
lesser-known techniques
evaluation methods
genre-specific research
library-building research
robustness / stress-test research
Step 3 — Codex builds the system structure

Codex should not invent from nothing in one pass. It should build after research direction is known. It owns:

folder structure
subagents
schemas
scaffolding
research-ingestion pipeline
library architecture
enforcement / validation architecture
Step 4 — Claude Code stress-tests

Claude Code is explicitly not the architect. It comes after the initial structure and first passes exist. It is the red team for:

schema breakage
validator brittleness
GitBash-native testing
adversarial fixtures
cadence drift
voice drift
regression pressure
Step 5 — You approve evolution

No live runtime changes should happen from one output or from ungated agent behavior. Human/governance approval comes before promotion.

So at the tool level, the order is:

You → Perplexity → Codex → Claude Code → You

2. Codex build order

Your source-of-truth file gives an immediate execution order and a “What Codex should do first” block. That is the right backbone and should be followed exactly.

Correct Codex build order
Phase A — Bootstrap only

Do not build the engine yet.

Codex should first build:

Project skeleton
Charter files
Base subagent definitions
Schema placeholders
Library folder placeholders
Stress-test layer

This is the explicit “First Codex task” in your source of truth:

build folder structure
create charter files
create base subagents
create schema placeholders
create library folders
create stress test layer

That means the first Codex pass should create:

PROJECT_BOOTSTRAP.md
system_charter/*
agents/*
schemas/*
libraries/*
stress_tests/*
Phase B — Research prompt pack

Only after the structure exists should Codex create:

the first Perplexity research pack with four specialized prompts
Phase C — Research-ingestion system

Then Codex should create:

@research-architect
@research-evolution-architect
@library-builder-architect
the ingestion contracts and file paths for research/raw_exports/ → structured findings → proposals → libraries/
Phase D — Library architecture

Then Codex should formalize library schemas and loading logic for:

voice
genre
cadence
tone
sentence_structure
dialogue_behavior
human_texture
abstraction_control
sensory_grounding
narrative_pressure
continuity_state
failure_modes
benchmark_fixtures
and the additional libraries you listed.
Phase E — Evaluation and benchmark base

Only after ingestion and libraries are in place should Codex build:

benchmark fixtures
rubrics
regression structure
evaluation report schemas
enforcement report schemas
Phase F — First enforcement and validation passes

Then Codex builds the first actual system logic:

anti-abstraction
anti-repetition
cadence checks
continuity checks
dialogue seam checks
voice/genre/mode routing
validation reports
Phase G — Controlled runtime experiments

Only then should runtime generation experiments begin. Your source-of-truth explicitly says deeper runtime experiments come after:

clean repo structure
subagent charter
schema contracts
library architecture
Perplexity prompt pack
research-ingestion system
governed self-improvement loop
benchmark fixtures and evaluation passes
stress-test prompts for Claude Code

So the Codex build order is:

1. Skeleton → 2. Charter → 3. Base agents → 4. Schemas → 5. Library folders → 6. Stress-test layer → 7. Research prompt pack → 8. Ingestion agents/system → 9. Library architecture → 10. Benchmarks/evaluation → 11. Enforcement/validation passes → 12. Controlled runtime experiments

3. Subagent creation order

This is different from runtime order.

You do not want to create all subagents at once in equal priority. The best order is based on system dependency.

Tier 1 — Foundational architecture agents

These must exist first because everything else depends on them.

1. @runtime-designer

This is the anchor agent. It owns architecture and boundaries. It should be created first.

2. @schema-designer

You want contracts early so Codex does not invent structures ad hoc later. It owns templates, fixtures, run artifacts, reports, and JSON contracts.

3. @migration-architect

This should exist early because your notes repeatedly insist that legacy material must be classified correctly and must not leak into live runtime by default.

4. @research-architect

This is the first ingestion-side agent. It converts raw research into structured findings.

5. @research-evolution-architect

This takes findings and turns them into system proposals rather than direct changes. This is central to your governed improvement model.

6. @library-builder-architect

This converts research outputs into structured libraries. Because “research should become runtime assets, not just notes,” this agent is now foundational, not optional.

These six should be created first.

Tier 2 — Core writing-quality agents

These should be created after the foundational architecture agents.

7. @prose-enforcement-designer

Needed early because enforcement is authoritative, not advisory, and prose quality goals are central.

8. @continuity-designer

Needed early because continuity must be validated by state/meaning, not literal phrasing.

9. @dialogue-integrity-designer

Dialogue realism is one of your major stated pain points.

10. @human-texture-designer

This is one of your core invention zones and should be in the first serious wave of writing-behavior agents, not deferred too long.

11. @cadence-architect

This is also first-wave important because cadence is explicitly declared a core pillar and not a cosmetic layer.

12. @evaluation-designer

This should be created before serious runtime experiments, because your whole system depends on evaluation, benchmarks, critic calibration, and regression safety.

Tier 3 — Parameterized runtime control agents

These come next, after you have base quality and evaluation scaffolding.

13. @genre-research-architect

This agent defines genre as behavioral logic, not trope lists.

14. @voice-architect

This agent defines voice as behavior over time, not surface vocabulary.

15. @mode-orchestrator

This should come after genre and voice because it routes the behavior system for Creative vs ACF vs Hybrid. It needs the other two to mean anything.

Tier 4 — Stress and adversarial agents

These come after basic system components exist.

16. @stress-test-architect

This comes after there is something real to break. Its job is Claude Code / GitBash adversarial testing, not initial doctrine design.

Best subagent creation order

So the best full creation order is:

@runtime-designer
@schema-designer
@migration-architect
@research-architect
@research-evolution-architect
@library-builder-architect
@prose-enforcement-designer
@continuity-designer
@dialogue-integrity-designer
@human-texture-designer
@cadence-architect
@evaluation-designer
@genre-research-architect
@voice-architect
@mode-orchestrator
@stress-test-architect

That is the best creation order.

4. Subagent runtime / operational order

Now the most important distinction:

The best order to create agents is not the same as the best order to run them during system operation.

Your notes imply a runtime stack with research flow, library flow, parameterized controls, writing quality controls, evaluation, and governed learning.

There are actually three operational pipelines:

research pipeline
generation pipeline
improvement pipeline
A. Research pipeline order

This is the cleanest one because it is explicitly written in the source-of-truth file.

Correct research flow
Perplexity / autoresearch
research/raw_exports/
@research-architect
structured findings
@research-evolution-architect
system proposals
@library-builder-architect
libraries/
runtime + evaluation + benchmarks

So the research agent order is:

@research-architect → @research-evolution-architect → @library-builder-architect

That order should not be changed.

Reason:

first you extract understanding,
then you decide what that understanding means for the system,
then you materialize the reusable assets.
B. Generation pipeline order

This is the order for an actual writing run.

Your notes define the parameterized runtime input as:

mode
genre
voice
tone profile
cadence profile
grit level
constraints

The best runtime order is:

Step 1 — @mode-orchestrator

The run starts here because mode decides the overall route:

Creative
ACF
Hybrid
Step 2 — @genre-research-architect

Genre behavior should shape:

pacing
scene pressure
dialogue behavior
structure tendencies
cliché risks

This is upstream behavior logic.

Step 3 — @voice-architect

Voice then narrows the behavior pattern:

sentence tendencies
phrasing behavior
emotional distance
rhythm tendencies
Step 4 — library resolution

At this point the system should pull the relevant library entries:

voice library
genre library
cadence library
tone library
dialogue behavior library
human texture library
abstraction control library
continuity/state library
failure mode library
benchmark fixture references where needed

This is not a named subagent in your notes, but functionally it belongs to the orchestration layer.

Step 5 — draft generation runtime

This is the prose-generation stage inside runtime/orchestration/generation.

Step 6 — @continuity-designer

Check state and meaning continuity before beautifying prose too much.

Step 7 — @cadence-architect

Then analyze sentence cadence, rhythm, pacing, symmetry patterns, predictable loops, emphasis placement, breath pattern. Cadence is a pillar, so it must not be left to the end as cosmetic polish.

Step 8 — @human-texture-designer

Then apply / validate the human texture dimension:

dual-lane ideas
irregularity
micro-variation
non-machine feel
invisible variation systems
controlled human friction
Step 9 — @dialogue-integrity-designer

Dialogue should get a dedicated pass, especially for seams, stiffness, exposition dumping, and unnatural line behavior.

Step 10 — @prose-enforcement-designer

Now enforce hard quality rules:

anti-abstraction
anti-repetition
anti-machine-rhythm
over-explanation checks
symmetry breaking where needed
Step 11 — @evaluation-designer

Now score and evaluate:

benchmark alignment
human-like quality
regression risk
quality dimensions
acceptance criteria
Step 12 — artifact generation

Produce:

run artifact
evaluation report
enforcement report
failure map if needed

So the best generation-time subagent order is:

@mode-orchestrator → @genre-research-architect → @voice-architect → generation runtime → @continuity-designer → @cadence-architect → @human-texture-designer → @dialogue-integrity-designer → @prose-enforcement-designer → @evaluation-designer

That is the cleanest operational order.

C. Improvement loop order

This is also explicitly defined in the source-of-truth file.

Correct governed self-improvement order
Generate output
Evaluate with separate evaluator agents
Extract structured failures
Propose:
enforcement changes
schema changes
benchmark additions
routing changes
Apply human or governance approval
Replay benchmark set
Promote only if no regressions

Mapped to your subagents, the improvement loop is:

runtime generation
@evaluation-designer
structured failure extraction
@research-evolution-architect or dedicated proposal layer
human approval
regression replay
promote changes
optionally push new patterns into libraries through @library-builder-architect

Important law:
No agent may directly modify live runtime rules from a single output.

So the improvement loop agent order is roughly:

generation stack → @evaluation-designer → failure extraction → @research-evolution-architect → human/governance gate → regression replay → @library-builder-architect / runtime update

The single best end-to-end order for your project

If you want one master sequence from zero to serious operation, this is the right one.

Stage 0 — Human source-of-truth lock

You finalize:

mission
laws
modes
voice/genre stance
cadence as pillar
innovation principles
governance rules

This is already captured in your source-of-truth doc.

Stage 1 — Codex bootstrap

Use Codex to create:

project skeleton
charter files
base subagents
schema placeholders
library folders
stress-test layer
Stage 2 — Perplexity research pack

Create and run the four research tracks:

core failure modes
evaluation and benchmarking
lesser-known techniques and hidden craft
system design and governed self-improvement
Stage 3 — Research ingestion

Run:

@research-architect
@research-evolution-architect
@library-builder-architect
Stage 4 — Library formation

Populate at minimum:

Voice
Genre
Cadence
Tone
Sentence Structure
Dialogue Behavior
Abstraction Control
Continuity / State
Failure Modes
Benchmark Fixtures
Stage 5 — Core quality system

Then build the first working behavior/evaluation stack:

@prose-enforcement-designer
@continuity-designer
@dialogue-integrity-designer
@human-texture-designer
@cadence-architect
@evaluation-designer
Stage 6 — Parameterized control

Then build and connect:

@genre-research-architect
@voice-architect
@mode-orchestrator
Stage 7 — Benchmark and validation base

Then create:

benchmark fixtures
rubrics
regression passes
evaluation and enforcement reports
Stage 8 — Claude Code red-team layer

Then use:

@stress-test-architect
GitBash runs
adversarial fixtures
regression pressure
validator/schema break testing
Stage 9 — Controlled runtime experiments

Only after all the above:

short scenes
dialogue scenes
emotional scenes
exposition passages
continuity runs
cross-genre runs
voice-preservation runs
cadence-drift tests
Stage 10 — Governed self-improvement

Then continuously run:

generate
evaluate
extract failures
propose changes
approve
replay benchmarks
promote only if safe
Final recommended order, simplified into one clean stack
Codex order
repo structure
charter files
base subagents
schema placeholders
library folders
stress-test folders
Perplexity prompt pack
research-ingestion agents/system
library architecture
benchmarks and rubrics
first enforcement/validation passes
controlled runtime experiments
Subagent creation order
@runtime-designer
@schema-designer
@migration-architect
@research-architect
@research-evolution-architect
@library-builder-architect
@prose-enforcement-designer
@continuity-designer
@dialogue-integrity-designer
@human-texture-designer
@cadence-architect
@evaluation-designer
@genre-research-architect
@voice-architect
@mode-orchestrator
@stress-test-architect
Research pipeline order
Perplexity / autoresearch
research/raw_exports/
@research-architect
@research-evolution-architect
@library-builder-architect
libraries
runtime + evaluation + benchmarks
Runtime generation order
@mode-orchestrator
@genre-research-architect
@voice-architect
generation runtime
@continuity-designer
@cadence-architect
@human-texture-designer
@dialogue-integrity-designer
@prose-enforcement-designer
@evaluation-designer
Improvement loop order
generate
evaluate
extract failures
propose changes
human/governance approval
replay benchmark set
promote only if no regressions
My direct recommendation

Use this as your immediate working order for the new project:

First Codex pass: repo + charter + base agents + schemas + library folders + stress-test layer.
Second pass: Perplexity research pack + research ingestion agents.
Third pass: library schemas and initial library population flow.
Fourth pass: core quality agents and evaluation scaffolding.
Fifth pass: parameterized runtime controls for genre, voice, and mode.
Sixth pass: Claude Code adversarial testing.
Seventh pass: controlled writing experiments.
Eighth pass onward: governed self-improvement.

The controlling source for that order is your uploaded “source of truth” document plus the earlier project notes.

I can turn this into a single PROJECT_EXECUTION_ORDER.md you can paste directly into the new repo.