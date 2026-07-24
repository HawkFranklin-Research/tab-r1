# -*- coding: utf-8 -*-
"""
Python script to generate Kaplan-Meier survival curves and label distribution
plots for the cancer cohorts (BRCA, ESCA, HNSCC, LSCC, LUAD).
Creates:
figures/cancer_survival_lifelines.png
"""

import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from lifelines import KaplanMeierFitter

# Create figures directory if not exists
os.makedirs("figures", exist_ok=True)

# Color Palette: "Aurora Mint & Obsidian"
BG_COLOR = "#FAF9F6"      # Soft Alabaster
OBSIDIAN = "#0F1728"      # Primary Text / Slate
CORAL = "#FF5A5F"         # Accent A: TabPFN
AURORA_MINT = "#06D6A0"   # Accent B: TabFM
SAFFRON_GOLD = "#F4A261"  # Accent C: Baselines
MUDDY_TEAL = "#2A9D8F"    # Auxiliary color
DEEP_PURPLE = "#4A357A"

plt.rcParams['figure.facecolor'] = BG_COLOR
plt.rcParams['axes.facecolor'] = BG_COLOR
plt.rcParams['text.color'] = OBSIDIAN
plt.rcParams['axes.labelcolor'] = OBSIDIAN
plt.rcParams['xtick.color'] = OBSIDIAN
plt.rcParams['ytick.color'] = OBSIDIAN
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.edgecolor'] = OBSIDIAN
plt.rcParams['axes.linewidth'] = 0.8
plt.rcParams['grid.color'] = '#E6E4DC'
plt.rcParams['grid.linestyle'] = '--'

# Load the cohort indices
input_root = "/home/prime/Documents/g3/c-5/gpt/processed/train_ready"
cancers = ["BRCA", "ESCA", "HNSCC", "LSCC", "LUAD"]

cancer_data = {}
for cancer in cancers:
    path = os.path.join(input_root, cancer, "core", "sample_index.csv")
    if os.path.exists(path):
        df = pd.read_csv(path)
        df["OS_days"] = pd.to_numeric(df["OS_days"], errors="coerce")
        df["OS_event"] = pd.to_numeric(df["OS_event"], errors="coerce")
        # Keep only valid rows
        df_valid = df.dropna(subset=["OS_days", "OS_event"])
        cancer_data[cancer] = df_valid

# Setup subplots: 1 row, 3 columns
fig, axes = plt.subplots(1, 3, figsize=(18, 5))
fig.suptitle("TCGA Cohort Overall Survival (OS) and Horizon Classification Breakdown", fontsize=15, fontweight='bold', color=OBSIDIAN, y=1.02)

# Panel A: Kaplan-Meier Survival Curves
axA = axes[0]
km_colors = {
    "BRCA": DEEP_PURPLE,
    "ESCA": CORAL,
    "HNSCC": SAFFRON_GOLD,
    "LSCC": MUDDY_TEAL,
    "LUAD": "#1D4ED8" # Royal Blue
}

kmf = KaplanMeierFitter()
for cancer in cancers:
    if cancer in cancer_data:
        df_c = cancer_data[cancer]
        # Convert days to years for readability
        T = df_c["OS_days"] / 365.25
        E = df_c["OS_event"]
        kmf.fit(T, event_observed=E, label=f"{cancer} (n={len(df_c)})")
        kmf.plot(ax=axA, color=km_colors[cancer], ci_show=False, linewidth=2)

axA.set_xlabel("Time (Years)", fontweight='bold')
axA.set_ylabel("Overall Survival Probability", fontweight='bold')
axA.set_xlim(0, 10)
axA.set_ylim(0, 1)
axA.grid(True)
axA.set_title("A: Kaplan-Meier Curves", fontsize=12, fontweight='bold')
axA.legend(loc="lower left")

# Panel B & C: 3-Year and 5-Year Horizon Breakdown
# Data from the report table
cancer_names = ["BRCA", "ESCA", "HNSCC", "LSCC", "LUAD"]

# 3-Year Counts
c3_survived = [430, 18, 175, 185, 161]
c3_died = [71, 68, 210, 170, 157]
c3_excluded = [679, 96, 239, 220, 292]

# 5-Year Counts
c5_survived = [249, 4, 54, 82, 57]
c5_died = [101, 75, 232, 199, 194]
c5_excluded = [830, 103, 338, 294, 359]

x = np.arange(len(cancer_names))
width = 0.25

# Plot 3-Year horizon (Panel B)
axB = axes[1]
axB.bar(x - width, c3_survived, width, label="Class 0: Survived past 3-Yr", color=AURORA_MINT, edgecolor=OBSIDIAN)
axB.bar(x, c3_died, width, label="Class 1: Died within 3-Yr", color=CORAL, edgecolor=OBSIDIAN)
axB.bar(x + width, c3_excluded, width, label="Excluded: Censored before 3-Yr", color="#B0B0B0", edgecolor=OBSIDIAN)
axB.set_xticks(x)
axB.set_xticklabels(cancer_names, fontweight='bold')
axB.set_ylabel("Patient Count", fontweight='bold')
axB.set_title("B: 3-Year OS Horizon Breakdown", fontsize=12, fontweight='bold')
axB.legend(loc="upper right", fontsize=9)
axB.grid(True, axis="y")

# Plot 5-Year horizon (Panel C)
axC = axes[2]
axC.bar(x - width, c5_survived, width, label="Class 0: Survived past 5-Yr", color=AURORA_MINT, edgecolor=OBSIDIAN)
axC.bar(x, c5_died, width, label="Class 1: Died within 5-Yr", color=CORAL, edgecolor=OBSIDIAN)
axC.bar(x + width, c5_excluded, width, label="Excluded: Censored before 5-Yr", color="#B0B0B0", edgecolor=OBSIDIAN)
axC.set_xticks(x)
axC.set_xticklabels(cancer_names, fontweight='bold')
axC.set_ylabel("Patient Count", fontweight='bold')
axC.set_title("C: 5-Year OS Horizon Breakdown", fontsize=12, fontweight='bold')
axC.legend(loc="upper right", fontsize=9)
axC.grid(True, axis="y")

plt.tight_layout()
plt.savefig("figures/cancer_survival_lifelines.png", dpi=300, bbox_inches='tight')
plt.close()

print("Survival lifelines figure successfully generated!")
