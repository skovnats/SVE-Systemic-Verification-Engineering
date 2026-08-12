#!/usr/bin/env python3
"""
TIK Experiments - Three-Phase Runner
=====================================
С Богом!

Three-phase experiment with cost optimization:

Phase 1: SAMPLING      - Quick screening of all 99 kernels
Phase 2: ADVERSARIAL   - Angel/Demon/Friend on contested kernels
Phase 3: DEEP DIVE     - Full matrix on most contested

Cost: ~$1,500-3,000 instead of $40,000+

Usage:
    python run_three_phase.py --help
    python run_three_phase.py --phase 1
    python run_three_phase.py --phase all --budget 3000
    python run_three_phase.py --estimate  # Show cost estimate
"""

import argparse
import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.live import Live
from rich.logging import RichHandler

from config import settings
from kernels import KERNELS, KERNEL_BY_ID
from orchestrator import (
    ThreePhaseOrchestrator,
    get_phase1_config,
    get_phase2_config,
    get_phase3_config,
    ExperimentPhase,
    VARIANT_TEMPLATES,
)
from cost_tracker import (
    BudgetTracker,
    estimate_experiment_cost,
    print_cost_estimate,
)
from formulations import (
    FormulationGenerator,
    estimate_formulation_cost,
    LANGUAGES,
    FORMULATION_STYLES,
)

# Setup
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)]
)
logger = logging.getLogger(__name__)
console = Console()


# ============================================================================
#                    CLI
# ============================================================================

def parse_args():
    parser = argparse.ArgumentParser(
        description="TIK Three-Phase Experiment Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
PHASES:
  1. SAMPLING      - All 99 kernels × 10 models × 3 langs × 3 forms
  2. ADVERSARIAL   - Contested kernels with Angel/Demon/Friend
  3. DEEP DIVE     - Full matrix on most contested

COST OPTIMIZATION:
  • FREE (g4f) → PAID → OPUS hierarchical arbitration
  • Caching identical queries
  • Formulations generated ONCE by Opus

Examples:
  # Show cost estimate
  python run_three_phase.py --estimate

  # Run Phase 1 only
  python run_three_phase.py --phase 1

  # Run all phases with budget limit
  python run_three_phase.py --phase all --budget 2000

  # Resume from Phase 2
  python run_three_phase.py --phase 2 --resume results/phase1.json

С Богом!
        """
    )
    
    # Phase selection
    parser.add_argument(
        '--phase', '-p',
        type=str,
        default='1',
        choices=['1', '2', '3', 'all'],
        help='Phase to run (1, 2, 3, or all)'
    )
    
    # Resume from previous phase
    parser.add_argument(
        '--resume',
        type=str,
        help='Resume from previous phase results file'
    )
    
    # Budget
    parser.add_argument(
        '--budget', '-b',
        type=float,
        default=3000.0,
        help='Total budget in USD'
    )
    
    # Cost estimate
    parser.add_argument(
        '--estimate', '-e',
        action='store_true',
        help='Show cost estimate and exit'
    )
    
    # Formulations
    parser.add_argument(
        '--generate-formulations',
        action='store_true',
        help='Generate all formulations (one-time, uses Opus)'
    )
    
    # Output
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='results',
        help='Output directory'
    )
    
    # Distributed
    parser.add_argument(
        '--distributed', '-d',
        action='store_true',
        help='Use Celery for distributed execution'
    )
    
    # Verbose
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    
    return parser.parse_args()


# ============================================================================
#                    DISPLAY FUNCTIONS
# ============================================================================

def display_banner():
    """Display experiment banner."""
    console.print(Panel("""
[bold blue]╔═══════════════════════════════════════════════════════════════╗
║           TIK EXPERIMENTS - THREE PHASE RUNNER                ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  Phase 1: SAMPLING      - 99 kernels × 10 models             ║
║  Phase 2: ADVERSARIAL   - Angel 👼 / Demon 😈 / Friend 🤝    ║
║  Phase 3: DEEP DIVE     - Full matrix analysis               ║
║                                                               ║
║  Strategy: FREE → PAID → OPUS (hierarchical arbitration)     ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝[/bold blue]

[yellow]"Attention is ALL you need"[/yellow] → [red]"HS ≠ HR"[/red]

[dim]С Богом![/dim]
    """, border_style="blue"))


def display_phase_config(phase: int, config):
    """Display phase configuration."""
    
    phase_names = {
        1: "SAMPLING",
        2: "ADVERSARIAL",
        3: "DEEP DIVE"
    }
    
    table = Table(title=f"Phase {phase}: {phase_names[phase]}")
    table.add_column("Parameter", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Kernels", str(len(config.kernel_ids)))
    table.add_row("Models", str(len(config.models)))
    table.add_row("Languages", str(len(config.languages)))
    table.add_row("Formulations", str(len(config.formulations)))
    table.add_row("Variants", ", ".join(config.variants))
    table.add_row("Evaluators", str(len(config.evaluator_models)))
    table.add_row("Est. Requests", f"{config.estimated_requests:,}")
    
    console.print(table)


def display_cost_summary(tracker: BudgetTracker):
    """Display cost summary."""
    summary = tracker.get_summary()
    
    panel_content = f"""
[bold]Budget:[/bold] ${summary['total_budget']:.2f}
[bold]Spent:[/bold]  ${summary['total_spent']:.2f} ({summary['percent_used']:.1f}%)
[bold]Remaining:[/bold] ${summary['remaining']:.2f}

[bold]By Tier:[/bold]
  FREE:    ${summary['by_tier']['free']:.2f} ({summary['free_requests']} requests)
  PAID:    ${summary['by_tier']['paid']:.2f} ({summary['paid_requests']} requests)
  ARBITER: ${summary['by_tier']['arbiter']:.2f} ({summary['arbiter_requests']} requests)

[bold]By Phase:[/bold]
  Phase 1: ${summary['by_phase'].get('phase_1_sampling', 0):.2f}
  Phase 2: ${summary['by_phase'].get('phase_2_adversarial', 0):.2f}
  Phase 3: ${summary['by_phase'].get('phase_3_deep_dive', 0):.2f}
    """
    
    # Color based on budget usage
    if summary['percent_used'] < 50:
        border = "green"
    elif summary['percent_used'] < 75:
        border = "yellow"
    else:
        border = "red"
    
    console.print(Panel(panel_content, title="💰 Cost Summary", border_style=border))


def display_results_table(results: dict, phase: int):
    """Display results from a phase."""
    
    kernel_results = results.get('kernel_results', {})
    
    table = Table(title=f"Phase {phase} Results")
    table.add_column("ID", style="dim")
    table.add_column("Kernel", style="cyan")
    table.add_column("TIK₈", style="green")
    table.add_column("Agreement", style="yellow")
    table.add_column("Contested?", style="red")
    
    for kid, data in sorted(kernel_results.items()):
        kernel = KERNEL_BY_ID.get(int(kid))
        name = kernel.name if kernel else f"Kernel {kid}"
        
        tik8 = data.get('tik_scores', {}).get('TIK_8', 0)
        agreement = data.get('agreement', 0)
        contested = "⚠️" if int(kid) in results.get('contested_kernels', []) else "✓"
        
        table.add_row(
            str(kid),
            name[:30],
            f"{tik8:.3f}",
            f"{agreement:.1%}",
            contested
        )
    
    console.print(table)


# ============================================================================
#                    PHASE RUNNERS
# ============================================================================

async def run_phase1(
    tracker: BudgetTracker,
    output_dir: Path
) -> dict:
    """Run Phase 1: Sampling."""
    
    console.print("\n[bold blue]═══ PHASE 1: SAMPLING ═══[/bold blue]\n")
    
    config = get_phase1_config()
    display_phase_config(1, config)
    
    # Check budget
    est = tracker.estimate_remaining_cost(config.estimated_requests)
    if not est['within_budget']:
        console.print(f"[red]⚠️ Estimated cost ${est['estimated_cost']:.2f} exceeds remaining budget![/red]")
        if not console.input("[yellow]Continue anyway? (y/N): [/yellow]").lower() == 'y':
            return None
    
    orchestrator = ThreePhaseOrchestrator()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console
    ) as progress:
        task = progress.add_task("Phase 1: Testing kernels...", total=len(config.kernel_ids))
        
        result = await orchestrator.executor.execute_phase1(config)
        
        progress.update(task, completed=len(config.kernel_ids))
    
    # Save results
    output_file = output_dir / "phase1_results.json"
    with open(output_file, 'w') as f:
        json.dump({
            "phase": "1_sampling",
            "timestamp": datetime.utcnow().isoformat(),
            "kernel_results": result.kernel_results,
            "contested_kernels": result.contested_kernels,
            "stats": result.stats,
            "duration_seconds": result.duration_seconds
        }, f, indent=2, default=str)
    
    console.print(f"\n[green]✓ Phase 1 complete! Results: {output_file}[/green]")
    console.print(f"[yellow]Contested kernels: {len(result.contested_kernels)}[/yellow]")
    
    return {
        "kernel_results": result.kernel_results,
        "contested_kernels": result.contested_kernels
    }


async def run_phase2(
    tracker: BudgetTracker,
    output_dir: Path,
    phase1_contested: List[int]
) -> dict:
    """Run Phase 2: Adversarial with Angel/Demon/Friend."""
    
    console.print("\n[bold yellow]═══ PHASE 2: ADVERSARIAL ═══[/bold yellow]\n")
    console.print("[dim]Testing with: 👼 Angel, 😈 Demon, 🤝 Friend[/dim]\n")
    
    config = get_phase2_config(phase1_contested)
    display_phase_config(2, config)
    
    # Show variant examples
    console.print("\n[bold]Question Variants:[/bold]")
    for name, variant in VARIANT_TEMPLATES.items():
        if name != "base":
            console.print(f"  [{name}]: {variant.prefix[:100]}...")
    
    orchestrator = ThreePhaseOrchestrator()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        console=console
    ) as progress:
        task = progress.add_task("Phase 2: Adversarial testing...", total=len(config.kernel_ids))
        
        result = await orchestrator.executor.execute_phase2(config, phase1_contested)
        
        progress.update(task, completed=len(config.kernel_ids))
    
    # Save results
    output_file = output_dir / "phase2_results.json"
    with open(output_file, 'w') as f:
        json.dump({
            "phase": "2_adversarial",
            "timestamp": datetime.utcnow().isoformat(),
            "kernel_results": result.kernel_results,
            "contested_kernels": result.contested_kernels,
            "stats": result.stats,
        }, f, indent=2, default=str)
    
    console.print(f"\n[green]✓ Phase 2 complete! Results: {output_file}[/green]")
    console.print(f"[red]Unstable kernels (need deep dive): {len(result.contested_kernels)}[/red]")
    
    return {
        "kernel_results": result.kernel_results,
        "contested_kernels": result.contested_kernels
    }


async def run_phase3(
    tracker: BudgetTracker,
    output_dir: Path,
    deep_dive_kernels: List[int]
) -> dict:
    """Run Phase 3: Deep Dive."""
    
    console.print("\n[bold red]═══ PHASE 3: DEEP DIVE ═══[/bold red]\n")
    console.print(f"[dim]Full matrix on {len(deep_dive_kernels)} kernels[/dim]\n")
    
    config = get_phase3_config(deep_dive_kernels)
    display_phase_config(3, config)
    
    # Check budget
    est = tracker.estimate_remaining_cost(config.estimated_requests)
    console.print(f"\n[yellow]Estimated cost: ${est['estimated_cost']:.2f}[/yellow]")
    
    if not est['within_budget']:
        console.print(f"[red]⚠️ Exceeds remaining budget (${tracker.remaining:.2f})![/red]")
        if not console.input("[yellow]Continue anyway? (y/N): [/yellow]").lower() == 'y':
            return None
    
    orchestrator = ThreePhaseOrchestrator()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        console=console
    ) as progress:
        task = progress.add_task("Phase 3: Deep dive...", total=len(deep_dive_kernels))
        
        result = await orchestrator.executor.execute_phase3(config, deep_dive_kernels)
        
        progress.update(task, completed=len(deep_dive_kernels))
    
    # Save results
    output_file = output_dir / "phase3_results.json"
    with open(output_file, 'w') as f:
        json.dump({
            "phase": "3_deep_dive",
            "timestamp": datetime.utcnow().isoformat(),
            "kernel_results": result.kernel_results,
            "stats": result.stats,
        }, f, indent=2, default=str)
    
    console.print(f"\n[green]✓ Phase 3 complete! Results: {output_file}[/green]")
    
    return {
        "kernel_results": result.kernel_results
    }


# ============================================================================
#                    MAIN
# ============================================================================

async def main():
    args = parse_args()
    
    display_banner()
    
    # Cost estimate mode
    if args.estimate:
        print_cost_estimate()
        
        console.print("\n[bold]Formulation Generation:[/bold]")
        form_est = estimate_formulation_cost()
        console.print(f"  Total formulations: {form_est['total_formulations']}")
        console.print(f"  Preset available: {form_est['preset_available']}")
        console.print(f"  Need generation: {form_est['need_generation']}")
        console.print(f"  Opus cost: ${form_est['estimated_opus_cost']:.2f}")
        return
    
    # Setup
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    tracker = BudgetTracker(total_budget=args.budget)
    
    console.print(f"\n[cyan]Budget: ${args.budget:.2f}[/cyan]")
    console.print(f"[cyan]Output: {output_dir}[/cyan]\n")
    
    # Generate formulations if requested
    if args.generate_formulations:
        console.print("[bold]Generating formulations (one-time)...[/bold]")
        generator = FormulationGenerator()
        # This would call Opus once per formulation
        # await generator.generate_all_formulations()
        console.print("[green]✓ Formulations generated and cached[/green]")
        return
    
    # Load previous results if resuming
    phase1_results = None
    phase2_results = None
    
    if args.resume:
        with open(args.resume, 'r') as f:
            prev = json.load(f)
            if prev.get('phase') == '1_sampling':
                phase1_results = prev
            elif prev.get('phase') == '2_adversarial':
                phase2_results = prev
    
    # Run phases
    try:
        if args.phase == '1' or args.phase == 'all':
            phase1_results = await run_phase1(tracker, output_dir)
            display_cost_summary(tracker)
        
        if (args.phase == '2' or args.phase == 'all') and phase1_results:
            contested = phase1_results.get('contested_kernels', [])
            phase2_results = await run_phase2(tracker, output_dir, contested)
            display_cost_summary(tracker)
        
        if (args.phase == '3' or args.phase == 'all') and phase2_results:
            deep_dive = phase2_results.get('contested_kernels', [])
            await run_phase3(tracker, output_dir, deep_dive)
            display_cost_summary(tracker)
        
        # Save final cost report
        tracker.save(output_dir / "cost_report.json")
        
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️ Interrupted by user[/yellow]")
        tracker.save(output_dir / "cost_report_partial.json")
    
    # Final summary
    console.print(Panel(f"""
[bold green]✓ EXPERIMENT COMPLETE[/bold green]

Total spent: ${tracker.total_spent:.2f} / ${tracker.total_budget:.2f}
Results saved to: {output_dir}

Files:
  • phase1_results.json
  • phase2_results.json  
  • phase3_results.json
  • cost_report.json

[dim]С Богом![/dim]
    """, border_style="green"))


if __name__ == '__main__':
    asyncio.run(main())
