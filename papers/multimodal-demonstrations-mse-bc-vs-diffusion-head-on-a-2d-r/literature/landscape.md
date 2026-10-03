# Landscape
- Multimodality in BC: MSE regression averages modes (Florence et al., IBC, 2109.00137; Shafiullah et al., BeT, 2206.11251, which uses k-means bins + offsets); mixtures (MDN-style) used in Lynch et al. play (1903.01973).
- Diffusion Policy (Chi et al., 2303.04137) reports that action diffusion with chunking handles multimodality and beats IBC/BeT; builds on DDPM (2006.11239) and improved schedules (2102.09672).
- Follow-ups: IMLE Policy (2502.12371) and CARP (2412.06782) propose cheaper alternatives; Ta et al. (2207.05824) show EBM training pathologies; Urain et al. survey (2408.04380); Mazza et al. (2605.22493) analyse bottlenecks of generative BC for multimodality.
- Gap: a minimal controlled test where every head shares data/width/epochs, a mixture head with matched capacity, and the one variable that decides if regression fails (start-state ambiguity) is swept.
