# Identical discrete energies can deliver different evidence

28 September 2026. The [predeclared diagnostic](PROTOCOL.md) adds
`lambda * sum(z_i * (1-z_i))` to the frozen energy. This term is zero on every
binary selection, so it changes neither a valid set's energy nor any discrete
ranking or training-pair loss. It does change the gradient followed between
discrete sets. The observed behavior confirms this matters operationally.

On the same 48 previously seen development questions, with all starts, steps,
rounding rules and learned weights fixed:

| Lambda | Rounded sets changed from zero | Global optimum after rounding | Complete support after rounding | Global optimum after swap repair |
|---:|---:|---:|---:|---:|
| -4 | 41/48 | 5/48 | 21/48 | 44/48 |
| -1 | 21/48 | 39/48 | 20/48 | 46/48 |
| -0.25 | 6/48 | 28/48 | 19/48 | 45/48 |
| 0 | 0/48 | 24/48 | 21/48 | 45/48 |
| 0.25 | 6/48 | 22/48 | 22/48 | 44/48 |
| 1 | 14/48 | 21/48 | 21/48 | 45/48 |
| 4 | 19/48 | 17/48 | 22/48 | 45/48 |

There is no different learned ordering in this table. The difference arises
solely in the continuous inference path. Exact and discrete beam search are
unaffected. Swap repair reduces the sensitivity: only zero to three final sets
per lambda differ from the zero-lambda refined output, with 19–21 complete
support sets. Beam reached the global score on all 48 in the phase-2 comparison.

Higher global-score attainment still does not guarantee higher annotated support
completion: lambda -1 reaches far more global optima after rounding than lambda 0,
yet has one fewer complete support set. The sampled lambdas are a diagnostic of
the method, not a search for a new winning deployable policy. None is selected
for confirmation, and no additional primary-model call follows from this table.

The lesson for this implementation is concrete: binary-set supervision does not
identify the energy's behavior at fractional selections. A deployment claim for
continuous minimization must specify that extension, its initialization, projection
and rounding. It cannot follow solely from a learned discrete set ranking or from
renaming that ranking an energy. This is a local methodological finding and an
algebraic identity, not a novelty claim about structured prediction generally.

Binary invariance and the added analytical gradient were checked against autograd.
The lambda-zero outputs reproduce phase 2 exactly. There were 107,520 selection
gradient steps in total, 80 steps × four starts × seven lambdas × 48 questions.
All rounded searches together took about 10.07 seconds; inclusive refined
searches took about 10.15 seconds. Those two totals share work and must not be
added. Representation loading/construction is separately recorded; original
encoder costs remain in phase 2. No new encoder, reader or training calls occurred.

Evidence and exact code/protocol/checkpoint hashes are under
[runs/extension](runs/extension). Reproduce after restoring phase-2 caches with:

```sh
uv run python scripts/phase4_relaxation.py --out .cache/phase4-replay
```

Use a new output directory. This is development material already inspected in
phase 2; the 336 lambda/question combinations are not independent fresh tasks.
