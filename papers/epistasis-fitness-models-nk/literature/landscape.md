# Landscape

**NK landscapes.** Kauffman and Weinberger's NK model [kauffman1989nk] assigns each of N sites a random contribution
that depends on the residue at that site and at K other sites; K tunes ruggedness from additive (K=0) to uncorrelated.
Its properties have been studied analytically and by simulation, e.g. adaptive walks under different interaction
schemes [nowak2015analysis] and the large-N, K/N-fixed limit with spin-glass tools [chen2025fitness].
**Experimental landscapes and epistasis.** Combinatorial DMS data such as GB1 [wu2016adaptation] and GFP
[sarkisyan2016local] show that epistasis is widespread but that much variance is captured by additive or
monotonic-nonlinear (global epistasis) terms [diazcolunga2022global].
**Supervised fitness prediction.** Linear regression on one-hot site features combined with an evolutionary density feature is reported to be competitive when labels are scarce [hsu2022learning] (we use the plain one-hot ridge part as the additive baseline); benchmarks such as
FLIP [dallago2021flip] and ProteinGym [notin2023proteingym] evaluate supervised and zero-shot predictors; low-N
engineering with learned representations is studied in [biswas2020low]. Greedy/adaptive sequence design on simulated
landscapes is benchmarked in FLEXS/AdaLead [sinai2020adalead].

**Gap.** On real data the amount and order of epistasis is unknown, so one cannot say how much of a model's failure is due to epistasis.
NK landscapes give a knob (K) with known interaction order. A controlled grid over (sequence length, alphabet, K, training size) for
four simple model classes, with a model-guided greedy design step as second endpoint, is a small, cheap complement that we did not find
in the retrieved literature (our search was shallow: 4-6 queries, with Semantic Scholar/OpenAlex rate-limited). We make no novelty claim beyond this.
