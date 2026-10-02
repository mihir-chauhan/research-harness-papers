# Seed corpus of the research library

AI-generated research papers, one directory per paper, each a complete study: brief, proposal, literature notes, code, run registry (`results/runs.jsonl`), tables, figures, the paper in IEEE conference format (`paper/main.pdf`), the reference check (`paper/citations.json`) and the independent audit (`reviews/audit.json`).

These papers were written end to end by an AI research agent running the [research-harness](https://github.com/mihir-chauhan/research-harness) pipeline. The topics were chosen to cover many fields and no person reviewed the papers. They are small CPU-scale studies, they are not peer reviewed, and they should be read as first looks, not as established results. Absolute paths of the machine that ran the studies were replaced by relative ones in logs and run records; nothing else was edited.

What was enforced for every paper here:

- every number in the paper comes from a run recorded in `results/runs.jsonl`;
- every cited reference resolves on arXiv or Crossref with a matching title;
- a second AI agent that did not write the paper re-ran two experiments, compared the text against the tables, read the citations against the cited papers, and its findings were fixed or the paper was dropped.

Code: MIT. Text and figures: CC BY 4.0.

| Field | Paper | Directory |
|---|---|---|
| biology | How Much Epistasis Can Simple Sequence-to-Fitness Models Absorb? A Small Study on Simulated NK Landscapes | [`papers/epistasis-fitness-models-nk`](papers/epistasis-fitness-models-nk) |
| computer-vision | Label noise robustness of a small CNN on 8x8 digits: cross-entropy, label smoothing, mixup and small-loss selection | [`papers/label-noise-augmentation-small-cnn`](papers/label-noise-augmentation-small-cnn) |
| computer-vision | Does Self-Supervised Pretraining Help with Few Labels at Toy Scale? A Multi-Seed Study on 8$\times$8 Digits | [`papers/self-supervised-few-labels-digits`](papers/self-supervised-few-labels-digits) |
| control-systems | Class-K Gain and Sampling Period in One-Constraint CBF Safety Filters: A Small Empirical Comparison on a Double Integrator and a Unicycle | [`papers/cbf-safety-filter-conservatism`](papers/cbf-safety-filter-conservatism) |
| control-systems | Energy-Deviation Running Costs for iLQR Model-Predictive Swing-Up: A Small Controlled Comparison on Pendulum and Cart-Pole | [`papers/energy-cost-trajectory-optimisation`](papers/energy-cost-trajectory-optimisation) |
| control-systems | Sparse Regression, Neural ODEs and Linear Least Squares for Identification Under Measurement Noise: Prediction Error and Closed-Loop LQR/MPC Cost | [`papers/sindy-vs-neural-ode-sysid-noise`](papers/sindy-vs-neural-ode-sysid-noise) |
| generative-models | What Does Classifier-Free Guidance Trade Away? A Controlled 2D Mixture Study Against Low-Temperature Sampling | [`papers/classifier-free-guidance-2d`](papers/classifier-free-guidance-2d) |
| generative-models | Flow Matching versus Denoising Diffusion on 2D Toy Distributions: Few-Step Sample Quality and What One Reflow Round Adds | [`papers/flow-matching-vs-diffusion-2d`](papers/flow-matching-vs-diffusion-2d) |
| ml-theory-optimization | Does In-Distribution Temperature Scaling Stay Calibrated Under Shift? A Small Study on Digits | [`papers/calibration-under-shift-digits`](papers/calibration-under-shift-digits) |
| ml-theory-optimization | Where the Peak Sits and Whether Ridge Removes It: A Small Study of Double Descent in Random-ReLU-Features Regression | [`papers/double-descent-random-features`](papers/double-descent-random-features) |
| ml-theory-optimization | Replay Memory versus EWC Strength on Permuted and Split Digits: A Small Controlled CPU Study | [`papers/ewc-vs-replay-permuted-digits`](papers/ewc-vs-replay-permuted-digits) |
| ml-theory-optimization | Does SAM Help a Small MLP Under Label Noise? A Controlled CPU Study Against SGD and Weight Decay | [`papers/sam-vs-sgd-label-noise-mlp`](papers/sam-vs-sgd-label-noise-mlp) |
| multi-agent | Channel Capacity in a Lewis Reconstruction Game: Vocabulary, Message Length, Held-Out Accuracy and Topographic Similarity (Small CPU Study) | [`papers/channel-capacity-emergent-communication`](papers/channel-capacity-emergent-communication) |
| multi-agent | Self-Play, Other-Play and Population Training for Zero-Shot Coordination in Small Symmetric Games: An Exactly Evaluated CPU Study | [`papers/other-play-zero-shot-coordination`](papers/other-play-zero-shot-coordination) |
| nlp-llm | Low-Rank Adaptation at Tiny Scale: LoRA Rank, Full Fine-Tuning and Forgetting in a Character-Level Transformer on Synthetic Sequence Tasks | [`papers/lora-rank-vs-full-finetune-tiny-transformer`](papers/lora-rank-vs-full-finetune-tiny-transformer) |
| nlp-llm | Does an Operand-Size Curriculum Speed Up Modular-Addition Grokking? A Small CPU Study of Ordering, Weight Decay and Training Fraction | [`papers/tiny-transformer-modular-arithmetic-curriculum`](papers/tiny-transformer-modular-arithmetic-curriculum) |
| reinforcement-learning | Count Bonuses versus a Random-Network-Distillation Bonus in Sparse-Reward Gridworlds: A Small Reimplementation Study with a Noisy-TV Test | [`papers/count-bonus-vs-rnd-sparse-gridworld`](papers/count-bonus-vs-rnd-sparse-gridworld) |
| reinforcement-learning | How Many Planning Steps? Dyna-Q, Dyna-Q+ and Prioritized Sweeping Under Stale and Stochastic Tabular Models | [`papers/dyna-planning-under-model-error`](papers/dyna-planning-under-model-error) |
| robotics | How Wide Should Domain Randomisation Be? A Small-Scale CartPole Study of Range Width and a Success-Gated Curriculum | [`papers/domain-randomisation-range-robustness`](papers/domain-randomisation-range-robustness) |
| robotics | Templated Language versus Learned Vectors for Multi-Robot Rendezvous: A Small CPU Study of Success, Sample Efficiency and Cross-Play | [`papers/language-vs-vector-multi-robot-comm`](papers/language-vs-vector-multi-robot-comm) |
| scientific-ml | FNO, DeepONet, MLP and CNN on 1D Burgers at Small Scale: Accuracy and Zero-Shot Finer-Grid Evaluation | [`papers/fno-vs-deeponet-burgers-1d`](papers/fno-vs-deeponet-burgers-1d) |
