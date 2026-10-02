# Landscape
- Dyna (Sutton 1991) interleaves real updates with updates from a learned model; prioritized sweeping (Moore & Atkeson 1993) directs planning updates by Bellman-error priority. Q-learning (Watkins & Dayan 1992) is the no-model reference. Kaelbling et al. (1996) survey these.
- Dyna-Q+ and the blocking/shortcut mazes are from Sutton & Barto (2018, textbook, not citable via DOI here); results there are single illustrative curves.
- van Hasselt et al. (2019) argue that using an imperfect model to generate fictional transitions from observed states should not beat replay; Pan et al. (2019) study search control in Dyna.
- Deep MBRL deals with model error via short rollouts (MBPO, Janner 2019) or ensembles (PETS, Chua 2018); Moerland et al. (2020) survey. Tabular model error under non-stationarity is the textbook case and is not systematically swept over n.
- Gap: a paired-seed sweep of planning steps over stale (blocking), opportunity (shortcut) and stochastic regimes for four tabular agents.
