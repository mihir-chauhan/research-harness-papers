# Landscape
- EWC (kirkpatrick2017overcoming): quadratic penalty weighted by diagonal Fisher. Related regularisers: SI (zenke2017continual), LwF (li2018learning), and a reparametrisation variant (liu2018rotate).
- Replay / memory: GEM (lopezpaz2017gradient), A-GEM (chaudhry2018efficient), tiny episodic memories (chaudhry2019tiny) show a few examples per class with plain replay is strong; iCaRL (rebuffi2017icarl) for class-incremental with exemplars; DER++ (buzzega2020dark).
- Scenario taxonomy (ven2019three): task-, domain-, class-incremental; EWC-type regularisation fails in class-incremental.
Closest work: ven2019three and chaudhry2019tiny. Gap: a same-budget, two-knob (lambda vs M) comparison at digits scale; the contribution is a replication, not a new method.
