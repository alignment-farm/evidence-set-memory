# Post-confirmation source and answer-metric diagnosis

The frozen metric is reproducible, but it is not an independent truth oracle.
After the 24-case run completed, the investigator inspected the question, annotated
support text and answer for **all 13 annotated-support-control cases that failed
answer exact match**. This is outcome-selected, unblinded diagnostic reading by
the same gpt-6-astra/high investigator, not independent adjudication or an estimate
of dataset-wide error prevalence. No scores, selection, weights or labels change.
A subsequent check read the remaining eleven control source bundles too, to look
for problems among EM passes; that extension remains post-hoc and unblinded.
All claims below concern the supplied historical text, not current real-world facts.

## Concrete source-link failures

| Raw question ID | Supplied evidence problem | Consequence |
| --- | --- | --- |
| `quadruple_iii__15567_59747_211319_557671` | The chain goes from Sears's sentence in Georgia and that state's Atlanta to a rally in Atlanta, Michigan and Michigan utilities. | Identical place names do not justify the geographic bridge. The gold Presque Isle County is not established by this chain. The reader abstained even with all annotated support. |
| `double__48776_807969` | The award paragraph identifies Mohamed Salah and Liverpool. The other support is a biography of Ahmed Salah Hosny. | A different person's national team cannot establish this link. The reader's Liverpool answer is explicitly supported by the award paragraph but receives zero EM against Egypt national football team. |
| `double__39063_212301` | The first paragraph concerns Robert Peel's new police; the other is titled Sidney Peel and identifies Sidney's father as Arthur Peel. | The annotated father answer crosses distinct people. This does not establish that the reader's alternative answer is correct, but it invalidates treating the annotation as a source-derived certificate. |
| `quadruple_ioh1__316459_41402_145282_13584` | The Nugent paragraph discusses French Revolutionary/Napoleonic wars; the Florida passage attributes the relevant sovereignty transfer to the American Revolutionary War. | The supplied war bridge does not match, independently of the answer-span mismatch about Barcelona/Madrid. |
| `double__512773_346751` | One paragraph locates the school serving Bancroft in Hastings County; the other says a river passes through Renfrew, Hastings and Haliburton. | A river traversing several counties does not explicitly identify the requested shared county boundary or uniquely select Haliburton. External geography was not checked. |

These observations do not allege an error in every occurrence of these entities
or establish how frequent the problem is in MuSiQue. They are enough to reject
“annotated support implies genuinely sufficient evidence” as an assumption for
all cases in this adopted slice.

The follow-up finds that EM passes can also have unsupported bridges:

- `double__825727_584042`: Maycon's paragraph names Goyang Hi FC; the supposed league support discusses another player's FC Seoul career. Matching the gold `K-League` does not validate that cross-team link.
- `double__144763_599630`: Zhu's birthplace is Wenzhou; a separate church is in Yongjia County **near** Wenzhou. Proximity of that church does not establish the athlete's county of birth.
- `double__636597_480615`: sources put Qiantong in Ninghai County of Ningbo, while the composed question asks for a city **inside** the county. The containment direction is reversed in the question.

Other bundles have a coherent visible connection, for example the Mickey Mouse
creation/show pair and the Saint Peter/basilica/Vatican chain. The conclusion is
not that every row is unusable. It is that neither benchmark success nor failure
can uniformly stand in for validated complete behavior in the adopted slice.

## Answer strings and citation requirements also differ from semantic quality

The same inspected control includes these answer/gold pairs:

- `double__159903_154896`: question asks for a year; output `2009`, gold `27 April 2009`.
- `triple_ii__131783_131926_87157`: question asks flow direction; output `southwards`, gold is a longer source span describing the river's origin and direction.
- `double__65202_712629`: output adds `Duke of Edinburgh` to the gold name `Philip Mountbatten`.
- `quadruple_ioh1__719125_132409_223216_35031`: output `third`, gold `third-largest`.
- `triple_ii__92788_648104_13493`: output names the continental treble and enumerates its competitions; gold is just `continental treble`. Its citations also omit the intermediate Villa/Barcelona paragraph, a separate metric failure.

These are concrete reasons why EM can fail without the short semantic answer
being wrong. They are **not** post-hoc aliases added to rescue one policy. F1 is
reported alongside EM, but it too is a token-overlap measure. A representative
wrong answer remains: `double__14095_15463` returns Compaq where the question and
two supports identify Hewlett Packard as the company that merged with Compaq.
Thus not every failure can be dismissed as annotation or formatting.

The Genesis/Pinball Quest control returns improved graphics and sound, while the
gold additionally includes 16-bit architecture. Its citations omit the separate
NES paragraph, although the supplied comparison already describes the 8-bit NES.
This illustrates why insisting on every annotation can penalize a potentially
sufficient alternative explanation; we do not adjudicate that output as a new
complete success here. The final Olympics case hit the response cap and is covered
by the separate public length-stop diagnostic.

## Conversion and implications

The pinned author converter was re-inspected: it copies `composed_question_text`,
answer text, paragraph text and supporting flags rather than validating entity
identity or repairing questions. The pinned author README states that raw and
official datasets differ in format, not qualitative content. That is an author
statement, not a new byte-for-byte check of the official download. Our conversion
uses the same relevant fields; the defective links are visible in the original
raw paragraphs, not generated by the energy or reader.

The raw inputs/labels are recoverable by the manifests and source SHA-256. The
published reader request/response pairs retain the inspected paragraphs and
outputs. Reproduce the affected rows by joining `confirmation-reader/outcomes.json`
on raw ID with `.cache/phase2/partitions/confirmation-{inputs,labels}.json`.

This narrows the phase's scientific claim. A functioning learner has acquired
benchmark support supervision, and optimizer behavior is measurable. The recorded
downstream table is **benchmark answer/citation quality**, not a validated count
of all genuinely correct completed tasks. No ordinary-method disadvantage or EBM
advantage is established by treating bad certificates as truth. A next source-native
continuing-work comparison needs source-link validation and a complete evaluator
that accepts legitimate alternatives before its acquisition/confirmation boundary.
The present confirmation material is now spent for developing such a revision.
