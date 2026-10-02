# Design
`method/run.py`: data (sklearn digits /16, stratified 60/20/20 train/val/test per seed), 5-task streams, MLP 64-100-100-10, SGD (no momentum), batch 32, 30 epochs per task, grad-norm clip 5 (all systems).
- Fine-tuning: sequential training.
- EWC: after task k store theta*_k and diagonal Fisher F_k (mean over the task's train set of squared gradients of log p(y~p_theta|x)); loss = CE + (lambda/2) sum_k sum_i F_k,i (theta_i - theta*_k,i)^2.
- Replay (ER): buffer of M slots split equally over tasks seen so far (random exemplars; shares shrink as tasks arrive, so floor(M/t) per task); each step adds CE on a replay batch of 32 to CE on the new batch.
- Joint: after each task t retrain from scratch on the union of tasks 1..t (same epochs, so more steps) - upper bound.
- split_til masks logits to the task's two classes in training and test; perm_dil and split_cil use the full 10-way head.
Metrics from the accuracy matrix A[i][j] (test, after stage i, task j): average_accuracy = mean_j A[T][j]; forgetting = mean_{j<T} (max_i A[i][j] - A[T][j]); backward_transfer = mean_{j<T}(A[T][j]-A[j][j]); last_task_accuracy = A[T][T]; mean_seen_accuracy = mean over stages of mean accuracy on seen tasks. val_* use the validation split.
