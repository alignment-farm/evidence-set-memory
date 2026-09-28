# Phase 4: discrete-equivalent continuous energies

Predeclared 28 September 2026, while phase-2 fresh QA runs. Use the frozen semantic
scorer and the 48 already-seen development questions only. No new training or
fresh quality claim. Preserve phase-2 code and results.

For relaxed selection z in [0,1]^N with sum(z)=4, define
E_lambda(z)=E_0(z)+lambda*sum_i z_i*(1-z_i).
For every binary set, the added term is exactly zero. Thus all discrete scores,
rankings, training-pair losses and exhaustive-search optima are unchanged. This
is an algebraic identity, not a new literature/novelty claim. The continuous
gradient nevertheless changes by lambda*(1-2*z). The experiment asks whether
that unconstrained extension changes the actual delivered evidence.

Use lambda = -4, -1, -.25, 0, .25, 1, 4; exactly the same four initializations,
80 projected-gradient steps, step size .3 and top-four rounding as phase 2.
Report both rounded outputs and the same public one-swap refinement. Choose the
best rounded candidate using the common discrete score, not a label. Do not tune
lambda from support outcomes or add a winning lambda to confirmation.

Compare global discrete-score attainment, selected-set changes relative to lambda=0,
support completeness, final fractionality and native cost. Test binary invariance
and analytical gradient against autograd. This diagnoses identification of the
continuous inference procedure from binary-only training; it does not establish
a new deployable selector or cross-session experience.
