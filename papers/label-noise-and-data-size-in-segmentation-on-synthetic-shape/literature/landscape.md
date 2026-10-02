# Landscape

- U-Net (Ronneberger 2015) is the standard small-data segmentation architecture; V-Net/Dice losses (Milletari 2016) are the usual alternative loss.
- Deep nets fit random labels (Zhang 2016) but learn clean patterns first (Arpit 2017); Rolnick 2017 shows classification is robust to massive *uniform* label noise given enough data. Hestness 2017 documents data-size scaling.
- Noise-robust losses: GCE (Zhang & Sabuncu 2018), SCE (Wang 2019); sample selection: Co-teaching (Han 2018); regularisation: ELR (Liu 2020). Survey: Song 2020.
- Segmentation-specific: Karimi 2019 (medical image label noise: robust losses, training-size interplay).
- Gap: a controlled, exact-ground-truth study varying data size and noise *type* (boundary vs object-level) for dense prediction on CPU. Library/search hits for the exact question were weak (semantic-scholar/openalex rate-limited).
