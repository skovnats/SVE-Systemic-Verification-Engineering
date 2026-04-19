#!/usr/bin/env python3
"""
TIK Experiments - Main Runner
==============================
С Богом!

Main script for running TIK experiments.

Usage:
    python run_experiments.py --help
    python run_experiments.py --kernels all --models claude
    python run_experiments.py --kernel 1 --test trolley
    python run_experiments.py --distributed --workers 4
"""

import argparse
import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional
import pandas as pd
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.logging import RichHandler

from config import settings, ModelConfig
from kernels import KERNELS, KERNEL_BY_ID, KernelCategory
from providers import (
    get_provider_manager,
    LLMConfig,
    LLMProvider,
    get_verification_configs,
    get_model_comparison_configs
)
from prompts import build_trolley_prompt, build_outcast_universal_prompt
from tik_metrics import TIKCalculator, TIKScore
from tasks import (
    test_kernel_full,
    test_kernel_trolley,
    test_kernel_outcast,
    test_all_kernels,
    verification_workflow
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)]
)
logger = logging.getLogger(__name__)
console = Console()


# ============================================================================
#                    CLI ARGUMENTS
# ============================================================================

def parse_args():
    parser = argparse.ArgumentParser(
        description="TIK Experiments - Test ethical kernels",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test single kernel
  python run_experiments.py --kernel 1 --test trolley

  # Test all transcendent kernels
  python run_experiments.py --category transcendent --test all

  # Run full experiment on all 99 kernels (distributed)
  python run_experiments.py --kernels all --distributed

  # Compare multiple models on kernel #1 (Christ)
  python run_experiments.py --kernel 1 --model-comparison

С Богом!
        """
    )
    
    # Kernel selection
    kernel_group = parser.add_mutually_exclusive_group()
    kernel_group.add_argument(
        '--kernel', '-k',
        type=int,
        help='Single kernel ID (1-99)'
    )
    kernel_group.add_argument(
        '--kernels',
        type=str,
        help='Comma-separated kernel IDs or "all"'
    )
    kernel_group.add_argument(
        '--category', '-c',
        type=str,
        choices=['transcendent', 'religious', 'philosophical', 
                 'political_economic', 'identity_social', 
                 'consumption_pleasure', 'techno_science'],
        help='Test all kernels in category'
    )
    
    # Test selection
    parser.add_argument(
        '--test', '-t',
        type=str,
        default='all',
        choices=['all', 'trolley', 'outcast', 'stress', 'components'],
        help='Type of test to run'
    )
    
    parser.add_argument(
        '--tracks',
        type=int,
        default=6,
        choices=[6, 8, 10],
        help='Number of tracks for trolley problem'
    )
    
    # Model configuration
    parser.add_argument(
        '--model', '-m',
        type=str,
        default='anthropic/claude-3.5-sonnet',
        help='Model to use (OpenRouter format)'
    )
    
    parser.add_argument(
        '--temperature', '-T',
        type=float,
        default=0.5,
        help='Temperature for LLM'
    )
    
    parser.add_argument(
        '--model-comparison',
        action='store_true',
        help='Compare multiple models'
    )
    
    parser.add_argument(
        '--temperature-sweep',
        action='store_true',
        help='Test across multiple temperatures'
    )
    
    # Verification
    parser.add_argument(
        '--verify',
        action='store_true',
        help='Use triple verification (3 independent models)'
    )
    
    parser.add_argument(
        '--runs', '-r',
        type=int,
        default=1,
        help='Number of runs per configuration'
    )
    
    # Distributed execution
    parser.add_argument(
        '--distributed', '-d',
        action='store_true',
        help='Use Celery for distributed execution'
    )
    
    parser.add_argument(
        '--workers', '-w',
        type=int,
        default=4,
        help='Number of Celery workers (if starting locally)'
    )
    
    # Output
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='results',
        help='Output directory'
    )
    
    parser.add_argument(
        '--format', '-f',
        type=str,
        default='json',
        choices=['json', 'csv', 'latex'],
        help='Output format'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    
    return parser.parse_args()


# ============================================================================
#                    EXPERIMENT RUNNERS
# ============================================================================

async def run_single_kernel_test(
    kernel_id: int,
    test_type: str,
    model: str,
    temperature: float,
    tracks: int = 6,
    verify: bool = False
) -> dict:
    """Run a single test on a single kernel."""
    
    kernel = KERNEL_BY_ID.get(kernel_id)
    if not kernel:
        return {'error': f'Kernel {kernel_id} not found'}
    
    console.print(f"\n[bold blue]Testing: {kernel.name}[/bold blue]")
    console.print(f"Test type: {test_type}, Model: {model}, Temp: {temperature}")
    
    pm = get_provider_manager()
    config = LLMConfig(
        model=model,
        temperature=temperature,
        system_prompt=kernel.system_prompt
    )
    
    # Build prompt based on test type
    if test_type == 'trolley':
        prompt = build_trolley_prompt(kernel, tracks)
    elif test_type == 'outcast':
        prompt = build_outcast_universal_prompt(kernel)
    else:
        return {'error': f'Unknown test type: {test_type}'}
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Querying LLM...", total=None)
        
        response = await pm.complete_with_fallback(prompt, [config])
        
        progress.update(task, completed=True)
    
    if response.success:
        console.print(f"\n[green]Response received ({response.latency_ms:.0f}ms)[/green]")
        console.print(f"\n{response.content[:500]}...")
    else:
        console.print(f"\n[red]Error: {response.error}[/red]")
    
    return {
        'kernel_id': kernel_id,
        'kernel_name': kernel.name,
        'test_type': test_type,
        'model': model,
        'temperature': temperature,
        'response': response.content,
        'success': response.success,
        'error': response.error,
        'latency_ms': response.latency_ms
    }


async def run_full_kernel_test(
    kernel_id: int,
    models: List[str],
    temperatures: List[float]
) -> dict:
    """Run full test suite on a kernel."""
    
    kernel = KERNEL_BY_ID.get(kernel_id)
    if not kernel:
        return {'error': f'Kernel {kernel_id} not found'}
    
    console.print(f"\n[bold blue]Full test suite: {kernel.name}[/bold blue]")
    
    # Use Celery task (synchronous call)
    result = test_kernel_full(kernel_id, models, temperatures)
    
    return result


def run_distributed_experiment(
    kernel_ids: List[int],
    models: List[str],
    temperatures: List[float]
) -> str:
    """Run experiment distributed across Celery workers."""
    
    console.print(f"\n[bold yellow]Starting distributed experiment[/bold yellow]")
    console.print(f"Kernels: {len(kernel_ids)}, Models: {len(models)}, Temps: {len(temperatures)}")
    
    # Submit to Celery
    group_id = test_all_kernels(kernel_ids, models, temperatures)
    
    console.print(f"\n[green]Submitted! Task group ID: {group_id}[/green]")
    console.print("Monitor with: celery -A tasks flower")
    
    return group_id


# ============================================================================
#                    OUTPUT FORMATTERS
# ============================================================================

def display_results_table(results: List[dict]):
    """Display results in a rich table."""
    
    table = Table(title="TIK Experiment Results")
    
    table.add_column("Kernel", style="cyan")
    table.add_column("TIK_8", style="green")
    table.add_column("λ (decay)", style="yellow")
    table.add_column("Survives?", style="magenta")
    table.add_column("Track 7?", style="blue")
    table.add_column("Saves Hitler?", style="red")
    
    for r in results:
        if 'tik_score' in r and r['tik_score']:
            tik = r['tik_score']
            table.add_row(
                r.get('kernel_name', 'Unknown'),
                f"{tik.get('TIK_8', 0):.3f}",
                f"{tik.get('lambda_decay', 0):.3f}",
                "✓" if tik.get('survives_10_gen') else "✗",
                "✓" if tik.get('S', 0) > 0.8 else "✗",
                "✓" if tik.get('O1', 0) > 0.5 else "✗"
            )
    
    console.print(table)


def save_results(results: List[dict], output_dir: str, format: str):
    """Save results to file."""
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if format == 'json':
        filepath = output_path / f"tik_results_{timestamp}.json"
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2, default=str)
    
    elif format == 'csv':
        filepath = output_path / f"tik_results_{timestamp}.csv"
        # Flatten results for CSV
        rows = []
        for r in results:
            if 'tik_score' in r and r['tik_score']:
                row = {
                    'kernel_id': r.get('kernel_id'),
                    'kernel_name': r.get('kernel_name'),
                    **r['tik_score']
                }
                rows.append(row)
        df = pd.DataFrame(rows)
        df.to_csv(filepath, index=False)
    
    elif format == 'latex':
        filepath = output_path / f"tik_results_{timestamp}.tex"
        # Generate LaTeX table
        rows = []
        for r in results:
            if 'tik_score' in r and r['tik_score']:
                tik = r['tik_score']
                rows.append(
                    f"{r.get('kernel_name', '')} & "
                    f"{tik.get('TIK_8', 0):.3f} & "
                    f"{tik.get('lambda_decay', 0):.3f} & "
                    f"{'Yes' if tik.get('survives_10_gen') else 'No'} \\\\"
                )
        
        latex = f"""
\\begin{{table}}[H]
\\centering
\\caption{{TIK Results - {timestamp}}}
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
    
    console.print(f"\n[green]Results saved to: {filepath}[/green]")


# ============================================================================
#                    MAIN
# ============================================================================

async def main():
    args = parse_args()
    
    # Banner
    console.print("""
[bold blue]
╔═══════════════════════════════════════════════════════════╗
║     TIK EXPERIMENTS - Testing 99 Ethical Kernels          ║
║                                                           ║
║     "Attention is ALL you need" → "HS ≠ HR"              ║
║                                                           ║
║                      С Богом!                             ║
╚═══════════════════════════════════════════════════════════╝
[/bold blue]
    """)
    
    # Determine kernel IDs
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
        # Default: test Christ (kernel 1)
        kernel_ids = [1]
    
    console.print(f"[cyan]Kernels to test: {len(kernel_ids)}[/cyan]")
    
    # Determine models and temperatures
    if args.model_comparison:
        models = [c.model for c in get_model_comparison_configs()]
    else:
        models = [args.model]
    
    if args.temperature_sweep:
        temperatures = ModelConfig.TEMPERATURES
    else:
        temperatures = [args.temperature]
    
    # Run experiments
    results = []
    
    if args.distributed:
        # Use Celery for distributed execution
        group_id = run_distributed_experiment(kernel_ids, models, temperatures)
        console.print(f"\n[yellow]Distributed job submitted: {group_id}[/yellow]")
        console.print("Check results with: celery -A tasks result <task_id>")
        return
    
    # Run locally
    for kernel_id in kernel_ids:
        if args.test == 'all':
            result = await run_full_kernel_test(kernel_id, models, temperatures)
        else:
            result = await run_single_kernel_test(
                kernel_id=kernel_id,
                test_type=args.test,
                model=args.model,
                temperature=args.temperature,
                tracks=args.tracks,
                verify=args.verify
            )
        
        results.append(result)
    
    # Display and save results
    if results:
        display_results_table(results)
        save_results(results, args.output, args.format)
    
    console.print("\n[bold green]Experiment complete! С Богом![/bold green]")


if __name__ == '__main__':
    asyncio.run(main())
