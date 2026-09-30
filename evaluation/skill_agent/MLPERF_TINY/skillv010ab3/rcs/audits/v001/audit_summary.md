# Steps 12-17 audit summary v001
12 Claim audit: numbers re-read against project/paper.txt via numcheck.py; only derived numbers (0.01, 0.1, 1.5, 1.6, 1.7, about 6) absent from source, all traced to E038. Negative result E026 reported in main text (5.2). No orphan claims after tagging.
13 Flow: each section opens with its question or a link back; RQ1 and RQ2 answered in 6.1.
14 Terms: TinyML, MCU, quantization, PTQ/QAT, Top-1, AUC, autoencoder, log-mel, DUT, runner, FPGA, RISC-V defined at first use; remaining lint acronym warnings are product/dataset names or reference metadata.
15 Tables: four tables, each with takeaway caption, prose statement and RQ link; cards in plan/figure_cards. Tables 1,2,4 reconstructed from damaged extraction and labelled.
16 Citations: 18 citations, all in registry (user_supplied_file, abstract depth), each used only for the role the project paper states; [16],[19] not cited (no year). Reddi/Gal-On cited with et al. form.
17 Overclaim: lint 0 errors; 'first industry-standard' attributed to authors and scoped to their three-benchmark comparison (L008); causal attribution of diversity to modular design marked as the authors' interpretation (C014, low confidence); 'showed'/'shows' used only for direct observations.
