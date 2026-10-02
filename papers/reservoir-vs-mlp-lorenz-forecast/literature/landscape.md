# Landscape

Searches (library, arXiv, Semantic Scholar, OpenAlex; candidates in `literature/candidates.jsonl`; arXiv/Semantic Scholar rate-limited some queries): reservoir attractor replication and Lyapunov exponents; LSTM forecasting of high-dimensional chaos; next-generation reservoir computing; reservoir hyperparameter sensitivity; chaos forecasting benchmarks.

What exists
- Pathak et al. (pathak2017using): ESN trained on Lorenz/Kuramoto-Sivashinsky data reproduces the attractor and its Lyapunov exponents; the standard ESN setup we reimplement.
- Vlachas et al. (vlachas2018data, vlachas2020backpropagation): LSTM/GRU forecasters of high-dimensional chaotic systems and a comparison of backpropagation-trained RNNs with reservoir computing.
- Gauthier et al. (gauthier2021next): next-generation RC (nonlinear VAR) needs far less training data; we do not run it (out of scope) but it motivates the data-efficiency question.
- Haluszczynski & Rath (haluszczynski2019good): statistical analysis over reservoir parametrisations, short-term versus climate quality on Lorenz and Rossler.
- Racca & Magri (racca2021robust): validation-based hyperparameter optimisation for ESNs on chaotic dynamics.
- Platt et al. (platt2021forecasting), Hart et al. (hart2023attractor): generalized synchronisation and conditional Lyapunov exponents as explanations of when reservoirs forecast / reconstruct attractors faithfully.
- Griffith et al. (griffith2019forecasting): very low connectivity reservoirs; Antonik et al. (antonik2018using): reservoir learning of chaotic attractors.
- Gilpin (gilpin2021chaos, gilpin2023model): dysts benchmark and a large comparison of forecasters on it.

Gap. Existing comparisons either study the reservoir alone or use different tuning and metrics across model families. A small, fully reproducible head-to-head with identical data, validation-tuning budget, VPT definition and climate metric, plus reservoir sensitivity and data-scaling for the three families on the same two systems, is cheap to run and checks how robust the ESN advantage is at CPU scale. We make no novelty claim beyond this controlled replication.
