# Original academic ATM project

The 18 files listed in `manifest.json` were copied byte-for-byte from the supplied workspace on 2026-09-22. The manifest records relative paths, sizes, and SHA-256 hashes. This README and the manifest are archive metadata, not original submission files.

Run `python docs/original-college-project/atm_simulation.py` from the repository root. The fictional demo PIN is `2468` and each run starts with $500.

The script and diagrams retain their original limitations, including float money, non-finite/sub-cent input acceptance, process-local state, and inconsistent diagram connectors. Preserve these files as provenance; implement corrected behavior in `src/bankflow/`. See the [baseline analysis](../analysis/PROJECT_ANALYSIS.md).
