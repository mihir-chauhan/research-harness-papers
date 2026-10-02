# Landscape
- Transformer forecasters for long horizons: Informer (zhou2020informer), Autoformer (wu2021autoformer) claimed large gains on ETT and other suites.
- zeng2022are introduced DLinear (moving-average decomposition + two one-layer linear maps, direct multi-step) and showed it beating those transformers on most benchmarks, attributing earlier gains to direct multi-step decoding rather than temporal attention.
- PatchTST (nie2022time): patching + channel independence; reported to beat linear models. iTransformer (liu2023itransformer) inverts tokens. N-BEATS (oreshkin2019n): MLP basis expansion.
- Benchmarks and protocol: TFB (qiu2024tfb) documents evaluation flaws (drop-last, look-back tuning) and finds that simple and classical methods are competitive on many datasets.
- GRU (cho2014learning) is the standard gated recurrent cell, used here as the recurrent nonlinear baseline.
- Gap: published comparisons use real datasets whose properties are uncontrolled. Few studies vary trend, seasonal complexity, noise and regime switching one at a time under one protocol. This study does so at small CPU scale.
