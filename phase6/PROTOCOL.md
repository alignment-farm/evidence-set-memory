# Phase 6 — source-native code-edit pilot

Declared 28 September 2026 before participant calls. Prior phases remain unchanged.
User explicitly authorized executable code-edit tasks with a fixed reader.

## Asset and scope

Use python-dotenv v1.0.1, commit
`d6c0b9638349a7dd605d60ee555ff60421c1a594`, cloned from the upstream public repository.
Its source, license and tests are inspectable; no future upstream patch or benchmark
solution is used as the participant's answer. The code/test base is source-native.
Requests and added acceptance/held-out tests are study-authored, not historical
issues or naturally accumulated user sessions. Inspect and run the upstream suite
before admitting this asset. Keep its existing tests unchanged. Test dependencies
have a separate phase-local uv project so earlier frozen lockfiles are untouched.

Start with two development edits: preserve quoted backslashes when writing values,
and expose existing interpolation-precedence behavior through `dotenv_values`.
Later requests will be materialized separately after development and claim freeze.
They must preserve earlier accepted behavior and original regression tests.
The compiler/test runner, not an answer string or support annotation, grades the
actual changed source. All arms have identical code access, current requirements,
scope rules, prior source changes and repair opportunities.

## Fixed reader and isolation

Choose the already available DMR tag `docker.io/ai/qwen3.8:27b-q4_K_M`, immutable
reported model ID `sha256:f04d0a543b642a6f0d06590973b124bc4e8700ddf7e99b669ec6c4ab1ef561ef`.
Pin the actual returned model path/digest, temperature 0, seed 761 and completion
cap after development interface validation. No model substitution based on quality.
The investigator is not the participant: observed gpt-6-astra, reasoning high,
OpenAI/Codex 0.158.0, session 01a0e7e4-68e2-7fb2-9a5d-2ea6873b86b8. Backend build and
investigator spend remain unknown. No subagent/reviewer is dispatched.

Participant returns JSON exact-match source replacements or explicit source-read
requests. Edits are restricted to existing production Python files in an isolated
copy. No tests, dependencies, evaluator or study files may be edited. Parse source
before execution. Tests run in bounded subprocesses, with minimal environment,
network denied and filesystem writes restricted to the owned case directory using
macOS sandbox-exec. Preserve raw requests, responses, patches, test logs and errors.

Before inference, no DMR model was loaded and no competing inference job was
visible. Use serial requests, advertise this study's use here, and recheck process/
model state before heavy jobs. This passive shared-machine coordination is not an
exclusive lease or an isolated timing guarantee. No sibling experiment is edited.

## Evidence and experience

Construct AST top-level source records with intact definitions and file headers.
All policies see a source inventory, current task/public examples and scope rules.
The primary reader can request any production source file regardless of initial
selection. This separates initial evidence delivery from candidate reachability.
Recovering omitted source is allowed and charged; compactness cannot be won by
forbidding ordinary access. Existing tests and completed earlier source changes
remain legitimate ordinary memory, not privileged learner supervision.

Compare broad source access, competent ordinary symbol/lexical retrieval with
dependency expansion, and a small set-energy policy if eligible development
executions provide a learnable contrast. Candidate sets are scored separately
from primary reading, valid patch application and complete test outcomes. Include
deliberate small/omitted evidence proposals during development to diagnose whether
source selection actually matters. These are acquisition probes, not the ordinary
baseline. Do not require a neural win to continue or manufacture one with weak access.

Learn only from earlier attempted edits and their executed outcomes/costs. Labels
are completed-task feedback, not authored relevant-file lists. Authored tests,
ordinary proposal teaching and learner-earned feedback are distinguished. Do not
train on later tests, reference fixes or future requirements. If feedback is too
small or invariant to identify a useful selector, report that limit and diagnose
it rather than promoting a static ranking score to continuing experience.

Within one attempt the reader may expand source and repair based on public test/
format errors. Hidden held-out failures never trigger repair. Between attempts
reset conversation, temporary code and interpreter state. Accepted earlier code,
source-linked attempt artifacts and learned selector weights may persist; declare
exactly which. Freeze after development, then run fresh requirements in a new
process. A canonical accepted change may advance shared source history only after
passing all applicable tests, with chosen attempt and source hashes recorded.

## Bounded work and publication

Initial acquisition: two tasks with a small diverse set of evidence proposals,
up to four reader calls per attempt including source reads/repair. Diagnose the
interface and task boundary before freezing. Fresh pilot: two new edits plus
retention tests, ordinary/broad/learned-or-explained-alternative comparison. Keep
request totals bounded and report actual retries, native tokens, runtime, tests,
representation building and training, including unsuccessful recipes.

The stopping condition is a validated source-native workload and an informative
complete-task comparison or explained concrete limit. Two tasks are not evidence
of broad code-repair generalization. Publish findings locally and keep README
current, with exact asset/runtime/code versions, authorship and reproduction paths.
