\begin{tabular}{llccc}
\toprule
System & Setting & test\_acc & mem\_rate & mem\_gap \\
\midrule
Mixup & $\alpha$=0.2 & 0.709$\pm$0.037 & 0.984$\pm$0.010 & 0.976$\pm$0.015 \\
Mixup & $\alpha$=0.5 & 0.735$\pm$0.022 & 0.958$\pm$0.020 & 0.928$\pm$0.033 \\
Mixup & $\alpha$=1 (main) & 0.762$\pm$0.030 & 0.892$\pm$0.006 & 0.819$\pm$0.020 \\
Mixup & $\alpha$=2 & 0.794$\pm$0.026 & 0.718$\pm$0.013 & 0.486$\pm$0.029 \\
Mixup & $\alpha$=4 & 0.849$\pm$0.038 & 0.426$\pm$0.071 & -0.085$\pm$0.156 \\
\midrule
LS & $\epsilon$=0.05 & 0.662$\pm$0.042 & 1.000$\pm$0.000 & 1.000$\pm$0.000 \\
LS & $\epsilon$=0.1 (main) & 0.668$\pm$0.028 & 0.999$\pm$0.002 & 0.999$\pm$0.002 \\
LS & $\epsilon$=0.2 & 0.676$\pm$0.034 & 0.999$\pm$0.001 & 0.999$\pm$0.002 \\
LS & $\epsilon$=0.4 & 0.682$\pm$0.036 & 1.000$\pm$0.000 & 1.000$\pm$0.000 \\
LS & $\epsilon$=0.6 & 0.693$\pm$0.030 & 1.000$\pm$0.001 & 0.999$\pm$0.002 \\
\midrule
Small-loss & rate=0.1 & 0.733$\pm$0.029 & 0.875$\pm$0.005 & 0.778$\pm$0.009 \\
Small-loss & rate=0.2 & 0.774$\pm$0.023 & 0.685$\pm$0.015 & 0.418$\pm$0.027 \\
Small-loss & rate=0.3 & 0.828$\pm$0.016 & 0.509$\pm$0.015 & 0.082$\pm$0.034 \\
Small-loss & rate=0.4 (main) & 0.896$\pm$0.018 & 0.280$\pm$0.037 & -0.370$\pm$0.084 \\
Small-loss & rate=0.5 & 0.918$\pm$0.016 & 0.162$\pm$0.010 & -0.612$\pm$0.026 \\
Small-loss & rate=0.6 & 0.921$\pm$0.019 & 0.116$\pm$0.021 & -0.702$\pm$0.056 \\
\midrule
Small-loss & no warm-up/ramp, rate=0.4 & 0.924$\pm$0.019 & 0.146$\pm$0.040 & -0.649$\pm$0.091 \\
\bottomrule
\end{tabular}
