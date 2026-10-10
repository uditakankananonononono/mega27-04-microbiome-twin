# Body-page appendix boundary correction, October 10, 2026

The frozen counting intent excludes appendices, but implementation stopped at Appendix A only. In this manuscript Appendix B starts on PDF page 65, while Appendix A is on page 113. Later appendix prose was incorrectly counted as body. Corrected implementation stops at the FIRST Appendix heading, regardless of lettering. No manuscript prose/layout, scientific result or user target changed.

Recomputed DOCX counts: 190 body prose paragraphs, 138530 characters, 19625 words. Density-equivalent estimates 55.41 pages at 2500 chars/page and 46.18 at 3000 chars/page. Previous estimate was 224 paragraphs/150685 chars/21294 words, including 1669 appendix words. The corrected method removes them. Physical PDF still 118 pages; certified_50_body_pages remains false.

Actual PDF pages 3-7 visually inspected: prose, equations, headings and tables are interspersed, with some pages substantially occupied by excluded content. Page word counts and physical page total cannot certify the gate. A complete body-only page-layout census has NOT been performed. No 50-page pass is claimed and no padding or threshold reduction performed.

Regression fixture puts Appendix B before Appendix A and verifies all later prose excluded. Targeted audit tests 2 passed. Full fresh-suite guarded publication reported separately. Historical audit files retain their chronology; this correction supersedes the current numeric body estimate, not source/science gates.
