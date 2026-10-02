# Lorenz-96 as a testbed for learned subgrid parametrisation (brief)

Seed: Lorenz-96 as a testbed for learned subgrid parametrisation: in the two-scale Lorenz-96 system, replace the fast variables with (a) a polynomial closure fitted by regression, (b) a small MLP, (c) a stochastic AR(1) closure, and compare short-term forecast skill, long-rollout stability and the climate (mean, variance, spectrum) of the slow variables against the full two-scale truth.

Precise question, hypotheses H1-H5, method, baselines, metrics and ablations: see proposal.md (authoritative; copied here by reference). Quick study, CPU, 5 seeds main / 3 seeds ablations.

Decisions taken where the seed was open (also in `rh decide`):
- Truth: K=8, J=32, h=1, b=10, F=20, c in {10, 4}; closure is a function of the local slow variable X_k only (shared across sectors); AR(1) = polynomial + red noise fitted on its residuals.
- "Method" label = the AR(1) stochastic closure; polynomial, MLP and no-closure are the comparison systems.
- Polynomial degree 4 and MLP size 32x2 fixed a priori; no tuning on test data.
- Reference climate = one fixed long truth run (4000 t.u.); a second independent truth run gives the noise floor.
Out of scope: online/coupled training, generative closures, data assimilation.
