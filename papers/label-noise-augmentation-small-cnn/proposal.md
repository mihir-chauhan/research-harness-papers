# Proposal
See BRIEF.md for question, hypotheses H1-H5, systems and metrics. Refutation criteria: H1 refuted if CE mem_rate<=0.9 or accuracy drop<=10 points at 40%/60%;
H2 refuted if LS beats CE by >=3 points at 40% with a paired test p<0.05; H3 refuted if mixup does not lower mem_rate or does not improve test_acc over CE; H4 refuted
if another system has higher mean test_acc at 40%/60% or small-loss does not lose at 0% noise; H5 refuted if mis-specified rates retain the gain.
