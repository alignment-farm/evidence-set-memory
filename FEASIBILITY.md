# Evidence-set workload reconnaissance — 28 September 2026

## Finding

SERBench supplies an immediately usable, bounded set-recovery diagnostic with real code excerpts and non-additive certificate completion. MuSiQue supplies an obtainable complete QA task with answer and support scoring. Neither inspected release supplies the proposed cross-session accumulated experience/correction sequence. Combining the datasets does not repair that missing scientific component. These are asset findings, not experimental treatment evidence or evidence for an energy-based model advantage.

Investigator: root dispatched `gpt-6-astra`, reasoning `medium`; this is dispatcher-reported provenance. The session identifies itself as an OpenAI GPT-6 agent; an independent backend build/model fingerprint is unavailable. No participant, teacher, training or model inference was run, no external messages/submissions were sent. The 22 September investigator policy remains gpt-6-astra for researchers/reviewers; participant models remain study choices. Read root AGENTS.md and notes/ANCILLARY_STUDY.md. Original reconnaissance writes were confined to Construct-2’s assigned scratch directory. Root then authorized this packaging into the study’s FEASIBILITY.md, scripts, sources/reconnaissance and ignored .cache/reconnaissance. No arXiv API/OAI calls.

## SERBench: checked assets and limits

Pinned repository: https://github.com/LordTARN1SHED/SERBench/commit/8c27a88e48dcbcd4a5745573c95937a4740f4406 . Source association supplied by root: arXiv:2609.20050v1. Local partial snapshot in `.cache/reconnaissance/SERBench/`; source files fetched with immutable raw URLs at that commit. The ignored cache preserves original API responses; only repository URLs, pinned commits and content hashes are included in the tracked fetch manifest. Unrelated API author/account metadata is not copied into tracked records. Manifest release is `serbench-public-v1-v5.6`. This is the latest accessible public asset revision on inspection, not a verified reconstruction of the paper v1 artifact state. Missing fields/assets describe the released supplied-candidate track and are not asserted to contradict the paper’s other tracks.

Downloaded and parsed all Cal500 inference records and public labels, all Test500 inference records, three example records/labels, SDK/scoring code, data card, evaluation/reproduction instructions, rights files and source inventory. All six downloaded manifest entries match both compressed and uncompressed SHA-256. Cal inference compressed 29,263,904 bytes; Test inference 26,010,955; calibration labels 121,455. No private Test500 labels are in the repository or were sought.

Observed Cal500 facts:

- 500 states, 241 issue instances, 174 repositories; candidate pools contain 40–120 excerpts. 47 pools marked truncated.
- 242/117/100/37/4 states have respectively 1/2/3/4/5 certificate groups. Group count overstates item count when one excerpt satisfies several groups.
- Exact enumeration over each certificate's acceptable-ID universe gives minimum complete set sizes: 1 item: 256 states; 2: 135; 3: 86; 4: 19; 5: 3; 14: 1. Thus 244 states require multiple IDs under the public certificate, and one cannot complete at the standard budgets 5/8. This is annotated interaction, not a demonstration of downstream causal necessity.
- All 500 `current_diff`, `latest_test_output`, and `observed_evidence_ids` are empty. Prefixes record plan/search/read and 134 edit-intent events; an inspected edit event only names a target path and intended patch. All event timestamps empty, exactly one run ID per issue. Several captured states per issue therefore do not establish repeated sessions, executed corrections, or successful task outcomes.
- Test500 has a different schema: no trajectory prefix, base commit, diff or test-output fields. 298 states have nonempty observed-ID lists, of which 186 overlap their candidate pool. Test pools contain 20–120 excerpts; 16 marked truncated. Do not extrapolate Cal500's absent observed-ID signal to Test500 or treat the two splits as matching state-history distributions.

Concrete interaction examples (public calibration annotations, for inspection only):

- `vega__altair-3853-...-s003`: a bug concerns lost `empty` behavior for parameter composition. Five groups separately cover AND, OR, invert, serialization, and schema behavior; the final group has six substitute excerpts. This mixes complementarity with redundancy. It is richer than choosing individually relevant paragraphs, but no executable issue-resolution result is provided.
- `casbin__pycasbin-392-...-s005`: five method-existence/absence groups collapse to two excerpts (two groups in one, three in another). Counting roles or choosing one item per group would be misleading.
- `celery__django-celery-beat-900-...-s005--g500x-012a4477`: the first calibration record is a singleton anchor for locating the SQL Server-incompatible regex query. It should not stand in for interacting evidence.

`load_dataset` returns inference records without certificates; `load_labels` is separate. Candidate fields are excerpt, hash, ID, line limits, observed flag, source path/type. Required groups, alternatives, necessity weights, annotation rationales and roles belong only in development supervision or evaluator data; no selector may consume test-side certificates or their derived labels. Data card says construction-source provenance/role hints were removed from inference export, while candidate membership/order/text remain fixed. Selection from this pool does not establish gold-blind full-repository retrieval.

The reference scorer performs AND over required groups, thresholded acceptable alternatives within groups, OR with enumerated complete alternative sets; it evaluates original top-k positions and does not mask observed IDs. Empty-vs-oracle assertions and SDK label separation passed. Public Cal labels are machine-calibrated/cross-family-repaired, not independently human-adjudicated test gold. The data card explicitly says the core release does not score code execution or issue resolution; complete repository-source/downstream localization/external-memory experiment assets are outside this interface. Test500 local scoring is unavailable without author certificates. The documented public submission queue entails publishing a prediction artifact and evaluation request; no submission was made and service operation was not independently tested.

Rights: original interface/evaluator code MIT; original annotations/state-card material CC BY 4.0; upstream source/issue excerpts retain upstream rights. The source inventory and base-commit metadata support later per-source inspection; no blanket redistribution grant for excerpts.

## MuSiQue: independent complementary check

Pinned author repository: https://github.com/StonyBrookNLP/musique/commit/922ac98f19a201998dbdae6d7f2887a5258dbdeb . Local partial snapshot `.cache/reconnaissance/MuSiQue/` includes README, evaluator and its metrics, raw-to-official converter, answer-alias map, license, and download maps. Repository/data license identifies CC BY 4.0; README cautions that seed single-hop questions in dev/test can occur in seed training datasets and publishes an exclusion list.

The official bundled download uses Google Drive ID `1tGdADlNjWFaHLeZZGShh2IRcpO6Lv24h`. To avoid downloading the bundle, inspected the separately author-linked raw **MuSiQue-Ans dev** asset in `.all_data_information.json`: https://drive.google.com/uc?export=download&id=1TRXU68wveSehVbQrRRtWsUsFkKUF43QS . Response advertises 42,457,393 bytes; downloaded only its first three complete JSONL records by streaming and closing the response. Stored `.cache/reconnaissance/MuSiQue/raw-dev-first3.jsonl` and historical response headers (cache only). The initial curl check intentionally capped size at 2 MB and stopped with error 63; this was a size cap, not access denial. Google Drive artifact lacks a pinned version/author checksum here; record a complete-file checksum if later acquired.

All three sampled records have 20 contexts, bridge decompositions, answer strings, supporting-context flags, answerability, composed questions and source IDs. Example: the UHF question asks for the founder of its distributor. One support identifies Orion Pictures as the film's supporting/distribution company; another identifies Mike Medavoy as Orion co-founder. The Green question links the album to Steve Hillage and his partner Miquette Giraudy. Third example links Ciudad Deportiva/Nuevo Laredo to Tamaulipas; its first supplied support establishes the place mostly via title/location rather than explicit ownership. Samples expose annotation/wording limitations and should be audited before strong necessity claims. A pretrained reader might answer without both supports; use removal controls rather than assuming logical composition guarantees operational dependence.

The official converter produces `id`, `question`, paragraphs with stable indices, `question_decomposition`, `answer`, aliases and answerability. Its `hide_labels` mode removes answers, aliases, decomposition, answerability and paragraph support flags. Preserve that boundary: deployable input is the composed question and paragraph titles/text/IDs, never raw decomposition answers or support annotations.

The public evaluator scores answer EM/F1 and support F1; MuSiQue-Full additionally supports grouped sufficiency metrics and requires paired answerable/unanswerable records. Only Ans raw examples were acquired, so Full pairs were not verified. Evaluator metric oracle self-checks passed on the three samples; this is plumbing, not model performance. No full converter run or official-format/full-bundle checksum comparison was performed. Code inspection shows a workable conversion and scoring path. No session chronology, tool outcomes, user corrections, or replayable agent-memory sequence exists in the inspected QA schema. Shuffling questions would not create one.

## Recommended first bounded lab step

Make the scientific split explicit: (A) controlled evidence-set utility; (B) accumulated-experience transfer. Start A with a small author-source MuSiQue development slice converted using the provided converter, clean inference/evaluator separation, fixed reader, and all-evidence / gold-support / support-removed / random / competent conventional selector controls. Confirm that at least some cases actually change downstream answer quality when complementary evidence is removed. Reserve new questions plus underlying single-hop components for confirmation after diagnostic development. These controls diagnose what the task measures; they are not an admission gate requiring a selector or neural treatment win. Workload construction and small EBM acquisition may proceed together within the remit, preserving failed attempts and using the controls to distinguish candidate reachability, selection, reader limitations and acquisition failure. SERBench's 243 multi-evidence states completable within k=8 provide a complementary code-selection diagnostic, split by repository/issue to avoid correlated-state leakage, with calibration annotation limits reported.

Before claiming B, acquire or construct genuine chronological sessions with observable correction/outcome events, later tasks that can benefit from retained evidence, and evaluable completed outcomes. Define the experience pool and timestamp access at each step. Neither current asset warrants calling generic joint retrieval a new memory mechanism. This is a workload-design gap, not evidence against learning or energy-based selection.

A quick combined web search did not locate author ParaSet/SetCE code for arXiv:2607.05712v1; no repository availability conclusion follows. Root owns its paper/metadata investigation.

## Reproduction and stopping point

Run from the study root:

```sh
uv run --no-project python scripts/fetch_assets.py --verify-only
uv run --no-project python scripts/check_assets.py
```

Both commands emit a single valid JSON document. The first verifies cached data without network access; the second checks hashes, enumerates public Cal500 minimum sets, checks inference/label separation, reads Test500 inference only, and exercises oracle/empty scorer plumbing plus MuSiQue answer/support metrics. Saved results are in `sources/reconnaissance/check-results.json` and `cache-verification.json`. The original two concatenated JSON outputs remain transparently preserved as `original-check-results.txt`, not advertised as valid JSON.

On a fresh checkout without cached assets, run:

```sh
uv run --no-project python scripts/fetch_assets.py
uv run --no-project python scripts/check_assets.py
```

The fetch script reads `sources/reconnaissance/fetch-manifest.json`, requests immutable commit-pinned raw GitHub URLs, and validates expected sizes/SHA-256 before writing into `.cache/reconnaissance`. For the author-linked MuSiQue Google Drive file, it streams exactly the first three complete JSONL lines, closes the response, and requires the recorded 47,500-byte sample hash. The Drive source is not version-pinned: changed bytes cause a hard failure rather than silently replacing evidence. This reconstructs the inspected sample, not the full dev file. Historical HTTP headers are capture-only and not required or re-fetched. Existing hash mismatches are preserved for inspection. Total reconstructible payload is 61,376,036 bytes, excluding network headers/retries. No archive extraction or upstream download shell script is executed. No external packages beyond the existing Python runtime/uv are required.

The tracked `sources/reconnaissance/downloaded-file-hashes.json` records all 57 original snapshot files including the historical header capture; all 57 copied files were hash-verified. The reproducible fetch route covers 56 files. `serbench-hash-checks.json` separately preserves original validation of all six released SERBench manifest entries against compressed/uncompressed hashes. Small descriptive audits are `serbench-summary.json`, `serbench-interaction-audit.json`, and `serbench-test-summary.json`; they reflect the inspection scope described above. `sources/reconnaissance/README.md` maps these records.

Original source-payload bytes retained total 61,381,709, excluding small API responses, scripts and reports. This remains below the 100 MB download ceiling; actual network transfer including HTTP overhead, early closed streams and failed requests was not instrumented. Copied caches consume additional local disk, not new network downloads. No model endpoints, training, inference, external submissions or cloud-spend actions were used. Investigator/tool monetary cost and exact backend build are unavailable; the cached-data packaging verification downloaded zero bytes. These are asset and scorer checks, not quality measurements from a learned treatment. Stopped after resolving obtainable-vs-missing workload distinctions and handing off the independent study’s subsequent workload/acquisition development.
