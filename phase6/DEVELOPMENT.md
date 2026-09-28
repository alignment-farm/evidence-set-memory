# Source-edit development findings

Two sequential authored edits in pinned python-dotenv, fixed local reader, at
most four read/edit calls per attempt. Complete means unchanged upstream tests,
current public/held-out tests and all previously accepted tests pass. Raw requests,
patches, failures and native results are under `runs/development` and `runs/packaging`.

| Initial evidence policy | Escaping edit | Precedence edit | Total logical tokens |
|---|---:|---:|---:|
| Ordinary dependency-expanded chunks | pass | pass | 25,568 |
| All production source as chunks | pass | pass | 47,719 |
| Pointwise top-three definitions + headers | pass | pass | 15,873 |
| Root-only definition + header | fail | pass | 36,150 |
| Ordinary-selected whole files | fail | pass | 60,054 |
| All production files intact | fail | pass | 74,321 |

Token totals include repeated conversation context, explicit source/test reads and
repair. They are not initial-context lengths, dollar charges or isolated latency
measurements. All policies could read any production source/upstream test file.
Whole-file packaging did not improve this reader's result; retain the successful
chunked alternatives as the ordinary/broad controls rather than assuming otherwise.

All three failures occur on quoted-backslash serialization. The failed reader edits
double escape characters **after** introducing escapes for quotes, which breaks
existing quote-only tests. A later patch undoes the change, restoring the original
backslash bug. Root-only then spends its final call reading tests; the two whole-file
arms end with invalid JSON objects on their final calls. These are observed semantic,
format and budget failures, not absent-candidate evidence or an annotated-support
recall deficit. Successful attempts produce the proper escape ordering and pass
the additional variants.

Actual accepted history uses the ordinary successful patch after each task. The
fixed reader adds the requested `dotenv_values(..., override=True)` parameter,
forwards it to existing behavior and updates its documentation. This is real
executed source editing, not answer-only QA. Upstream source remains unmodified;
canonical changed snapshots are experiment artifacts.

The six-weight energy learns 25/30 observed pair preferences and chooses successful
proposals for both development tasks, but misses the cheapest choice on the first.
Simple empirical policy reuse selects pointwise, already better on aggregate native
tokens. Leave-one-task-out fits also select pointwise, with only two cases. These
are development diagnostics, not fresh transfer or population-level generalization.
No necessity labels or reference fix supplied the training targets.

A separate cosmetic-output control removes only pytest elapsed times/object
addresses from reader-facing logs. The already-seen precedence task then passes
twice with identical request hashes: one physical completion, two logical attempts.
Raw logs remain intact. Transfer is frozen at `fa9f5e7`; its results are reported
separately after completion, without updating these development checkpoints.
