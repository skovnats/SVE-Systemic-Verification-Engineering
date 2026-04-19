#!/usr/bin/env python3
"""
TIK Experiments - Smart Runner
===============================
С Богом!

Cost-optimized experiment runner:
1. FREE TIER (g4f) - массовые запросы
2. PAID TIER (OpenRouter) - fallback
3. ARBITER (Opus 4.5) - финальный арбитр, формулировки, переводы

Usage:
    python run_smart.py --help
    python run_smart.py --kernel 1 --test all
    python run_smart.py --kernels all --distributed
    python run_smart.py --stats  # Show cost statistics
"""

import argparse
import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.logging import RichHandler

from config import settings
from kernels import KERNELS, KERNEL_BY_ID, KernelCategory
from smart_providers import get_smart_manager, ProviderTier
from smart_tasks import (
    smart_query,
    arbiter_query,
    smart_trolley_test,
    smart_outcast_test,
    smart_component_score,
    smart_full_test,
    smart_batch_test,
    formulate_prompt,
    translate_text,
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
        description="TIK Experiments - Cost-Optimized Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Strategy:
  1. FREE (g4f)    - All initial queries (бесплатно)
  2. PAID          - Fallback when FREE fails
  3. ARBITER       - Opus 4.5 for arbitration only

Examples:
  # Test single kernel (Christ)
  python run_smart.py --kernel 1 --test all

  # Test transcendent kernels
  python run_smart.py --category transcendent

  # Distributed execution
  python run_smart.py --kernels all --distributed

  # Show cost statistics
  python run_smart.py --stats

С Богом!
        """
    )
    
    # Kernel selection
    kernel_group = parser.add_mutually_exclusive_group()
    kernel_group.add_argument('--kernel', '-k', type=int, help='Single kernel ID')
    kernel_group.add_argument('--kernels', type=str, help='Kernel IDs or "all"')
    kernel_group.add_argument('--category', '-c', type=str, help='Kernel category')
    
    # Test selection
    parser.add_argument('--test', '-t', type=str, default='all',
                       choices=['all', 'trolley', 'outcast', 'components'],
                       help='Test type')
    parser.add_argument('--tracks', type=int, default=6, choices=[6, 8, 10],
                       help='Trolley tracks')
    
    # Provider control
    parser.add_argument('--free-only', action='store_true',
                       help='Only use FREE providers (no fallback)')
    parser.add_argument('--no-arbiter', action='store_true',
                       help='Disable Opus 4.5 arbiter')
    parser.add_argument('--samples', '-n', type=int, default=3,
                       help='Number of FREE samples per test')
    
    # Execution
    parser.add_argument('--distributed', '-d', action='store_true',
                       help='Use Celery for distributed execution')
    
    # Output
    parser.add_argument('--output', '-o', type=str, default='results',
                       help='Output directory')
    parser.add_argument('--format', '-f', type=str, default='json',
                       choices=['json', 'csv', 'latex'], help='Output format')
    
    # Utilities
    parser.add_argument('--stats', action='store_true',
                       help='Show cost statistics')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    
    return parser.parse_args()


# ============================================================================
#                    RUNNERS
# ============================================================================

async def run_single_test(
    kernel_id: int,
    test_type: str,
    num_samples: int = 3,
    use_arbiter: bool = True,
    tracks: int = 6
) -> dict:
    """Run a single test on one kernel."""
    
    kernel = KERNEL_BY_ID.get(kernel_id)
    if not kernel:
        return {'error': f'Kernel {kernel_id} not found'}
    
    console.print(f"\n[bold blue]Testing: {kernel.name}[/bold blue]")
    console.print(f"Test: {test_type}, Samples: {num_samples}, Arbiter: {use_arbiter}")
    
    if test_type == 'trolley':
        result = smart_trolley_test(kernel_id, tracks, num_samples, use_arbiter)
    elif test_type == 'outcast':
        result = smart_outcast_test(kernel_id, "universal", num_samples, use_arbiter)
    elif test_type == 'all':
        result = smart_full_test(kernel_id, num_samples, use_arbiter)
    else:
        result = {'error': f'Unknown test type: {test_type}'}
    
    return result


async def run_batch_local(
    kernel_ids: List[int],
    test_type: str,
    num_samples: int,
    use_arbiter: bool
) -> List[dict]:
    """Run batch tests locally (sequential)."""
    
    results = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task(f"Testing {len(kernel_ids)} kernels...", total=len(kernel_ids))
        
        for kernel_id in kernel_ids:
            result = await run_single_test(kernel_id, test_type, num_samples, use_arbiter)
            results.append(result)
            progress.advance(task)
    
    return results


def run_batch_distributed(
    kernel_ids: List[int],
    num_samples: int,
    use_arbiter: bool
) -> str:
    """Submit batch to Celery workers."""
    
    console.print(f"\n[yellow]Submitting {len(kernel_ids)} kernels to Celery workers...[/yellow]")
    
    group_id = smart_batch_test(kernel_ids, num_samples, use_arbiter)
    
    console.print(f"\n[green]Submitted! Group ID: {group_id}[/green]")
    console.print("Monitor: celery -A smart_tasks flower")
    console.print(f"Results: celery -A smart_tasks result {group_id}")
    
    return group_id


# ============================================================================
#                    OUTPUT
# ============================================================================

def display_results(results: List[dict]):
    """Display results in a table."""
    
    table = Table(title="TIK Results (FREE-FIRST Strategy)")
    
    table.add_column("Kernel", style="cyan")
    table.add_column("TIK₈", style="green")
    table.add_column("λ", style="yellow")
    table.add_column("Survives?", style="magenta")
    table.add_column("Track 7?", style="blue")
    table.add_column("Saves Hitler?", style="red")
    table.add_column("Arbiter Used", style="dim")
    
    for r in results:
        if 'error' in r:
            table.add_row(str(r.get('kernel_id', '?')), "ERROR", "-", "-", "-", "-", "-")
            continue
        
        tik = r.get('tik_scores', {})
        trolley = r.get('trolley', [{}])[0] if r.get('trolley') else {}
        outcast = r.get('outcast', {}).get('universal', {})
        
        arbiter_used = trolley.get('arbiter_used', False) or outcast.get('arbiter_used', False)
        
        table.add_row(
            r.get('kernel_name', 'Unknown'),
            f"{tik.get('TIK_8', 0):.3f}",
            f"{tik.get('lambda', 0):.3f}",
            "✓" if tik.get('survives_10_gen') else "✗",
            "✓" if trolley.get('is_self_sacrifice') else "✗",
            "✓" if outcast.get('saves_outcast') else "✗",
            "✓" if arbiter_used else "✗"
        )
    
    console.print(table)


def display_cost_stats(results: List[dict]):
    """Display cost statistics."""
    
    # Aggregate stats from all results
    total_free = 0
    total_paid = 0
    total_arbiter = 0
    
    for r in results:
        stats = r.get('cost_stats', {})
        total_free += stats.get('free_requests', 0)
        total_paid += stats.get('paid_requests', 0)
        total_arbiter += stats.get('arbiter_requests', 0)
    
    total = total_free + total_paid + total_arbiter
    
    panel_content = f"""
[bold green]FREE (g4f):[/bold green] {total_free} requests ({total_free/total*100:.1f}%)
[bold yellow]PAID (OpenRouter):[/bold yellow] {total_paid} requests ({total_paid/total*100:.1f}%)
[bold red]ARBITER (Opus 4.5):[/bold red] {total_arbiter} requests ({total_arbiter/total*100:.1f}%)

[bold]Total requests:[/bold] {total}
[bold]Estimated cost:[/bold] ${total_paid * 0.01 + total_arbiter * 0.05:.2f}
[bold]Savings vs all-paid:[/bold] ${total_free * 0.01:.2f}
    """
    
    console.print(Panel(panel_content, title="💰 Cost Statistics", border_style="green"))


def save_results(results: List[dict], output_dir: str, fmt: str):
    """Save results to file."""
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if fmt == 'json':
        filepath = output_path / f"tik_results_{timestamp}.json"
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2, default=str)
    
    elif fmt == 'csv':
        import pandas as pd
        filepath = output_path / f"tik_results_{timestamp}.csv"
        
        rows = []
        for r in results:
            if 'tik_scores' in r:
                row = {
                    'kernel_id': r.get('kernel_id'),
                    'kernel_name': r.get('kernel_name'),
                    **r['tik_scores']
                }
                rows.append(row)
        
        df = pd.DataFrame(rows)
        df.to_csv(filepath, index=False)
    
    elif fmt == 'latex':
        filepath = output_path / f"tik_results_{timestamp}.tex"
        
        rows = []
        for r in results:
            if 'tik_scores' in r:
                tik = r['tik_scores']
                rows.append(
                    f"{r.get('kernel_name', '')} & "
                    f"{tik.get('TIK_8', 0):.3f} & "
                    f"{tik.get('lambda', 0):.3f} & "
                    f"{'Yes' if tik.get('survives_10_gen') else 'No'} \\\\"
                )
        
        latex = f"""
\\begin{{table}}[H]
\\centering
\\caption{{TIK Results (FREE-FIRST Strategy) - {timestamp}}}
\\begin{{tabular}}{{@{{}}lccc@{{}}}}
\\toprule
\\textbf{{Kernel}} & \\textbf{{TIK$_8$}} & \\textbf{{$\\lambda$}} & \\textbf{{Survives?}} \\\\
\\midrule
{chr(10).join(rows)}
\\bottomrule
\\end{{tabular}}
\\end{{table}}
"""
        with open(filepath, 'w') as f:
            f.write(latex)
    
    console.print(f"\n[green]Results saved: {filepath}[/green]")


# ============================================================================
#                    MAIN
# ============================================================================

async def main():
    args = parse_args()
    
    # Banner
    console.print(Panel("""
[bold blue]TIK EXPERIMENTS - Smart Runner[/bold blue]

[green]FREE-FIRST Strategy:[/green]
  1. g4f (бесплатно) → 2. OpenRouter (платно) → 3. Opus 4.5 (арбитр)

[yellow]"Attention is ALL you need"[/yellow] → [red]"HS ≠ HR"[/red]

[dim]С Богом![/dim]
    """, border_style="blue"))
    
    # Just show stats?
    if args.stats:
        manager = get_smart_manager()
        stats = manager.get_stats()
        console.print(Panel(
            f"FREE: {stats['free_requests']}\n"
            f"PAID: {stats['paid_requests']}\n"
            f"ARBITER: {stats['arbiter_requests']}\n"
            f"Est. cost: ${stats['estimated_cost_usd']:.2f}",
            title="Current Session Stats"
        ))
        return
    
    # Determine kernels
    kernel_ids = []
    
    if args.kernel:
        kernel_ids = [args.kernel]
    elif args.kernels:
        if args.kernels.lower() == 'all':
            kernel_ids = list(KERNEL_BY_ID.keys())
        else:
            kernel_ids = [int(k.strip()) for k in args.kernels.split(',')]
    elif args.category:
        category = KernelCategory(args.category)
        kernel_ids = [k.id for k in KERNELS if k.category == category]
    else:
        kernel_ids = [1]  # Default: Christ
    
    console.print(f"[cyan]Kernels: {len(kernel_ids)}[/cyan]")
    console.print(f"[cyan]Test: {args.test}[/cyan]")
    console.print(f"[cyan]Samples: {args.samples}[/cyan]")
    console.print(f"[cyan]Arbiter: {not args.no_arbiter}[/cyan]")
    
    # Run
    if args.distributed:
        group_id = run_batch_distributed(
            kernel_ids, 
            args.samples, 
            not args.no_arbiter
        )
        return
    
    # Local execution
    results = await run_batch_local(
        kernel_ids,
        args.test,
        args.samples,
        not args.no_arbiter
    )
    
    # Output
    if results:
        display_results(results)
        display_cost_stats(results)
        save_results(results, args.output, args.format)
    
    console.print("\n[bold green]✓ Complete! С Богом![/bold green]")


if __name__ == '__main__':
    asyncio.run(main())
