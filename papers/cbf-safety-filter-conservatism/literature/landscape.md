# Landscape

**Foundations.** Control barrier function (CBF) quadratic programs filter a nominal controller by a minimum-norm correction subject to a barrier condition (Ames et al., 2017; Ames et al., 2019). For relative-degree-two constraints such as position limits of a double integrator, exponential/high-order CBFs are used (Xiao and Belta, 2019).

**Discretisation.** Discrete-time CBF conditions have been developed mostly inside MPC (Zeng et al., 2021) and extended to high-order and adaptive cases (Xiong et al., 2023). Sampled-data implementations of continuous-time CBFs, and safety synthesis for sampled-data systems, are studied in Niu et al. (2021). A predictive safety filter is an alternative that certifies over a horizon (Wabersich and Zeilinger, 2021). Candidate records from the library search also include Breeden et al. (sampled-data CBFs, arXiv 2103.03677) and Breeden and Panagou (arXiv 2203.11470); these could not be added through `rh lit cite` (arXiv API rate-limited) and are therefore not cited.

**Obstacle-avoidance comparisons.** Singletary et al. (2021) compare CBFs with artificial potential fields for obstacle avoidance, a heuristic-vs-CBF comparison in the same spirit as ours.

**Gap.** The literature gives sufficient conditions; a compact empirical measurement of how the gain alpha and the period dt move violation rate, time to goal and clearance for a CT-CBF at discrete steps, a DT-CBF condition and a distance-threshold braking heuristic, on two simple plants with a single-constraint closed-form filter, is what this study adds. It is a small empirical study, not a new method.
