#!/usr/bin/env python3
"""
step2_prepare_downloads.py
──────────────────────────
• Input  : species_shortlist.csv  (output from Step 1)
• Output : species_shortlist_clean.csv   – rows that *do* have lifespan data
           species_shortlist_oneasm.csv  – one best assembly per species
"""

import pandas as pd

##############################################################################
# 1. Load the shortlist produced in Step 1
##############################################################################
short = pd.read_csv("species_shortlist.csv")

##############################################################################
# 2-a.  Drop rows whose lifespan is blank / NaN
##############################################################################
clean = short.dropna(subset=["max_lifespan_years"])
removed = len(short) - len(clean)
print(f"Removed {removed} species without lifespan; {len(clean)} remain.")
clean.to_csv("species_shortlist_clean.csv", index=False)

##############################################################################
# 2-b.  Choose one assembly per species
#       • Preference order: Complete Genome < Chromosome < Scaffold < Contig
##############################################################################
assembly_rank = {
    "Complete Genome": 0,
    "Chromosome":      1,
    "Scaffold":        2,
    "Contig":          3
}

clean["rank"] = clean["assembly_level"].map(
    lambda x: assembly_rank.get(x, 4))      # default 4 for odd labels

oneasm = (clean
          .sort_values(["rank", "assembly_accession"])   # best first
          .drop_duplicates("species_name", keep="first") # keep first per species
          .drop(columns="rank"))

oneasm.to_csv("species_shortlist_oneasm.csv", index=False)

##############################################################################
# 3. Quick preview
##############################################################################
print("\nPreview of species_shortlist_oneasm.csv:")
print(oneasm.head(10).to_string(index=False))
print(f"\nFinal species count: {len(oneasm)}")
