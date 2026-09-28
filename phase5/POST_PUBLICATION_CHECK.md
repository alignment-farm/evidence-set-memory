# Additional publication verification

After building the 52-file phase manifest, reran the frozen confirmation command
to `.cache/phase5-confirmation-publication-replay`. All **504 policy/episode
outcomes** match the published outputs after recursively excluding timing fields.
This is a same-material verification replay, not 504 new task observations.

Additional verification cost: **369 native executions** (336 noncached attempts
plus 33 repairs); seven policies each retain 24 cache hits. This is additional to
the 6,185 native executions and five weight replays in the saved audit, and is not
included in the 4,481 experimental executions. Its raw timing/cost fields remain
in the ignored local replay directory; no extra training or external model call.
The 52-file manifest verified twice and `git diff --check` passed before the
publication commit `93ab8b6`. All 18 boundary tests passed in the preceding audit.

This supplement is subsequent to that publication and deliberately outside its
unchanged manifest; it does not revise any frozen claim, outcome or cost artifact.
