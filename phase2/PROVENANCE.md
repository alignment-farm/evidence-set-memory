# Phase 2 provenance and source boundaries

Started at study ad01b74421d2297356ba92bd67584e1667cb4fdf with a clean worktree.
Active session 01a0e7e4-68e2-7fb2-9a5d-2ea6873b86b8, observed `turn_context.model`
gpt-6-astra and `effort` **high**. OpenAI/Codex 0.158.0. No independent backend
fingerprint or investigator monetary cost. No delegated investigator/reviewer.
Root scientific review is separate from the investigator's checks.

User's continuation authorizes further experiments and energy exploration without
waiting for routine approval. Existing study scope and evidence boundaries remain.
Machine checks found no loaded serving model or active inference before the new
reader launch. Serving remains serial and bounded; local training uses two CPU
threads. No formal cross-study lease protocol was found. No other study is edited.

Source asset: author-linked raw MuSiQue-Ans dev, repository
922ac98f19a201998dbdae6d7f2887a5258dbdeb, full file SHA-256
76eb07a2cd7b60b3336374a28097e90867f979791023f5626e7397dc2d083dd5,
42,457,393 bytes, 2,417 records. The Google Drive object is not version-pinned;
reacquisition must match the recorded hash. Reconnaissance reconstruction added
61,376,036 payload bytes before the full-file acquisition. Retained downloaded
source text stays in ignored `.cache`; CC BY 4.0 attribution is to the authors of
MuSiQue as recorded in the pinned repository. The original code/metrics are used
under that repository's license; our harness imports the author's answer metric.

Inspected pinned author `raw_data_to_official_format.py` for field and alias
boundaries, plus cached `metrics/answer.py`. Our converter retains original raw
composed IDs rather than translating them, and filters aliases to those occurring
in source text. Original paragraph support flags and single-hop IDs are evaluator/
split metadata only. Original retrieval score, primary flag and Wikipedia IDs
are omitted from input. Training/development/confirmation have disjoint single-hop
IDs; their distractor passages may still overlap and are audited separately.

Methods background: phase 1's exact-version SPEN, ParaSet/SetCE and MSS-Complement
ledger remains relevant. This phase implements a query-conditioned quadratic
selection energy with small nonlinear coefficient networks. It does not reproduce
those papers' architectures or imply a new set-retrieval method. No arXiv discovery
or metadata calls occurred. PyTorch's official [autograd documentation](https://docs.pytorch.org/docs/2.14/generated/torch.autograd.grad.html)
was checked; an analytical selection-gradient equality test was executed.
SentenceTransformer documentation was inspected and a semantic representation
diagnostic was subsequently adopted. The frozen encoder is all-MiniLM-L6-v2 at
revision 1110a243fdf4706b3f48f1d95db1a4f5529b4d41, 22,713,216 frozen parameters,
384 dimensions and a 256-token input limit. Its imported pretraining is distinct
from our learned specialist, and its token/caching/truncation costs are recorded.
The model card lists QA-related pretraining sources; no absence of contamination
is claimed. This is not a 674-parameter end-to-end system.

Python 3.12.14, NumPy 2.5.3 and PyTorch 2.14.0 are locked by uv.lock. Parameters
are actually updated through torch CPU autograd/AdamW. Relaxed selection uses the
equivalent analytic gradient of the frozen quadratic score; it does not update
model weights. Full package resolver versions/hashes are in uv.lock. Package
download logs reported torch 121.4 MiB and networkx 2.0 MiB; complete installer
network transfer was not instrumented. No foundation-model training is performed.

Chosen reader is the available DMR tag docker.io/ai/qwen3.8:27b-q4_K_M, local model
digest sha256:f04d0a543b642a6f0d06590973b124bc4e8700ddf7e99b669ec6c4ab1ef561ef.
Model inspection reports GGUF but no architecture/parameter/quantization fields;
27b and q4_K_M are tag descriptions, not independently verified metadata. Use
raw completion responses for actual returned model identity. Reader context resets
each request; temperature 0, seed 761, max_tokens 256 and thinking disabled are
requested, not independently certified. No reader weight download is required.
The pretrained encoder was downloaded separately. The reader's final cap is 1,024
after two preserved development interface revisions; raw requests are authoritative.
Docker's API documentation says JSON-object mode is supported, but observed
responses did not consistently obey it. Final schema-object extraction is a
deterministic public formatting repair, fixed before confirmation.

Costs include representation construction, training plus checkpoint-selection
validation, all search work, actual reader requests and counterfactual per-policy
fallback tokens. Model-forward coefficient construction is shared across search
arms and must not be confused with free deployment computation. Monetary cost,
machine power and actual backend build fingerprint beyond reported llama.cpp
remain unknown. Existing phase-1 artifact hashes refer to the ad01b74 publication;
the current README may subsequently change as new findings are published.
