#!/bin/bash
# Chain E: wave-2 arms (xgb, catb, ridgeclr) after chain D arms finish - all fast tree/linear models
cd ~/mega27/item04/mega27-04-microbiome-twin
while ! grep -q ARMS_DONE /tmp/bench_arms.log 2>/dev/null; do sleep 60; done
for d in Drosophila_Gut Human_Gut Human_Oral Ocean Soil_Vitro Soil_Vivo; do
  python3 run_bench.py $d xgb,catb,ridgeclr 10 >> /tmp/bench_wave2.log 2>&1
done
echo WAVE2_DONE >> /tmp/bench_wave2.log
