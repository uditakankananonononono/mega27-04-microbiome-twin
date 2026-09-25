#!/bin/bash
# Chain D: waits for 2b stream A, then cnode2+lgbm arms (small to large), then weights, then T1 shard 1
cd ~/mega27/item04/mega27-04-microbiome-twin
while ! grep -q B2A_DONE /tmp/bench_2b_a.log 2>/dev/null; do sleep 60; done
for d in Drosophila_Gut Human_Gut Human_Oral Ocean Soil_Vitro Soil_Vivo; do
  python3 run_bench.py $d lgbm 10 >> /tmp/bench_arms.log 2>&1
  python3 run_bench.py $d cnode2 10 >> /tmp/bench_arms.log 2>&1
done
echo ARMS_DONE >> /tmp/bench_arms.log
python3 scripts/stack_weights.py Human_Oral Ocean Soil_Vitro Soil_Vivo Drosophila_Gut >> /tmp/weights.log 2>&1
echo WEIGHTS_DONE >> /tmp/weights.log
OMP_NUM_THREADS=1 T1_SHARD=1 T1_NSHARD=2 python3 scripts/twindiscovery_t1.py >> /tmp/t1_s1.log 2>&1
echo T1_S1_DONE >> /tmp/t1_s1.log
