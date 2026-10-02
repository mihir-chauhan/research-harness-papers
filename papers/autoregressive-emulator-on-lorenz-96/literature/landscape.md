# Landscape

- ML weather models (GraphCast, FourCastNet, NeuralGCM, Keisler's GNN) are autoregressive one-step emulators; GraphCast and FourCastNet add multi-step (rollout) fine-tuning, NeuralGCM trains through many steps. Their ablations of rollout length are done at full scale and bundled with other changes.
- Rollout/stability tricks on PDEs: pushforward trick and noise (Brandstetter et al.), Stachenfeld et al. (noise, multi-step), PDE-Refiner (refinement to preserve high-frequency modes), Thermalizer (stabilising emulators of chaos by diffusion-based correction).
- Lorenz-96 as a testbed: Chattopadhyay et al. (reservoir/ANN/LSTM forecasting of two-scale L96), Gagne et al. (GAN stochastic parameterisation of the fast variables).
- Benchmarks and protocols: WeatherBench / WeatherBench 2 (RMSE and ACC against persistence and climatology per lead time).
- Gap: a controlled, multi-seed sweep of the training rollout length for a small CNN on the slow L96 variables with the fast variables hidden, reporting skill and long-run climate statistics jointly. We expect a mixed outcome and say so.
