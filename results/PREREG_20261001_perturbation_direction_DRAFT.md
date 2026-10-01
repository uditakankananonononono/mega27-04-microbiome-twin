# Prospective perturbation-direction protocol draft
Status: DRAFT, not frozen for scoring; exact source identities, timepoints and exposure verdict unresolved.

Task: from a subject's pre-treatment abundance and known antibiotic/treatment labels, predict the sign of species-level relative-abundance change to the first publication-defined during-treatment or earliest post-treatment sample. Recovery status, future samples and publication-selected recovery-associated species cannot enter predictors. Relative change is compositional, not absolute microbial growth or causal antibiotic effect.

Candidate: processed author-deposited Singapore PRJEB41866, subject/time/arm labels pending original-method verification. NUH PRJEB41865 is a separate candidate, not an independent validation claim yet. Mouse SRP142225 would require cage-level splits and a distinct species/addition intervention estimand. No pooling these tasks into one leaderboard.

After metadata verification and before outcome reads, freeze exact window, eligible subjects, missingness and repeated-course rules, count/relative unit, taxonomic version, subject-group folds and primary threshold. Proposed development test: leave-one-subject-out prior-direction baseline versus an eligible interaction forecast, identical inputs/hyperparameter budget. Primary metric: subject-macro direction accuracy among taxa exceeding a training-defined absolute relative-change threshold; report coverage, abstentions and uncertainty grouped by subject. Zero predicted change abstains. Same-task strongest eligible published comparator must be identified before a top-tool claim. A one-cohort test cannot establish unseen-study transfer.

Do not adapt threshold/model to viewed final outcomes. No scoring until parent returns exposure clearance and the unresolved metadata fields can be named concretely. If candidate lacks these labels, reject this task and report a usable alternative rather than infer treatment timing.
