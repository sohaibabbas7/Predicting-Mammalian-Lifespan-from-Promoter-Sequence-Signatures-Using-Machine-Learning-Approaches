#!/usr/bin/env bash
CSV=species_shortlist_oneasm.csv      # adjust if you used another filename
OUTDIR=data/genomes
mkdir -p "$OUTDIR"

tail -n +2 "$CSV" | while IFS=, read -r SPECIES ACC LVL LIFE; do
    echo "▶ $SPECIES  ($ACC)"
    datasets download genome accession "$ACC" \
        --filename "$OUTDIR/${ACC}.zip" \
        --include genome,gff3
    unzip -q "$OUTDIR/${ACC}.zip" -d "$OUTDIR/$ACC"
    rm "$OUTDIR/${ACC}.zip"
done
