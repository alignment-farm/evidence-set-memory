# Exposure audit and qualification of “fresh”

Published during the fixed-reader run, without changing the frozen cohort or
methods. See [machine-readable audit](runs/exposure-audit.json).

The partitioner separated underlying single-hop component IDs across acquisition,
development and confirmation, but did **not** exclude the three questions already
inspected during initial reconnaissance. One of them,
`double__701895_752697`, occurs in the 64-row confirmation cohort. Auditing all
single-hop IDs from those three questions finds no further component-related
confirmation questions. The original “fresh” wording was too strong for this row.
The original freeze is retained, not retrospectively rewritten.

Keep the prespecified 64 cases and separately exclude every question sharing a
previously inspected component. On the resulting 63 cases, exact selection retains
all annotated support on 26, ordinary hybrid on 15, and learned unary on 14.
Exact versus ordinary has 15 wins, 4 losses, 44 ties; versus unary has 18 wins,
6 losses, 39 ties. This sensitivity does not repair the original partition design
or establish unseen pretraining. No selector or reader setting changes follow it.

There are 55 component-connected clusters among the 64 questions, 54 among the
63. Descriptive paired cluster-resampling intervals and the exact resampling seed
are in the audit; no population-level, multiplicity-adjusted inference is made.

Exact title-plus-body hashes overlap even where component IDs do not. Among
eligible 20-candidate rows, training/development share 160 unique paragraphs,
training/confirmation share 128, and development/confirmation share 35. These
counts include distractors and do not imply shared answer annotations, but they
rule out a claim of fully disjoint source prose. Input files omit support flags,
decompositions and answers; labels remain separately supplied training/evaluation
data. The imported encoder and reader may also have encountered benchmark seed
material during pretraining; their provenance cannot exclude that.

The completed reader audit confirms that the previously inspected row does not
enter the prespecified first-24 reader subset. No-context and omitted-support controls
are diagnostics, not certificates that a particular answer required its sources.
