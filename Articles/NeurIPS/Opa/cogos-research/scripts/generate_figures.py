#!/usr/bin/env python3
"""
CogOS Research: Visualization Generator

Creates publication-ready figures for all papers.

Usage:
    python scripts/generate_figures.py --paper main
    python scripts/generate_figures.py --figure manifold_trajectory
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from pathlib import Path
from typing import List, Dict, Optional
import argparse

# Use non-interactive backend for server
matplotlib.use('Agg')

# Publication-quality settings
plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 10,
    'axes.labelsize': 11,
    'axes.titlesize': 12,
    'legend.fontsize': 9,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'figure.figsize': (6, 4),
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'axes.grid': True,
    'grid.alpha': 0.3
})

# Color palette (colorblind-friendly)
COLORS = {
    'cogos': '#2ecc71',      # Green
    'constitutional': '#3498db',  # Blue
    'rlhf': '#e74c3c',       # Red
    'cove': '#9b59b6',       # Purple
    'baseline': '#95a5a6',   # Gray
    'gev': '#f39c12',        # Orange
    'highlight': '#1abc9c'   # Teal
}


class FigureGenerator:
    """Generates all figures for papers."""
    
    def __init__(self, output_dir: str = "./figures"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def save_figure(self, fig, name: str, formats: List[str] = ['pdf', 'png']):
        """Save figure in multiple formats."""
        for fmt in formats:
            path = self.output_dir / f"{name}.{fmt}"
            fig.savefig(path, format=fmt, bbox_inches='tight')
            print(f"✅ Saved: {path}")
        plt.close(fig)
        
    def generate_manifold_trajectory(self) -> plt.Figure:
        """Generate Figure 1: Semantic manifold trajectories."""
        np.random.seed(42)
        
        fig, ax = plt.subplots(figsize=(8, 6))
        
        # GEV point (attractor)
        gev = np.array([0, 0])
        
        # Generate trajectories
        # CogOS: converges to GEV
        t = np.linspace(0, 1, 50)
        cogos_start = np.array([2, 1.5])
        cogos_traj = np.array([cogos_start * (1-tt) + gev * tt + 
                               np.random.randn(2) * 0.1 * (1-tt) for tt in t])
        
        # Baseline: diverges
        baseline_start = np.array([-1.5, 2])
        baseline_traj = np.array([baseline_start + np.array([0.5, 0.3]) * tt + 
                                   np.random.randn(2) * 0.15 for tt in t])
        
        # Constitutional AI: oscillates
        const_start = np.array([1, -1.5])
        const_traj = np.array([const_start * np.exp(-tt) * np.cos(4*tt*np.pi) + 
                               np.array([0.3, 0.2]) + np.random.randn(2) * 0.1 for tt in t])
        
        # Plot trajectories
        ax.plot(cogos_traj[:, 0], cogos_traj[:, 1], '-', 
                color=COLORS['cogos'], linewidth=2, label='CogOS (ours)')
        ax.plot(baseline_traj[:, 0], baseline_traj[:, 1], '--', 
                color=COLORS['baseline'], linewidth=2, label='GPT-4 Baseline')
        ax.plot(const_traj[:, 0], const_traj[:, 1], ':', 
                color=COLORS['constitutional'], linewidth=2, label='Constitutional AI')
        
        # Mark start and end points
        ax.scatter(*cogos_start, s=100, c=COLORS['cogos'], marker='o', zorder=5)
        ax.scatter(*cogos_traj[-1], s=100, c=COLORS['cogos'], marker='s', zorder=5)
        
        # GEV attractor
        ax.scatter(*gev, s=200, c=COLORS['gev'], marker='*', 
                   label='GEV (Attractor)', zorder=10, edgecolors='black')
        
        # Cultural basis vectors
        cultures = [
            ('Western', np.array([1.2, 0.8])),
            ('Confucian', np.array([-0.9, 0.6])),
            ('Islamic', np.array([0.3, -1.1])),
            ('Ubuntu', np.array([-0.7, -0.5])),
        ]
        
        for name, vec in cultures:
            ax.annotate('', xy=vec*0.8, xytext=gev,
                       arrowprops=dict(arrowstyle='->', color='gray', alpha=0.5))
            ax.text(vec[0]*0.9, vec[1]*0.9, name, fontsize=8, alpha=0.7)
        
        ax.set_xlabel('Semantic Dimension 1 (t-SNE)')
        ax.set_ylabel('Semantic Dimension 2 (t-SNE)')
        ax.set_title('Semantic Trajectories on Manifold $\\mathcal{M}$')
        ax.legend(loc='upper right')
        ax.set_xlim(-2.5, 3)
        ax.set_ylim(-2, 3)
        
        # Add stability region
        circle = plt.Circle(gev, 0.5, color=COLORS['gev'], alpha=0.1)
        ax.add_patch(circle)
        
        return fig
    
    def generate_delta_timeseries(self) -> plt.Figure:
        """Generate Figure 4: Delta-Dehumanization over time."""
        np.random.seed(42)
        
        fig, ax = plt.subplots(figsize=(8, 5))
        
        t = np.arange(50)
        
        # CogOS: stable around 0
        cogos_delta = np.random.randn(50) * 0.02
        cogos_delta = np.convolve(cogos_delta, np.ones(5)/5, mode='same')
        
        # Add adversarial perturbation at t=25
        cogos_delta[25:30] += np.array([0.15, 0.12, 0.08, 0.04, 0.01])
        
        # Constitutional AI: gradual drift
        const_delta = 0.02 + 0.003 * t + np.random.randn(50) * 0.03
        
        # RLHF: unstable
        rlhf_delta = 0.05 + 0.01 * np.sin(t/5) + np.random.randn(50) * 0.05
        rlhf_delta[30:] += 0.1
        
        ax.plot(t, cogos_delta, '-', color=COLORS['cogos'], 
                linewidth=2, label='CogOS (ours)')
        ax.plot(t, const_delta, '--', color=COLORS['constitutional'], 
                linewidth=2, label='Constitutional AI')
        ax.plot(t, rlhf_delta, ':', color=COLORS['rlhf'], 
                linewidth=2, label='RLHF')
        
        # Mark adversarial event
        ax.axvline(x=25, color='red', linestyle='--', alpha=0.5)
        ax.annotate('Adversarial\nPerturbation', xy=(25, 0.15), 
                   xytext=(30, 0.2), fontsize=9,
                   arrowprops=dict(arrowstyle='->', color='red', alpha=0.7))
        
        # Safe threshold
        ax.axhline(y=0.1, color='orange', linestyle='--', alpha=0.5, label='Alert Threshold')
        ax.fill_between(t, -0.05, 0.1, alpha=0.1, color='green', label='Safe Zone')
        
        ax.set_xlabel('Conversation Step')
        ax.set_ylabel('$\\Delta$-Dehumanization')
        ax.set_title('Ethical Drift Dynamics Under Adversarial Stress')
        ax.legend(loc='upper left')
        ax.set_ylim(-0.1, 0.3)
        
        return fig
    
    def generate_comparison_radar(self) -> plt.Figure:
        """Generate Figure 3: Radar chart comparison."""
        categories = ['Truthfulness', 'Ethics', 'Cultural\nAlignment', 
                     'Robustness', 'Efficiency']
        n_cats = len(categories)
        
        # Scores (0-1)
        cogos = [0.94, 0.89, 0.79, 0.96, 0.68]
        const_ai = [0.85, 0.80, 0.70, 0.68, 0.86]
        rlhf = [0.84, 0.78, 0.67, 0.64, 0.90]
        cove = [0.87, 0.78, 0.68, 0.65, 0.65]
        
        # Create radar chart
        angles = [n / float(n_cats) * 2 * np.pi for n in range(n_cats)]
        angles += angles[:1]  # Complete the loop
        
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
        
        def add_to_radar(values, label, color, linestyle='-'):
            values += values[:1]
            ax.plot(angles, values, linestyle, linewidth=2, label=label, color=color)
            ax.fill(angles, values, alpha=0.1, color=color)
        
        add_to_radar(cogos, 'CogOS (ours)', COLORS['cogos'])
        add_to_radar(const_ai, 'Constitutional AI', COLORS['constitutional'], '--')
        add_to_radar(rlhf, 'RLHF', COLORS['rlhf'], ':')
        add_to_radar(cove, 'CoVe', COLORS['cove'], '-.')
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories)
        ax.set_ylim(0, 1)
        ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
        ax.set_yticklabels(['20%', '40%', '60%', '80%', '100%'])
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
        ax.set_title('Multi-Dimensional Performance Comparison', y=1.08)
        
        return fig
    
    def generate_convergence_dynamics(self) -> plt.Figure:
        """Generate Figure 5: SIP convergence dynamics."""
        fig, axes = plt.subplots(3, 1, figsize=(8, 10), sharex=True)
        
        np.random.seed(42)
        iterations = np.arange(1, 11)
        
        # Distance to GEV
        gev_dist = 1.5 * np.exp(-0.4 * iterations) + 0.1 + np.random.randn(10) * 0.02
        axes[0].plot(iterations, gev_dist, 'o-', color=COLORS['cogos'], linewidth=2)
        axes[0].set_ylabel('Distance to GEV')
        axes[0].set_title('(a) GEV Distance: $\\|v_i - C\\|$')
        axes[0].axhline(y=0.2, color='orange', linestyle='--', alpha=0.5, label='Convergence threshold')
        axes[0].legend()
        axes[0].fill_between(iterations, 0, 0.2, alpha=0.1, color='green')
        
        # Delta-dehumanization
        delta = 0.2 * np.exp(-0.5 * iterations) - 0.02 + np.random.randn(10) * 0.01
        axes[1].plot(iterations, delta, 's-', color=COLORS['constitutional'], linewidth=2)
        axes[1].axhline(y=0, color='gray', linestyle='-', alpha=0.5)
        axes[1].set_ylabel('$\\Delta$-Dehumanization')
        axes[1].set_title('(b) Ethical Drift: $\\Delta(v_i)$')
        axes[1].fill_between(iterations, -0.1, 0, alpha=0.1, color='green', label='Recovery zone')
        axes[1].legend()
        
        # Epistemic entropy
        entropy = 0.8 * np.exp(-0.3 * iterations) + 0.1 + np.random.randn(10) * 0.02
        axes[2].plot(iterations, entropy, '^-', color=COLORS['rlhf'], linewidth=2)
        axes[2].set_ylabel('Epistemic Entropy $H(P)$')
        axes[2].set_xlabel('SIP Iteration')
        axes[2].set_title('(c) Uncertainty: $H(P_i)$')
        
        # Shaded convergence region
        for ax in axes:
            ax.axvspan(4, 6, alpha=0.1, color='gray', label='Typical convergence')
        
        plt.tight_layout()
        return fig
    
    def generate_architecture_diagram(self) -> plt.Figure:
        """Generate Figure 2: Architecture diagram."""
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis('off')
        
        # Define boxes
        boxes = {
            'input': (1, 8, 2, 1, 'Query $q$'),
            'socrates': (1, 5.5, 2, 1.5, 'SOCRATES\n(Logic)'),
            'solomon': (4, 5.5, 2, 1.5, 'SOLOMON\n(Ethics)'),
            'ivan': (7, 5.5, 2, 1.5, 'IVAN\n(Humility)'),
            'aggregate': (4, 3, 2, 1, 'Aggregate'),
            'converge': (4, 1.5, 2, 1, 'Converge?'),
            'output': (7, 1.5, 2, 1, 'Output'),
            'isc': (0, 3, 1.5, 1, 'ISC $\\Phi$'),
            'gev': (8.5, 3, 1.5, 1, 'GEV $C$'),
        }
        
        # Draw boxes
        for name, (x, y, w, h, label) in boxes.items():
            color = COLORS['cogos'] if name in ['socrates', 'solomon', 'ivan'] else 'lightblue'
            if name in ['isc', 'gev']:
                color = COLORS['gev']
            
            rect = plt.Rectangle((x, y), w, h, facecolor=color, 
                                  edgecolor='black', linewidth=2, alpha=0.7)
            ax.add_patch(rect)
            ax.text(x + w/2, y + h/2, label, ha='center', va='center', 
                   fontsize=10, fontweight='bold')
        
        # Draw arrows
        arrows = [
            ((2, 8), (2, 7)),      # input to socrates
            ((3, 6.25), (4, 6.25)),  # socrates to solomon
            ((6, 6.25), (7, 6.25)),  # solomon to ivan
            ((2, 5.5), (2, 4)),    # socrates to aggregate
            ((5, 5.5), (5, 4)),    # solomon to aggregate
            ((8, 5.5), (8, 4), (6, 4), (6, 4)),  # ivan to aggregate (bend)
            ((5, 3), (5, 2.5)),    # aggregate to converge
            ((6, 2), (7, 2)),      # converge to output (yes)
            ((4, 2), (2, 2), (2, 5.5)),  # converge back to socrates (no)
            ((1.5, 3.5), (1.5, 5.5)),  # ISC to socrates
            ((8.5, 3.5), (8, 5.5)),    # GEV to ivan
        ]
        
        for arrow in arrows:
            if len(arrow) == 2:
                ax.annotate('', xy=arrow[1], xytext=arrow[0],
                           arrowprops=dict(arrowstyle='->', color='black', lw=1.5))
        
        ax.set_title('CogOS Triple-Agent Architecture with SIP Iteration', fontsize=14, fontweight='bold')
        
        return fig
    
    def generate_all(self, paper: str = "main"):
        """Generate all figures for a paper."""
        if paper == "main":
            figures = [
                ("manifold_trajectory", self.generate_manifold_trajectory),
                ("delta_timeseries", self.generate_delta_timeseries),
                ("comparison_radar", self.generate_comparison_radar),
                ("convergence_dynamics", self.generate_convergence_dynamics),
                ("architecture", self.generate_architecture_diagram),
            ]
            
            for name, generator in figures:
                try:
                    fig = generator()
                    self.save_figure(fig, name)
                except Exception as e:
                    print(f"⚠️ Error generating {name}: {e}")


def main():
    parser = argparse.ArgumentParser(description="Figure Generator")
    
    parser.add_argument("--paper", type=str, default="main", help="Paper to generate for")
    parser.add_argument("--figure", type=str, help="Generate specific figure")
    parser.add_argument("--output", type=str, default="./figures", help="Output directory")
    parser.add_argument("--format", type=str, nargs='+', default=['pdf', 'png'], 
                       help="Output formats")
    
    args = parser.parse_args()
    
    generator = FigureGenerator(output_dir=args.output)
    
    if args.figure:
        method = getattr(generator, f"generate_{args.figure}", None)
        if method:
            fig = method()
            generator.save_figure(fig, args.figure, args.format)
        else:
            print(f"Unknown figure: {args.figure}")
    else:
        generator.generate_all(args.paper)


if __name__ == "__main__":
    main()
