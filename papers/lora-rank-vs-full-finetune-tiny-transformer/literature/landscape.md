# Landscape
- LoRA (Hu et al., 2021) freezes pretrained weights and trains low-rank updates; claims quality comparable to full fine-tuning with far fewer parameters. Adapters (Houlsby 2019), BitFit (2021) and the unified view of He et al. (2021) are alternative parameter-efficient methods.
- Aghajanyan et al. (2020) argue fine-tuning has low intrinsic dimension, motivating low-rank updates.
- Biderman et al. (2024), "LoRA Learns Less and Forgets Less", measure on 7B-scale models that LoRA underperforms full fine-tuning on code and maths but forgets less of the source domain.
- Catastrophic forgetting (Kirkpatrick et al., 2016, EWC) is the classic framing.
Gap: those results are on large models with noisy, hard-to-attribute benchmarks. A synthetic setting with exact-match scoring, known pretraining task and exact trainable-parameter counts lets us test the rank/forgetting claims in a fully controlled but tiny regime. Closest work: Biderman et al. 2024; we do not claim to resolve their large-scale findings.
