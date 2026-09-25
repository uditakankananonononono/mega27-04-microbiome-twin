# Item 4 morning sequence (deadline 1:00 PM IST Sep 26)
1. Check /tmp/bench_2b_c.log (B2C_DONE), /tmp/bench_arms.log (ARMS_DONE), /tmp/weights.log (WEIGHTS_DONE), /tmp/t1_s0.log, /tmp/t1_s1.log, /tmp/t1_consensus.log, /tmp/t2.log (CHAIN_C_ALL_DONE).
2. Commit every landed results/bench_*.json + bootstraps (paired_bootstrap vs best base per dataset, verdict WIN/tie/LOSS), stack_weights.json, twindiscovery_*.json/csv.
3. If T1 <60% done by 9 AM: commit PREREG_twindiscovery_amendment.md with completion-order stopping rule BEFORE opening any T1 output.
4. Rewrite paper Abstract + Findings in build_paper.py to the final verified scoreboard (win lane = match + interpretable-blend plus point; Human_Oral published point-win; every LOSS named).
4b. NOVELTY-FIRST restructure (9:41 directive): reorder Results so the 160-study predictability map (with the assembly-artefact catch) and the MDSINE2 metric-artifact result lead, keystones + T1/T2 close as the discovery arc, benchmark tables support. Fix all "(Section X.Y)" cross-references after moving blocks.
4c. ISEF JUDGE LOOP (9:42 directive): after gates pass, run the ChatGPT loop - write lease + Continue-with-Google if profile has a Google session, else anonymous free tier (report the substitution). Question: would this project win ISEF + weaknesses. Record each round verbatim (question, critique, fix applied) in ISEF_JUDGE_ROUNDS.md, fix and re-ask until no material weaknesses or only wet-lab/large-GPU items remain. Report the final verdict exactly as given.
5. ./finalize_paper.sh (rebuild, pdfinfo>=50 pages, pdffonts pure TNR, tools>=40, datasets>=120, bundle, push).
6. Upload paper PDF + DOCX + git bundle to Drive folder 1D-yJqoTmmIb9EvrTHN0LiVYfZIajKGeP (absolute paths, tools google-drive upload --parent-id).
7. Report final per-gate state to parent with honest shortfalls.
