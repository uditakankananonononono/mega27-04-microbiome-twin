# Candidate finding: on human-associated microbiomes, a presence-only null matches cNODE
Protocol: leave-one-out (as in Michel-Mata et al. 2022), median Bray-Curtis, 5000-bootstrap CI of the null's median.
Null = mean training composition restricted to taxa present, renormalised (no interactions, no parameters beyond means).
| dataset | n | null LOO median [95% CI] | published cNODE |
|---|---|---|---|
| Ocean | 269 | 0.094 [0.089, 0.101] | 0.060 |
| Drosophila gut | 24 | 0.170 [0.100, 0.193] | 0.066 |
| Soil in vitro | 48 | 0.198 [0.085, 0.268] | 0.079 |
| Soil in vivo | 678 | 0.124 [0.119, 0.127] | 0.107 |
| Human oral | 143 | 0.204 [0.188, 0.222] | 0.211 |
| Human gut | 106 | 0.259 [0.236, 0.271] | 0.242 |
Read: cNODE clearly beats the null on ocean, soil and Drosophila, but on both human datasets the published cNODE error falls inside the null's CI. Interaction learning shows no measurable gain on human-associated data in this benchmark.
Caveats: our de-dup yields 143 human-oral samples vs 150 reported; published values are point estimates.
gLV twin under LOO: Drosophila 0.074, soil in vitro 0.099 - does NOT beat published cNODE (earlier 10-fold 0.052 retracted).
