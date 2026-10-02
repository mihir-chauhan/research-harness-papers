# Neural quantum states at small scale (author brief)

## Question
For the periodic 1D transverse-field Ising model H=-sum s^z s^z - Gamma sum s^x (N=8,10,12), how do RBM wavefunctions (hidden density alpha=1,2,4) compare with a mean-field product state and a Jastrow ansatz in ground-state energy error, magnetisation error and fidelity across the critical field, with plain SGD and with stochastic reconfiguration (SR)?

## Hypotheses
H1-H5 as registered in `proposal.md` (ansatz ordering, SR vs SGD, monotone in alpha, errors peak at criticality, size dependence).

## Method / baselines
numpy VMC (Metropolis, 256 parallel chains, 300 iterations). Mean-field, Jastrow and RBM all reimplemented; each trained with SGD and SR. Method of record: RBM alpha=2 with SR. Reference: sparse exact diagonalisation. Evaluation by exact enumeration of the trained state.

## Tasks
N=10 with Gamma in {0.25,0.5,0.75,1,1.25,1.5,2}; N=8 and N=12 with Gamma in {0.5,1,1.5}. 5 seeds.

## Metrics
relative energy error, |Mz| error, <sigma^x> error, infidelity (primary: relative energy error).

## Ablations
Start ablation (symmetric vs symmetry-broken initial fields, all systems and tasks); SR diagonal shift sweep; samples-per-step sweep (RBM alpha=2 SR, N=10, Gamma=1).

## Decisions (open choices)
- Real positive amplitudes only (TFIM is stoquastic).
- Learning rate tuned per (ansatz, optimiser): grid {0.003,0.01,0.03,0.1} for SGD, {0.02,0.05,0.1} for SR, lowest mean relative energy error over 3 tuning tasks x 3 tuning seeds (100-102), diverged = infinite (protocol v3; v1 used one task and one seed, v2 three tasks and one seed, both superseded).
- SR shift 1e-2 fixed for main runs.
- Magnetisation reported as <|Mz|> since the finite-size ground state has <Mz>=0.
- Two starts for every system (fix round after the first audit): symmetric (a_i ~ N(0,0.01^2)) and symmetry-broken (a_i = 0.5 + N(0,0.01^2)), same rate and budget; the reported state is the lower-energy start. Reason: from the symmetric start the Jastrow state stays near a symmetric stationary point at small fields and mean-field falls into domain-wall minima, which made both baselines look worse than they are.
- Jastrow stored with one parameter per pair (N + N(N-1)/2 parameters); earlier runs that allocated an N x N block were re-run and superseded.

## Out of scope
Complex amplitudes, larger N, 2D, deep/autoregressive ansaetze, time evolution.
