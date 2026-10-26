#!/usr/bin/env python3
"""
Generate publication-quality Figure 5 for StateShift:
Panel A: Condition Accuracies with 95% CIs on Authentic Physical GPU Run (N=100).
Panel B: Matched-Pairs Contingency Matrix (Condition F vs Condition D).
"""

import matplotlib.pyplot as plt
import numpy as np

# Set publication style
plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 11,
    'axes.labelsize': 12,
    'axes.titlesize': 12,
    'xtick.labelsize': 11,
    'ytick.labelsize': 11,
    'legend.fontsize': 10,
    'figure.titlesize': 14
})

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.5, 4.2), gridspec_kw={'width_ratios': [1.2, 1]})

# --- Panel A: Condition Accuracies ---
conditions = ['Cond A\n(Zero-Shot)', 'Cond D\n(Forced Restart)', 'Cond E\n(Explicit Repair)', 'Cond F\n(State-Preserving)']
accs = [64.0, 67.0, 71.0, 73.0]
# Wilson score 95% CIs for N=100
ci_lower = [54.2, 57.3, 61.4, 63.5]
ci_upper = [72.7, 75.4, 79.1, 80.9]
yerr_lower = [accs[i] - ci_lower[i] for i in range(4)]
yerr_upper = [ci_upper[i] - accs[i] for i in range(4)]

colors = ['#7f8c8d', '#e67e22', '#2980b9', '#27ae60']

bars = ax1.bar(conditions, accs, yerr=[yerr_lower, yerr_upper], capsize=5, color=colors, alpha=0.85, edgecolor='black', linewidth=1.2, width=0.55)

for bar, acc in zip(bars, accs):
    yval = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2.0, yval + 3.0, f'{acc:.1f}%', ha='center', va='bottom', fontweight='bold', fontsize=11)

ax1.set_ylabel('Accuracy on MATH-500 (%)')
ax1.set_ylim(0, 92)
ax1.set_title('(A) Condition Accuracy Comparison (N=100)', pad=10)
ax1.grid(axis='y', linestyle='--', alpha=0.5)

# Add annotation for primary delta
ax1.annotate('', xy=(3, 84), xytext=(1, 84),
            arrowprops=dict(arrowstyle='<->', color='black', lw=1.2))
ax1.text(2, 85.5, r'$\hat{\tau}_{F-D} = +6.0\%$ ($p = 0.109$, odds 4:1)', ha='center', va='bottom', fontsize=10, fontweight='bold')

# --- Panel B: Matched Contingency Heatmap ---
# Matrix: rows = F (1, 0), cols = D (1, 0)
matrix = np.array([[65, 8],
                   [2, 25]])

im = ax2.imshow(matrix, cmap='Blues', alpha=0.7)

ax2.set_xticks([0, 1])
ax2.set_yticks([0, 1])
ax2.set_xticklabels(['Success (1)', 'Failure (0)'])
ax2.set_yticklabels(['Success (1)', 'Failure (0)'])
ax2.set_xlabel('Condition D (Forced Restart)')
ax2.set_ylabel('Condition F (State-Preserving)')
ax2.set_title('(B) Paired Outcomes Contingency ($N=100$)', pad=10)

# Add text values
for i in range(2):
    for j in range(2):
        val = matrix[i, j]
        label = f'n = {val}'
        if i == 0 and j == 1:
            label += '\n(F wins, b=8)'
            color = '#1b5e20'
            fontweight = 'bold'
        elif i == 1 and j == 0:
            label += '\n(D wins, c=2)'
            color = '#b71c1c'
            fontweight = 'bold'
        else:
            color = 'black'
            fontweight = 'normal'
        ax2.text(j, i, label, ha='center', va='center', color=color, fontweight=fontweight, fontsize=11)

plt.tight_layout()
fig_path_pdf = '/Users/shamthakare/.gemini/antigravity/scratch/stateshift_reconstruction_2026/research_mission_19/figures/figure5_results.pdf'
fig_path_png = '/Users/shamthakare/.gemini/antigravity/scratch/stateshift_reconstruction_2026/research_mission_19/figures/figure5_results.png'
plt.savefig(fig_path_pdf, dpi=300, bbox_inches='tight')
plt.savefig(fig_path_png, dpi=300, bbox_inches='tight')
print(f"Successfully generated {fig_path_pdf} and {fig_path_png}")
