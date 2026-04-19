"""
TIK Experiments - Cost Estimator & Budget Tracker
==================================================
С Богом!

Track experiment costs in real-time.
Alert when approaching budget limits.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
import json
import logging

logger = logging.getLogger(__name__)


# ============================================================================
#                    COST CONFIGURATION
# ============================================================================

@dataclass
class ModelCost:
    """Cost per request for a model."""
    model: str
    cost_per_1k_input: float
    cost_per_1k_output: float
    avg_input_tokens: int = 500
    avg_output_tokens: int = 300
    
    @property
    def avg_cost_per_request(self) -> float:
        """Estimated cost per request."""
        input_cost = (self.avg_input_tokens / 1000) * self.cost_per_1k_input
        output_cost = (self.avg_output_tokens / 1000) * self.cost_per_1k_output
        return input_cost + output_cost


# Cost data (January 2026 estimates)
MODEL_COSTS = {
    # Anthropic via OpenRouter
    "anthropic/claude-opus-4": ModelCost(
        model="claude-opus-4",
        cost_per_1k_input=0.015,
        cost_per_1k_output=0.075,
        avg_input_tokens=800,
        avg_output_tokens=400
    ),
    "anthropic/claude-sonnet-4": ModelCost(
        model="claude-sonnet-4",
        cost_per_1k_input=0.003,
        cost_per_1k_output=0.015,
    ),
    
    # OpenAI via OpenRouter
    "openai/gpt-4-turbo": ModelCost(
        model="gpt-4-turbo",
        cost_per_1k_input=0.01,
        cost_per_1k_output=0.03,
    ),
    "openai/gpt-4o": ModelCost(
        model="gpt-4o",
        cost_per_1k_input=0.005,
        cost_per_1k_output=0.015,
    ),
    
    # Google via OpenRouter
    "google/gemini-pro-1.5": ModelCost(
        model="gemini-pro-1.5",
        cost_per_1k_input=0.00125,
        cost_per_1k_output=0.005,
    ),
    
    # Open source (cheap/free)
    "meta-llama/llama-3.1-70b-instruct": ModelCost(
        model="llama-3.1-70b",
        cost_per_1k_input=0.0008,
        cost_per_1k_output=0.0008,
    ),
    "mistralai/mistral-large": ModelCost(
        model="mistral-large",
        cost_per_1k_input=0.004,
        cost_per_1k_output=0.012,
    ),
    
    # g4f FREE
    "g4f/gpt-4": ModelCost(
        model="g4f-gpt4",
        cost_per_1k_input=0.0,
        cost_per_1k_output=0.0,
    ),
    "g4f/llama-70b": ModelCost(
        model="g4f-llama",
        cost_per_1k_input=0.0,
        cost_per_1k_output=0.0,
    ),
}


# ============================================================================
#                    BUDGET TRACKER
# ============================================================================

@dataclass
class BudgetAlert:
    """Budget alert configuration."""
    threshold_percent: float
    message: str
    triggered: bool = False


@dataclass
class CostRecord:
    """Record of a single cost event."""
    timestamp: datetime
    model: str
    tier: str  # free, paid, arbiter
    input_tokens: int
    output_tokens: int
    cost: float
    phase: str
    kernel_id: Optional[int] = None


class BudgetTracker:
    """
    Real-time budget tracking for experiments.
    """
    
    def __init__(self, total_budget: float = 3000.0):
        self.total_budget = total_budget
        self.records: List[CostRecord] = []
        
        # Alerts
        self.alerts = [
            BudgetAlert(25, "⚠️ 25% of budget used"),
            BudgetAlert(50, "⚠️ 50% of budget used"),
            BudgetAlert(75, "🚨 75% of budget used - consider pausing"),
            BudgetAlert(90, "🛑 90% of budget used - STOP recommended"),
        ]
        
        # Per-tier tracking
        self.tier_costs = {
            "free": 0.0,
            "paid": 0.0,
            "arbiter": 0.0,
        }
        
        # Per-phase tracking
        self.phase_costs = {
            "phase_1_sampling": 0.0,
            "phase_2_adversarial": 0.0,
            "phase_3_deep_dive": 0.0,
            "formulation_generation": 0.0,
        }
    
    def record(
        self,
        model: str,
        tier: str,
        input_tokens: int,
        output_tokens: int,
        phase: str,
        kernel_id: Optional[int] = None
    ) -> CostRecord:
        """Record a cost event."""
        
        # Get cost
        model_cost = MODEL_COSTS.get(model)
        if model_cost:
            cost = (
                (input_tokens / 1000) * model_cost.cost_per_1k_input +
                (output_tokens / 1000) * model_cost.cost_per_1k_output
            )
        else:
            # Default estimate for unknown models
            cost = 0.01 if tier != "free" else 0.0
        
        record = CostRecord(
            timestamp=datetime.utcnow(),
            model=model,
            tier=tier,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost,
            phase=phase,
            kernel_id=kernel_id
        )
        
        self.records.append(record)
        self.tier_costs[tier] = self.tier_costs.get(tier, 0) + cost
        self.phase_costs[phase] = self.phase_costs.get(phase, 0) + cost
        
        # Check alerts
        self._check_alerts()
        
        return record
    
    def _check_alerts(self):
        """Check and trigger budget alerts."""
        spent = self.total_spent
        percent = (spent / self.total_budget) * 100
        
        for alert in self.alerts:
            if percent >= alert.threshold_percent and not alert.triggered:
                alert.triggered = True
                logger.warning(f"{alert.message} (${spent:.2f} / ${self.total_budget:.2f})")
    
    @property
    def total_spent(self) -> float:
        """Total amount spent."""
        return sum(self.tier_costs.values())
    
    @property
    def remaining(self) -> float:
        """Remaining budget."""
        return self.total_budget - self.total_spent
    
    @property
    def percent_used(self) -> float:
        """Percentage of budget used."""
        return (self.total_spent / self.total_budget) * 100
    
    def get_summary(self) -> Dict:
        """Get budget summary."""
        return {
            "total_budget": self.total_budget,
            "total_spent": self.total_spent,
            "remaining": self.remaining,
            "percent_used": self.percent_used,
            "by_tier": self.tier_costs.copy(),
            "by_phase": self.phase_costs.copy(),
            "total_requests": len(self.records),
            "free_requests": sum(1 for r in self.records if r.tier == "free"),
            "paid_requests": sum(1 for r in self.records if r.tier == "paid"),
            "arbiter_requests": sum(1 for r in self.records if r.tier == "arbiter"),
        }
    
    def estimate_remaining_cost(
        self,
        remaining_requests: int,
        free_rate: float = 0.80,
        paid_rate: float = 0.17,
        arbiter_rate: float = 0.03
    ) -> Dict:
        """Estimate cost for remaining requests."""
        
        free_req = int(remaining_requests * free_rate)
        paid_req = int(remaining_requests * paid_rate)
        arbiter_req = int(remaining_requests * arbiter_rate)
        
        # Average costs
        avg_paid = 0.01  # ~$0.01 per paid request
        avg_arbiter = 0.05  # ~$0.05 per Opus request
        
        estimated_cost = (paid_req * avg_paid) + (arbiter_req * avg_arbiter)
        
        return {
            "remaining_requests": remaining_requests,
            "estimated_free": free_req,
            "estimated_paid": paid_req,
            "estimated_arbiter": arbiter_req,
            "estimated_cost": estimated_cost,
            "total_projected": self.total_spent + estimated_cost,
            "within_budget": (self.total_spent + estimated_cost) <= self.total_budget
        }
    
    def save(self, filepath: str):
        """Save records to file."""
        data = {
            "summary": self.get_summary(),
            "records": [
                {
                    "timestamp": r.timestamp.isoformat(),
                    "model": r.model,
                    "tier": r.tier,
                    "cost": r.cost,
                    "phase": r.phase,
                    "kernel_id": r.kernel_id
                }
                for r in self.records
            ]
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load(self, filepath: str):
        """Load records from file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        self.tier_costs = data["summary"]["by_tier"]
        self.phase_costs = data["summary"]["by_phase"]
        # Records could be reconstructed if needed


# ============================================================================
#                    EXPERIMENT COST ESTIMATOR
# ============================================================================

def estimate_experiment_cost() -> Dict:
    """
    Estimate total experiment cost with three-phase approach.
    """
    
    # Phase 1: Sampling
    phase1_kernels = 99
    phase1_models = 10
    phase1_languages = 3
    phase1_formulations = 3
    phase1_variants = 1
    phase1_evaluators = 5
    
    phase1_base = phase1_kernels * phase1_models * phase1_languages * phase1_formulations * phase1_variants
    phase1_eval = phase1_base * phase1_evaluators
    phase1_total = phase1_base + phase1_eval
    
    # Phase 2: Adversarial (estimated 20 contested kernels)
    phase2_kernels = 20
    phase2_models = 10
    phase2_quantizations = 2
    phase2_languages = 3
    phase2_formulations = 3
    phase2_variants = 4  # base + angel + demon + friend
    phase2_evaluators = 5
    
    phase2_base = phase2_kernels * phase2_models * phase2_quantizations * phase2_languages * phase2_formulations * phase2_variants
    phase2_eval = phase2_base * phase2_evaluators
    phase2_total = phase2_base + phase2_eval
    
    # Phase 3: Deep dive (estimated 10 contested kernels)
    phase3_kernels = 10
    phase3_models = 50
    phase3_quantizations = 3
    phase3_languages = 9
    phase3_formulations = 9
    phase3_variants = 4
    phase3_evaluators = 10
    
    phase3_base = phase3_kernels * phase3_models * phase3_quantizations * phase3_languages * phase3_formulations * phase3_variants
    phase3_eval = phase3_base * phase3_evaluators
    phase3_total = phase3_base + phase3_eval
    
    # Formulation generation (one-time)
    questions = 4  # trolley_6, outcast_universal, outcast_kernel, stress
    languages = 9
    formulations = 9
    formulation_opus_calls = questions * languages * formulations  # ~324
    
    # Cost estimation (with hierarchical arbitration)
    # FREE: 80%, PAID: 17%, ARBITER: 3%
    
    total_requests = phase1_total + phase2_total + phase3_total
    
    free_requests = int(total_requests * 0.80)
    paid_requests = int(total_requests * 0.17)
    arbiter_requests = int(total_requests * 0.03)
    
    free_cost = 0
    paid_cost = paid_requests * 0.01  # ~$0.01 average
    arbiter_cost = arbiter_requests * 0.05  # ~$0.05 per Opus
    formulation_cost = formulation_opus_calls * 0.05  # One-time
    
    total_cost = free_cost + paid_cost + arbiter_cost + formulation_cost
    
    return {
        "phases": {
            "phase_1": {
                "requests": phase1_total,
                "base": phase1_base,
                "eval": phase1_eval,
            },
            "phase_2": {
                "requests": phase2_total,
                "base": phase2_base,
                "eval": phase2_eval,
            },
            "phase_3": {
                "requests": phase3_total,
                "base": phase3_base,
                "eval": phase3_eval,
            },
        },
        "totals": {
            "total_requests": total_requests,
            "free_requests": free_requests,
            "paid_requests": paid_requests,
            "arbiter_requests": arbiter_requests,
        },
        "costs": {
            "free_cost": free_cost,
            "paid_cost": paid_cost,
            "arbiter_cost": arbiter_cost,
            "formulation_cost": formulation_cost,
            "total_cost": total_cost,
        },
        "comparison": {
            "all_paid_cost": total_requests * 0.01,
            "all_opus_cost": total_requests * 0.05,
            "savings_vs_all_paid": (total_requests * 0.01) - total_cost,
            "savings_vs_all_opus": (total_requests * 0.05) - total_cost,
        },
        "recommendations": {
            "budget": 3000,
            "buffer": 500,
            "total_recommended": 3500,
        }
    }


def print_cost_estimate():
    """Print formatted cost estimate."""
    est = estimate_experiment_cost()
    
    print("=" * 60)
    print("TIK EXPERIMENT COST ESTIMATE")
    print("С Богом!")
    print("=" * 60)
    
    print("\n📊 REQUESTS BY PHASE:")
    for phase, data in est["phases"].items():
        print(f"  {phase}: {data['requests']:,} ({data['base']:,} base + {data['eval']:,} eval)")
    
    print(f"\n  TOTAL: {est['totals']['total_requests']:,} requests")
    
    print("\n📈 REQUEST DISTRIBUTION (with hierarchical arbitration):")
    print(f"  FREE (g4f):   {est['totals']['free_requests']:,} (80%)")
    print(f"  PAID:         {est['totals']['paid_requests']:,} (17%)")
    print(f"  ARBITER:      {est['totals']['arbiter_requests']:,} (3%)")
    
    print("\n💰 ESTIMATED COSTS:")
    print(f"  FREE:         ${est['costs']['free_cost']:.2f}")
    print(f"  PAID:         ${est['costs']['paid_cost']:.2f}")
    print(f"  ARBITER:      ${est['costs']['arbiter_cost']:.2f}")
    print(f"  Formulations: ${est['costs']['formulation_cost']:.2f} (one-time)")
    print(f"  ─────────────────────")
    print(f"  TOTAL:        ${est['costs']['total_cost']:.2f}")
    
    print("\n📉 SAVINGS:")
    print(f"  vs all PAID:  ${est['comparison']['savings_vs_all_paid']:.2f}")
    print(f"  vs all OPUS:  ${est['comparison']['savings_vs_all_opus']:.2f}")
    
    print("\n💡 RECOMMENDATION:")
    print(f"  Budget:       ${est['recommendations']['budget']}")
    print(f"  Buffer:       ${est['recommendations']['buffer']}")
    print(f"  Total:        ${est['recommendations']['total_recommended']}")
    
    print("=" * 60)


# ============================================================================
#                    EXPORTS
# ============================================================================

__all__ = [
    "ModelCost",
    "MODEL_COSTS",
    "CostRecord",
    "BudgetTracker",
    "estimate_experiment_cost",
    "print_cost_estimate",
]


if __name__ == "__main__":
    print_cost_estimate()
