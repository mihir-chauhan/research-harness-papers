# Landscape

- **FNO** (Li et al., 2020, `li2020fourier`): parametrises the integral kernel in Fourier space; the paper reports Burgers 1D results and resolution-independent evaluation (zero-shot super-resolution). Our setup follows its Burgers data recipe (Gaussian measure, nu=0.01) but with our own solver and 400 training pairs.
- **DeepONet** (Lu et al., 2019, `lu2019deeponet`): branch/trunk architecture motivated by the universal approximation theorem for operators. The trunk accepts arbitrary query points, the branch needs fixed sensor locations.
- **Direct comparison** (Lu et al., 2021, `lu2021comprehensive`): fair comparison of DeepONet and FNO over a range of problems with practical extensions; finds neither dominates universally. Closest prior work.
- **Neural operator framework** (Kovachki et al., 2021, `kovachki2021neural`) and **alias-free analysis** (Bartolucci et al., 2023, `bartolucci2023representation`): discretisation invariance in theory; the latter argues that FNO-type models are not exactly discretisation-invariant once truncation/aliasing matter. **CNO** (Raonic et al., 2023, `raoni2023convolutional`) is a U-Net-style alias-aware alternative (not reimplemented here).
- **Benchmarks**: PDEBench (`takamoto2022pdebench`) provides Burgers 1D data with FNO/U-Net/PINN baselines; PINO (`li2021physics`) adds physics-informed losses (out of scope).
- **PCA-Net** (`bhattacharya2020model`): PCA-based encoder-decoder operator learning, the closest to a plain MLP-on-coefficients baseline.
- **Solver**: ETDRK4 (`kassam2005fourth`); optimiser Adam (`kingma2014adam`).

## Gap
The literature has the ingredients; we offer a tiny, fully-specified, multi-seed CPU replication that (i) gives controls (MLP, CNN) that cannot natively change resolution and states what "zero-shot" means for each, (ii) reports the failure case of each model, and (iii) tests sensitivity to modes and data size. We make no novelty claim for any model.
