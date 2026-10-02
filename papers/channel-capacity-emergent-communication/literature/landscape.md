# Landscape

Searches run (see literature/candidates.jsonl): emergent communication capacity/vocabulary/message length;
compositionality and topographic similarity; Gumbel-softmax vs REINFORCE discrete channels; held-out
attribute combinations in referential games.

What exists
- Referential/signalling games with neural agents: Lazaridou et al. 2016 (lazaridou2016multi), Havrylov & Titov 2017
  (havrylov2017emergence, sequences of symbols, Gumbel-softmax and REINFORCE), Kottur et al. 2017 (kottur2017natural:
  language does not emerge compositional by default).
- Channel capacity: Resnick et al. 2019 (resnick2019capacity) show that bandwidth/capacity trade off against
  compositionality; Chaabouni et al. 2020 (chaabouni2020compositionality) show that held-out generalisation requires a
  channel not much larger than needed, and that compositionality is not necessary for generalisation.
- Measures: topographic similarity (brighton2006understanding), non-trivial compositionality (korbak2020measuring), grammar
  analysis (wal2020grammar).
- Pressures/biases: iterated learning (ren2020compositional), noise (kuciski2021catalytic), entropy minimisation
  (kharitonov2019entropy). Toolkit: EGG (kharitonov2019egg). Survey: lazaridou2020emergent.
- Estimators: Gumbel-softmax (jang2016categorical, maddison2016concrete), REINFORCE (williams1992simple).

Gap / what a small study can add
Prior work varies vocabulary or length separately in bigger setups. Here: a small controlled replication on 4x4 attribute-value
objects crossing V and L, with both estimators, two fixed-code reference senders (random code of equal capacity; an
oracle compositional code) that isolate what a *listener* can generalise from, and the over-capacity channel. This is a
reimplementation-scale replication of known qualitative claims, not a new method.
