# Source-native editing: useful compact delivery, no learned-energy advantage

Published locally 28 September 2026. Investigator: observed gpt-6-astra/high,
OpenAI Codex CLI 0.158.0, session `01a0e7e4-68e2-7fb2-9a5d-2ea6873b86b8`.
No independent reviewer ran; root scientific review remains separate.

The pilot establishes an executable source-edit regime and a functioning small
experience-fitted selector. It does **not** establish a benefit of learned energy
over competent ordinary reuse. On both later tasks, the energy chooses precisely
the same pointwise proposal as the empirical best-policy baseline. They receive
identical reader deliveries and outcomes; energy adds training and proposal work.
Source availability and public-test success do not guarantee complete behavior.

## Workload, acquisition and comparison

Pinned python-dotenv v1.0.1 (`d6c0b9638349a7dd605d60ee555ff60421c1a594`)
supplies real production source and unchanged executable upstream tests: 149 pass,
one optional IPython integration skips. Requests, added tests and episode chronology
are authored here, not upstream issues or naturally collected user experience.
See [sources](SOURCES.md), [protocol](PROTOCOL.md) and [development](DEVELOPMENT.md).

Two earlier edits teach literal-backslash serialization and interpolation-precedence
forwarding. Six evidence policies produce 12 executed attempts, nine complete.
Root-only and both whole-file policies fail the escaping edit; correct ordering
of escaping operations, valid patch format and repair budget matter. Whole-file
delivery is preserved as an unsuccessful diagnosis, not silently discarded.
Chunked ordinary dependency expansion, all-source access and top-three definitions
each complete both. Packaging choices for the later ordinary/broad baselines are
chosen by earlier complete quality, then native token cost.

The learner has six linear coefficients over set size, request/public-example
coverage, resolved/unresolved source-symbol edges and packaging. Pairwise preferences
come from earlier actual complete quality, then total reader token cost—not file
relevance labels, reference fixes or future answers. Authored evaluators supply the
feedback; the exploration policies are investigator-designed, not autonomously
discovered. There are 30 dependent pairs from just two tasks: nine quality contrasts
and 21 within-quality cost contrasts. Adam fits 25/30 orderings in 800 CPU steps.
It chooses successful seen proposals but misses the cheapest one on the first task.
Two leave-one-task-out fits are development diagnostics, not additional transfer.

This is an earlier-to-later **authored executable experience contrast**, not static
QA relabeled as sessions. It is also not evidence of natural continuing workload
learning. The serious nonparametric alternative simply reuses the cheapest policy
with maximal earlier completion: pointwise. The ordinary dependency policy assembles
sets using named APIs, lexical overlap and two rounds of source-symbol expansion.
Both ordinary assembly and learned features are set-aware; pointwise is not the
only competitor.

Energy inference enumerates six public proposals and chooses minimum linear energy.
Its negative is exactly a set score with the reverse sign: no different ordering
or inference-time continuous minimization method is claimed. Training gradients
update persistent coefficients, not the evidence set at inference. This phase tests
learned set preference, not a new EBM optimizer or neural architecture advantage.

## Frozen later outcomes

Freeze: `fa9f5e7db94810f017baedec7851785d88e2623f`; 33 pinned files verify.
Fixed reader: reported Qwen3.8 27B Q4_K_M GGUF digest
`f04d0a543b642a6f0d06590973b124bc4e8700ddf7e99b669ec6c4ab1ef561ef`.
Temperature 0, seed 761, response cap 4,096, at most four calls including reads
and public-failure repair. All policies may read every production file, upstream
test and README. All receive current requirements, source inventory, accepted prior
patch memory and scope rules. No current held-out failure enters a repair call.

| Policy | Literal `get_key` | Preserve line endings | Total logical tokens | Calls |
|---|---|---|---:|---:|
| Ordinary dependency-expanded chunks | complete | public pass; 1/6 hidden fails | 59,596 | 5 |
| All production source as chunks | complete | public pass; 1/6 hidden fails | 105,130 | 5 |
| Empirical best-policy reuse | complete | public pass; 3/6 hidden fail | 52,285 | 5 |
| Learned energy | complete | public pass; 3/6 hidden fail | 52,285 | 5 |

Tokens include repeated context, explicit reads, invalid responses and repairs.
Each API-extension attempt uses one call; each newline attempt uses four. Identical
energy/reuse request hashes share physical completions, so their tie is a delivery
identity, not independent model replications. There are two new edit instances,
not eight independent tasks. The compact policies are cheapest at equal **binary**
completion, but worse on the failed task's partial behavior; do not suppress that
ordinary-method advantage or call compactness sufficient usefulness.

The API extension forwards `interpolate=False` through `get_key`, retaining defaults,
encoding, missing keys and earlier changes. It closely resembles the earlier
forwarding edit: near transfer, not distant generalization. Its accepted canonical
patch is the first passing ordinary attempt, shared by every later policy.

On line endings, ordinary/broad patches choose CRLF if it appears **anywhere**.
The explicit requirement instead says the **first** encountered LF/CRLF style.
Compact reuse/energy update the style while traversing records, using later/current
endings rather than consistently the first. All can access and do read the relevant
source. Their public CRLF example does not distinguish these rules. Tests with
mixed endings do, producing the saved failures. This is a primary implementation
and public-test-coverage limit, not evidence of unreachable candidates. It does
not prove selection is irrelevant in other tasks.

The [post-hoc intervention](SEMANTIC_DIAGNOSIS.md) reconstructs the ordinary failed
patch byte-for-byte and changes only its detector to inspect the first LF and
its preceding byte-character. Before: 178 pass, one fails, one skips. After: 179
pass, one skips. All upstream, earlier and current tests run together. This is an
unblinded investigator-authored repair, **not** another reader success, eligible
training example, proof of exhaustive correctness, or revised frozen outcome.

No policy produces an accepted newline revision. The canonical history therefore
stops after the API extension. Both old obligations pass retention probes there
with zero reader calls. These are maintenance checks after one accepted update,
not successful retention after the rejected newline edit or two extra edit wins.

## Persistence, feedback and provenance correction

Between attempts, reader conversations, working copies and Python subprocesses
reset. Immutable source records/logs, accepted source snapshots, prior patch memory,
retained old tests and learned coefficients survive. Representations are rebuilt
from the current source; there is no separately trained encoder. Within a run,
exact normalized requests cache completions. Serving prefix-cache token counts
are reported, but are not semantic learning. Public execution/format failures
permit repair; only completed earlier attempts' evaluation supplies acquisition
labels. No transfer labels update the selector or prompt.

Correction to the archived claim/protocol wording: later task definitions already
appear in the frozen `phase6_transfer.py`. They were written **after acquisition
but before freezing**, and serialized/executed in a fresh process after freezing.
“Generated after freeze” is therefore too strong. Eligible acquisition reads only
earlier task/source/outcome files; exact replay confirms the examples/weights.
This is held-out-from-training execution, not investigator-blinded task creation.
The frozen files are retained unchanged so this correction is auditable.

## Costs and verification

[Native ledger](runs/audit/native-costs.json) and
[verification supplement](runs/verification/verification.json) separate experimental,
audit and post-hoc costs. Development: 25 physical reader calls including packaging;
interface control: one; transfer: 15. Total **41 calls, 469,523 prompt tokens,
11,774 completion tokens**, 1,863.83 seconds of request wall time. Failed recipes,
source expansion and repair are included. No fallback model or unreported successful
canonical fix is substituted. Server reports 257,273 cached prompt tokens across
these calls. Neither tokens nor cached tokens are dollar/energy measurements.

The main fit takes 0.7224 seconds; example construction 0.0563 seconds; two development
leave-one-task-out fits total 0.1138 seconds. Later learned proposal selection
totals 0.0552 seconds versus empirical reuse's 0.00187 seconds. Recorded per-attempt
representation and selection timings are available, but not exhaustive: six outer
transfer scans and one interface-control scan (eight source files each) execute
with discarded timers. Copying/hashing/serialization, investigator compute and
authored-label labor are not fully timed. No latency dominance is inferred from
these tiny non-isolated measurements. No pretrained encoder costs are hidden.

There are 80 original native pytest invocations including failed sandbox preflights;
48 audit replays and two post-hoc intervention invocations are separately charged.
The audit reproduces all 24 attempt/probe source hashes and complete grades,
verifies unmodified tests, 47 logical request identities/private-test-name checks
and all 33 frozen hashes. These checks plus code inspection support the boundary;
absence of a private function name alone is not a general nonleakage proof.
The six-weight fit and both diagnostic fits replay bit-for-bit. All 22 repository
boundary tests pass. [Reproduction](REPRODUCE.md) gives exact commands and versions.

## Limits and next bounded step

One public project, two earlier and two later authored tasks, one reader, one seed,
small authored test suites and correlated policies. Pretraining exposure to source
is unknown. The common reader interface permits reads and edits with automatic
public testing, but not participant-authored scratch tests or arbitrary shell work.
The four-call cap and early stopping on public success constrain competence for
every arm. Thus this is not a comparison against a full production coding agent.
The current data cannot identify a general neural, energy, transfer or maintenance
advantage. Backend build, investigator spend and machine joules remain unknown.

Close this phase on explanatory progress: the learner functions, source-native
complete work is measured, simple reuse matches it, and a concrete reader error
is isolated beyond an initial failed recipe. A next bounded phase should give the
same fixed reader ordinary scratch-test/self-check access, develop that interface
on these now-exposed failures, freeze it, then use genuinely new edits in another
small source project. Keep the ordinary policy and empirical reuse strong, charge
self-check/repair work, and only add a richer energy if a new development contrast
motivates it. Do not recycle the exposed mixed-ending case as fresh confirmation.
The broader investigation remains open; no sibling experiment was modified.
