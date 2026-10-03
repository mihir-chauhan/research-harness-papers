# Protocol
Tasks: transductive (held-out 10% units of graph 1, message graph = its train+val units) and inductive (fresh graph 2 with new entities, same split proportions; message graph = its train+val units, test = its held-out 10%). Models are trained on graph 1 train+val only.
Seeds 0-4: each seed generates its own graph pair and splits. Metric: filtered MRR (head and tail queries, ties split evenly), Hits@1, Hits@10, per-relation MRR.
Tuning: validation split of graphs from seeds 100,101 (never the test split): TransE three rounds (margin, norm, dim, epochs), Path-MP epochs x lr. Hardware: shared CPU, 2 threads. Runs: experiments/run_main.sh 1 and 2.
Groups: main, abl_nodrop, sweep_layers, sweep_density, tune_*.
