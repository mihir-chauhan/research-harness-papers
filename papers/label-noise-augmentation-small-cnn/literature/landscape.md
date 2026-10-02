# Landscape
Zhang et al. (2016) showed deep nets fit random labels; Arpit et al. (2017) showed they learn clean patterns before memorising noisy ones, which motivates
small-loss selection (MentorNet, Co-teaching, DivideMix) and early-learning regularisation (ELR). Mixup (Zhang et al. 2017) was reported to resist memorisation of corrupted labels.
Label smoothing (Mueller 2019) is argued to help (Lukasik 2020 relates it to loss correction) but Wei et al. (2021) find the advantage vanishes at high noise.
Patel & Sastry (2021) examine memorisation vs loss function. Gap: most evidence is on CIFAR with large nets and tuned recipes; here we do a controlled, equal-budget
comparison of four simple methods on a tiny dataset with a direct memorisation measurement on the corrupted subset, with 5 seeds and paired tests.
