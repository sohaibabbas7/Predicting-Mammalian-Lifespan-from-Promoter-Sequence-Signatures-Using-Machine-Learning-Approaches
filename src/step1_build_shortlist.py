#!/usr/bin/env python3
"""
Step 1 – build species_shortlist.csv
────────────────────────────────────
• Intersect NCBI RefSeq mammalian assemblies (download-table TSV)
  with AnAge longevity data (full dataset TXT).
• Output columns:
    species_name, assembly_accession, assembly_level, max_lifespan_years
"""
import re
import pandas as pd

##############################################################################
# helper -- normalise a taxon name to "genus species" (lower-case, no punctuation)
##############################################################################
def normalise(name: str) -> str:
    """Return first two Latin words in lower-case (e.g. 'Homo sapiens')."""
    if pd.isna(name):
        return ""
    # drop anything inside parentheses or after commas
    name = re.split(r"[,(]", name)[0]
    # squeeze whitespace & keep first two tokens
    tokens = re.sub(r"\s+", " ", name.strip()).split()[:2]
    return " ".join(tokens).lower() if len(tokens) == 2 else ""

##############################################################################
# 1. LOAD NCBI TABLE
##############################################################################
ncbi = pd.read_csv("ncbi_dataset.tsv", sep="\t", dtype=str)

# flexible header detection
name_col  = next(c for c in ncbi.columns
                 if c.lower().startswith(("scientific name", "organism")))
try:
    acc_col = next(c for c in ncbi.columns
                   if "refseq" in c.lower() and "accession" in c.lower())
except StopIteration:
    acc_col = next(c for c in ncbi.columns if "assembly accession" in c.lower())
level_col = next(c for c in ncbi.columns if "assembly level" in c.lower())

ncbi["species_name"] = ncbi[name_col].apply(normalise)
ncbi_subset = ncbi[["species_name", acc_col, level_col]].copy()
ncbi_subset.columns = ["species_name", "assembly_accession", "assembly_level"]

##############################################################################
# 2. LOAD ANAGE TABLE
##############################################################################
anage = pd.read_csv("anage_data.txt", sep="\t", dtype=str, na_values=["", "NA"])
anage["species_name"] = (
    anage["Genus"].str.cat(anage["Species"], sep=" ").apply(normalise)
)
anage_subset = anage[["species_name", "Maximum longevity (yrs)"]].copy()
anage_subset.columns = ["species_name", "max_lifespan_years"]

##############################################################################
# 3. INNER JOIN
##############################################################################
shortlist = ncbi_subset.merge(anage_subset, on="species_name", how="inner")

##############################################################################
# 4. SAVE + PREVIEW
##############################################################################
shortlist.to_csv("species_shortlist.csv", index=False)

print("\nFirst 10 rows of intersect:")
print(shortlist.head(10).to_string(index=False))
print(f"\nTotal species after intersect: {shortlist.shape[0]}")

##############################################################################
# 5. DIAGNOSTICS (quick visibility if overlap is still zero)
##############################################################################
print("\n── diagnostics ─────────────────────────────────────────")
print(f"Rows in NCBI table : {len(ncbi_subset)}")
print(f"Rows in AnAge table: {len(anage_subset)}")

print("\nSample NCBI names  :", ncbi_subset['species_name'].dropna().unique()[:8])
print("Sample AnAge names :", anage_subset['species_name'].dropna().unique()[:8])

common = set(ncbi_subset['species_name']) & set(anage_subset['species_name'])
print(f"\nRaw intersection size: {len(common)}")
print("Sample overlaps      :", list(common)[:10])
print("─────────────────────────────────────────────────────────")
