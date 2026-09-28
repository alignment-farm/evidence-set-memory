# Phase 6 source selection and limitations

Selected [python-dotenv v1.0.1](https://github.com/theskumar/python-dotenv/tree/v1.0.1),
resolved and checked at commit `d6c0b9638349a7dd605d60ee555ff60421c1a594`.
Shallow Git clone, 39 working-tree files hashed in `assets/source-manifest.json`.
The upstream variables implementation was also inspected via its public GitHub
page; one web fetch of the repository tree failed, while the Git clone succeeded.
Selection is based on obtainable source, small executable regressions, explicit
parser/serializer and interpolation interactions—not an expected learned win.

The source is used under its three-clause BSD license, preserved verbatim in
`UPSTREAM_LICENSE.txt`; that license also covers upstream text inside archived
reader requests and canonical source snapshots. Original authors retain copyright.
The future task requests, added tests, chronology, selectors and harness are authored
locally. This is not an upstream issue dataset, human developer trajectory, or
claim that the modifications were requested/accepted by the upstream maintainers.

Checked asset: unchanged upstream tests with 149 passes and one skip (IPython is
not installed), Python 3.12.14, pytest 8.3.5, click 8.1.8, sh 2.2.2. The remaining
versions/hashes are phase-local `uv.lock`. No upstream test was disabled to admit
the task. Console-script tests use the project's standard `dotenv.cli:cli` entry
point through a case-local wrapper, importing that case's edited `src` directory.
The first two sandbox preflights failed because `/dev/null` and pseudo-terminal
devices were denied; both logs are retained. The final profile permits those
devices, blocks network and confines regular-file writes to the isolated case.
It is not a fully hermetic VM or a comprehensive adversarial-code security claim.

Current tasks have public requirement/examples and additional held-out tests.
They must also retain all earlier accepted task tests and upstream behavior.
Held-out tests are authored checks of the stated requirement, not a proof of all
possible behavior. Previously completed task tests become legitimate retained
requirements in later work. No future task is exposed to the reader or acquisition.

Candidate records are AST top-level definitions and module-level material from
eight production Python files. Representation scans the whole production source;
this work is charged. Source inventory and explicit read access include upstream
tests and README as well as production code. Selection cannot claim to discover
missing candidates: all code is recoverable, and subsequent reads are charged.

Reader is the existing reported Qwen3.8 27B Q4_K_M tag/digest, not independently
verified architecture/quantization metadata. First response returns the expected
digest-bearing local GGUF path. Prior exposure to the old public code is unknown;
new requests do not establish absence of pretrained source knowledge.
No external participant calls other than serial DMR requests, upstream write,
model download, other-study edit or arXiv API request occurred in setup.
