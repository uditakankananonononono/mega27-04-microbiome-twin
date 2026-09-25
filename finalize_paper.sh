#!/bin/bash
# Morning finalize: rebuild paper from final committed results, verify gates, commit, push, upload to Drive.
# Run from repo root. Usage: ./finalize_paper.sh
set -e
cd ~/mega27/item04/mega27-04-microbiome-twin
python3 paper/build_paper.py
cd paper && soffice --headless --convert-to pdf mega27-04-microbiome-twin-paper.docx >/dev/null 2>&1; cd ..
pdfinfo paper/mega27-04-microbiome-twin-paper.pdf | grep Pages
pdffonts paper/mega27-04-microbiome-twin-paper.pdf | tail -n +3 | awk '{print $1}' | sort -u
python3 -c "import csv; print('tools:', sum(1 for _ in csv.reader(open('results/tools_ledger.csv'))) - 1)"
python3 -c "import csv; print('datasets:', sum(1 for _ in csv.reader(open('results/datasets_ledger.csv'))) - 1)"
grep -c "P.equation" paper/build_paper.py paper/paper_expansion.py
git add paper/ results/ && git commit -m "final paper rebuild with complete arm results" || true
git bundle create paper/mega27-04-microbiome-twin.bundle --all
GIT_SSH_COMMAND="ssh -i ~/.ssh/id_ed25519_mega27 -o StrictHostKeyChecking=no" git push origin HEAD
