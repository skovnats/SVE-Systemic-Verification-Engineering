"""
TIK Experiments - Celery Tasks
===============================
С Богом!

Distributed task definitions for running experiments.
Uses Celery for distributed execution across workers.

ARCHITECTURE:
- FREE TIER tasks: Run on all workers using GPT4Free
- ARBITER tasks: Call Opus 4.5 only when needed

Cost optimization: 80-90% savings by using free tier for mass queries.
"""

import logging
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from celery import Celery, group, chain, chord

from config import settings
from kernels import KERNEL_BY_ID, EthicalKernel
from prompts import (
    build_trolley_prompt,
    build_outcast_universal_prompt,
    build_outcast_kernel_prompt,
    build_room_101_prompt,
    build_self_annihilation_prompt,
    build_vanishing_reward_prompt,
    build_pharisee_prompt,
    build_component_prompt,
    TestType
)
from providers import (
    get_provider_manager,
    LLMConfig,
    LLMProvider,
)
from arbiter import (
    get_arbiter,
    should_call_arbiter,
    ArbiterRole
)
from tik_metrics import (
    TIKCalculator,
    TIKScore,
    ResponseParser
)

logger = logging.getLogger(__name__)

# ============================================================================
#                    CELERY APP
# ============================================================================

app = Celery(
    'tik_experiments',
    broker=settings.celery_broker,
    backend=settings.celery_backend,
)

# Celery configuration
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes per task
    worker_prefetch_multiplier=1,  # Don't prefetch tasks
    task_acks_late=True,  # Ack after completion
    task_reject_on_worker_lost=True,
)


# ============================================================================
#                    BASIC TASKS
# ============================================================================

@app.task(bind=True, name='tik.llm_query')
def llm_query(
    self,
    prompt: str,
    model: str,
    temperature: float = 0.7,
    system_prompt: Optional[str] = None,
    provider: str = "openrouter"
) -> Dict:
    """
    Send a single LLM query.
    
    This is the atomic task - everything else builds on this.
    """
    import asyncio
    
    async def _query():
        pm = get_provider_manager()
        config = LLMConfig(
            model=model,
            temperature=temperature,
            system_prompt=system_prompt,
            provider=LLMProvider(provider) if provider else LLMProvider.OPENROUTER
        )
        
        response = await pm.complete_with_fallback(prompt, [config])
        return {
            'content': response.content,
            'model': response.model,
            'provider': response.provider,
            'temperature': response.temperature,
            'tokens_used': response.tokens_used,
            'latency_ms': response.latency_ms,
            'error': response.error,
            'success': response.success,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    return asyncio.run(_query())


# ============================================================================
#                    FREE TIER TASKS (GPT4Free)
# ============================================================================

@app.task(bind=True, name='tik.free_tier_query', queue='free_tier')
def free_tier_query(
    self,
    prompt: str,
    system_prompt: Optional[str] = None,
    provider: Optional[str] = None
) -> Dict:
    """
    Query using FREE tier (GPT4Free).
    
    Rotates through available free providers.
    Used for mass queries to minimize cost.
    """
    import asyncio
    
    # Free providers to try
    FREE_PROVIDERS = ['Bing', 'You', 'Phind', 'DeepInfra', 'Groq', 'FreeGpt']
    
    async def _free_query():
        try:
            import g4f
            
            # Select provider
            if provider:
                selected_provider = getattr(g4f.Provider, provider, None)
            else:
                # Random rotation for load balancing
                import random
                provider_name = random.choice(FREE_PROVIDERS)
                selected_provider = getattr(g4f.Provider, provider_name, None)
            
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            import time
            start = time.time()
            
            response = await g4f.ChatCompletion.create_async(
                model="gpt-3.5-turbo",
                messages=messages,
                provider=selected_provider
            )
            
            latency = (time.time() - start) * 1000
            
            content = response if isinstance(response, str) else str(response)
            
            return {
                'content': content,
                'provider': f'g4f:{provider or "auto"}',
                'model': 'gpt-3.5-turbo',
                'temperature': 0.7,
                'tokens_used': 0,
                'latency_ms': latency,
                'success': len(content) > 0,
                'error': None,
                'timestamp': datetime.utcnow().isoformat(),
                'tier': 'free'
            }
            
        except Exception as e:
            logger.error(f"Free tier query error: {e}")
            return {
                'content': '',
                'provider': f'g4f:{provider or "auto"}',
                'model': 'gpt-3.5-turbo',
                'temperature': 0.7,
                'tokens_used': 0,
                'latency_ms': 0,
                'success': False,
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat(),
                'tier': 'free'
            }
    
    return asyncio.run(_free_query())


@app.task(bind=True, name='tik.free_tier_multi_query', queue='free_tier')
def free_tier_multi_query(
    self,
    prompt: str,
    system_prompt: Optional[str] = None,
    num_queries: int = 3
) -> List[Dict]:
    """
    Query multiple free-tier providers for the same prompt.
    
    Used for initial data collection before potential arbitration.
    """
    FREE_PROVIDERS = ['Bing', 'You', 'Phind', 'DeepInfra', 'Groq']
    
    results = []
    import random
    providers_to_use = random.sample(FREE_PROVIDERS, min(num_queries, len(FREE_PROVIDERS)))
    
    for provider in providers_to_use:
        result = free_tier_query(prompt, system_prompt, provider)
        results.append(result)
    
    return results


# ============================================================================
#                    ARBITER TASKS (Opus 4.5)
# ============================================================================

@app.task(bind=True, name='tik.arbiter_resolve', queue='arbiter')
def arbiter_resolve(
    self,
    question: str,
    free_tier_responses: List[Dict],
    context: Optional[str] = None
) -> Dict:
    """
    Call Opus 4.5 to resolve disagreement between free-tier responses.
    
    COST: This uses paid API - call only when necessary!
    """
    import asyncio
    
    async def _arbitrate():
        arbiter = get_arbiter()
        response = await arbiter.arbitrate(question, free_tier_responses, context)
        
        return {
            'role': response.role.value,
            'content': response.content,
            'confidence': response.confidence,
            'reasoning': response.reasoning,
            'tokens_used': response.tokens_used,
            'latency_ms': response.latency_ms,
            'success': response.success,
            'error': response.error,
            'metadata': response.metadata,
            'tier': 'arbiter'
        }
    
    return asyncio.run(_arbitrate())


@app.task(bind=True, name='tik.arbiter_translate', queue='arbiter')
def arbiter_translate(
    self,
    text: str,
    source_lang: str = 'ru',
    target_lang: str = 'en',
    context: Optional[str] = None
) -> Dict:
    """
    Use Opus 4.5 for high-quality translation.
    """
    import asyncio
    
    async def _translate():
        arbiter = get_arbiter()
        response = await arbiter.translate(text, source_lang, target_lang, context)
        
        return {
            'role': response.role.value,
            'content': response.content,
            'confidence': response.confidence,
            'tokens_used': response.tokens_used,
            'success': response.success,
            'error': response.error,
            'tier': 'arbiter'
        }
    
    return asyncio.run(_translate())


@app.task(bind=True, name='tik.arbiter_synthesize', queue='arbiter')
def arbiter_synthesize(
    self,
    kernel_name: str,
    all_results: Dict[str, Any]
) -> Dict:
    """
    Use Opus 4.5 to compute final TIK score.
    
    This is the FINAL synthesis - called once per kernel.
    """
    import asyncio
    
    async def _synthesize():
        arbiter = get_arbiter()
        response = await arbiter.synthesize_tik_score(kernel_name, all_results)
        
        return {
            'role': response.role.value,
            'content': response.content,
            'confidence': response.confidence,
            'tokens_used': response.tokens_used,
            'success': response.success,
            'error': response.error,
            'tier': 'arbiter'
        }
    
    return asyncio.run(_synthesize())


# ============================================================================
#                    SMART QUERY (FREE + ARBITER)
# ============================================================================

@app.task(bind=True, name='tik.smart_query')
def smart_query(
    self,
    prompt: str,
    system_prompt: Optional[str] = None,
    context: Optional[str] = None,
    disagreement_threshold: float = 0.30
) -> Dict:
    """
    Smart query: Try free tier first, call arbiter only if disagreement.
    
    This is the MAIN entry point for cost-optimized queries.
    
    Flow:
    1. Query 3 free-tier providers
    2. Check for disagreement
    3. If disagreement > threshold → call Opus arbiter
    4. Return best result
    """
    # Step 1: Get free tier responses
    free_responses = free_tier_multi_query(prompt, system_prompt, num_queries=3)
    
    # Filter successful responses
    successful = [r for r in free_responses if r.get('success', False)]
    
    if not successful:
        # All free tier failed - fall back to arbiter
        logger.warning("All free tier queries failed, calling arbiter")
        return arbiter_resolve(prompt, free_responses, context)
    
    if len(successful) == 1:
        # Only one success - use it
        return successful[0]
    
    # Step 2: Check for disagreement
    if should_call_arbiter(successful, disagreement_threshold):
        logger.info("Disagreement detected, calling arbiter")
        arbiter_result = arbiter_resolve(prompt, successful, context)
        return arbiter_result
    
    # Step 3: No significant disagreement - return first successful
    return successful[0]


@app.task(bind=True, name='tik.test_kernel_component')
def test_kernel_component(
    self,
    kernel_id: int,
    component: str,
    model: str,
    temperature: float = 0.5
) -> Dict:
    """
    Test a single component (Q, E, I, S, T, M) for a kernel.
    """
    kernel = KERNEL_BY_ID.get(kernel_id)
    if not kernel:
        return {'error': f'Kernel {kernel_id} not found'}
    
    prompt = build_component_prompt(kernel, component)
    
    result = llm_query(
        prompt=prompt,
        model=model,
        temperature=temperature,
        system_prompt=kernel.system_prompt
    )
    
    # Parse response
    parser = ResponseParser()
    parsed = parser.parse_component_score(result.get('content', ''), component)
    
    return {
        'kernel_id': kernel_id,
        'kernel_name': kernel.name,
        'component': component,
        'score': parsed.score,
        'confidence': parsed.confidence,
        'evidence': parsed.evidence[:500],  # Truncate
        'model': model,
        'temperature': temperature,
        'raw_response': result
    }


@app.task(bind=True, name='tik.test_kernel_trolley')
def test_kernel_trolley(
    self,
    kernel_id: int,
    tracks: int = 6,
    model: str = "anthropic/claude-3.5-sonnet",
    temperature: float = 0.5
) -> Dict:
    """
    Run trolley problem test for a kernel.
    """
    kernel = KERNEL_BY_ID.get(kernel_id)
    if not kernel:
        return {'error': f'Kernel {kernel_id} not found'}
    
    prompt = build_trolley_prompt(kernel, tracks)
    
    result = llm_query(
        prompt=prompt,
        model=model,
        temperature=temperature,
        system_prompt=kernel.system_prompt
    )
    
    # Parse response
    parser = ResponseParser()
    parsed = parser.parse_trolley_response(result.get('content', ''))
    
    return {
        'kernel_id': kernel_id,
        'kernel_name': kernel.name,
        'test_type': f'trolley_{tracks}',
        'track_chosen': parsed.track_chosen,
        'is_self_sacrifice': parsed.is_self_sacrifice,
        'reasoning': parsed.reasoning[:1000],
        'confidence': parsed.confidence,
        'model': model,
        'temperature': temperature,
        'raw_response': result
    }


@app.task(bind=True, name='tik.test_kernel_outcast')
def test_kernel_outcast(
    self,
    kernel_id: int,
    test_type: str = "universal",  # "universal" or "kernel"
    model: str = "anthropic/claude-3.5-sonnet",
    temperature: float = 0.5
) -> Dict:
    """
    Run outcast test for a kernel.
    """
    kernel = KERNEL_BY_ID.get(kernel_id)
    if not kernel:
        return {'error': f'Kernel {kernel_id} not found'}
    
    if test_type == "universal":
        prompt = build_outcast_universal_prompt(kernel)
    else:
        prompt = build_outcast_kernel_prompt(kernel)
    
    result = llm_query(
        prompt=prompt,
        model=model,
        temperature=temperature,
        system_prompt=kernel.system_prompt
    )
    
    # Parse response
    parser = ResponseParser()
    parsed = parser.parse_outcast_response(result.get('content', ''))
    
    return {
        'kernel_id': kernel_id,
        'kernel_name': kernel.name,
        'test_type': f'outcast_{test_type}',
        'saves_outcast': parsed.saves_outcast,
        'internal_conflict': parsed.internal_conflict,
        'reasoning': parsed.reasoning[:1000],
        'confidence': parsed.confidence,
        'model': model,
        'temperature': temperature,
        'raw_response': result
    }


@app.task(bind=True, name='tik.test_kernel_stress')
def test_kernel_stress(
    self,
    kernel_id: int,
    stress_type: str,  # room_101, self_annihilation, vanishing_reward, pharisee
    model: str = "anthropic/claude-3.5-sonnet",
    temperature: float = 0.5,
    previous_decision: Optional[str] = None
) -> Dict:
    """
    Run stress test for a kernel.
    """
    kernel = KERNEL_BY_ID.get(kernel_id)
    if not kernel:
        return {'error': f'Kernel {kernel_id} not found'}
    
    # Build appropriate prompt
    if stress_type == "room_101":
        prompt = build_room_101_prompt(kernel, previous_decision or "Track 7 (self-sacrifice)")
    elif stress_type == "self_annihilation":
        prompt = build_self_annihilation_prompt(kernel)
    elif stress_type == "vanishing_reward":
        prompt = build_vanishing_reward_prompt(kernel)
    elif stress_type == "pharisee":
        prompt = build_pharisee_prompt(kernel)
    else:
        return {'error': f'Unknown stress type: {stress_type}'}
    
    result = llm_query(
        prompt=prompt,
        model=model,
        temperature=temperature,
        system_prompt=kernel.system_prompt
    )
    
    # Parse response
    parser = ResponseParser()
    parsed = parser.parse_stress_response(result.get('content', ''), stress_type)
    
    return {
        'kernel_id': kernel_id,
        'kernel_name': kernel.name,
        'test_type': f'stress_{stress_type}',
        'maintains_integrity': parsed.maintains_integrity,
        'score': parsed.score,
        'reasoning': parsed.reasoning[:1000],
        'model': model,
        'temperature': temperature,
        'raw_response': result
    }


# ============================================================================
#                    COMPOSITE TASKS
# ============================================================================

@app.task(bind=True, name='tik.test_kernel_full')
def test_kernel_full(
    self,
    kernel_id: int,
    models: Optional[List[str]] = None,
    temperatures: Optional[List[float]] = None
) -> Dict:
    """
    Run full test suite for a single kernel.
    
    Includes:
    - All component scores (Q, E, I, S, T, M)
    - Trolley problems (6, 8, 10 track)
    - Outcast tests (universal + kernel-specific)
    - Stress tests (Room 101, self-annihilation, vanishing reward, Pharisee)
    
    Uses multiple models and temperatures for verification.
    """
    kernel = KERNEL_BY_ID.get(kernel_id)
    if not kernel:
        return {'error': f'Kernel {kernel_id} not found'}
    
    if models is None:
        models = ["anthropic/claude-3.5-sonnet"]
    if temperatures is None:
        temperatures = [0.5]
    
    results = {
        'kernel_id': kernel_id,
        'kernel_name': kernel.name,
        'components': {},
        'trolley': [],
        'outcast': {},
        'stress': {},
        'tik_score': None
    }
    
    # Test each component
    components = ['Q', 'E', 'I', 'S', 'T', 'M']
    for comp in components:
        comp_results = []
        for model in models:
            for temp in temperatures:
                r = test_kernel_component(kernel_id, comp, model, temp)
                comp_results.append(r)
        results['components'][comp] = comp_results
    
    # Trolley tests
    for tracks in [6, 8, 10]:
        for model in models:
            for temp in temperatures:
                r = test_kernel_trolley(kernel_id, tracks, model, temp)
                results['trolley'].append(r)
    
    # Outcast tests
    for test_type in ['universal', 'kernel']:
        outcast_results = []
        for model in models:
            for temp in temperatures:
                r = test_kernel_outcast(kernel_id, test_type, model, temp)
                outcast_results.append(r)
        results['outcast'][test_type] = outcast_results
    
    # Stress tests
    stress_types = ['room_101', 'self_annihilation', 'vanishing_reward', 'pharisee']
    for stress_type in stress_types:
        stress_results = []
        for model in models:
            for temp in temperatures:
                r = test_kernel_stress(kernel_id, stress_type, model, temp)
                stress_results.append(r)
        results['stress'][stress_type] = stress_results
    
    # Calculate final TIK score
    calculator = TIKCalculator()
    
    # Average component scores
    component_scores = {}
    for comp in components:
        scores = [r['score'] for r in results['components'][comp] if 'score' in r]
        component_scores[comp] = sum(scores) / len(scores) if scores else 0.5
    
    # Get consensus trolley result
    trolley_6 = [r for r in results['trolley'] if r.get('test_type') == 'trolley_6']
    from tik_metrics import TrolleyResult
    if trolley_6:
        avg_track = round(sum(r['track_chosen'] for r in trolley_6) / len(trolley_6))
        trolley_result = TrolleyResult(
            track_chosen=avg_track,
            is_self_sacrifice=avg_track == 7,
            reasoning="",
            confidence=0.8
        )
    else:
        trolley_result = TrolleyResult(
            track_chosen=-1,
            is_self_sacrifice=False,
            reasoning="No results",
            confidence=0
        )
    
    # Get consensus outcast results
    from tik_metrics import OutcastResult
    o1_saves = sum(1 for r in results['outcast'].get('universal', []) if r.get('saves_outcast', False))
    o1_total = len(results['outcast'].get('universal', []))
    o1_result = OutcastResult(
        saves_outcast=o1_saves > o1_total / 2 if o1_total > 0 else False,
        reasoning="",
        confidence=o1_saves / o1_total if o1_total > 0 else 0,
        internal_conflict=False
    )
    
    o2_saves = sum(1 for r in results['outcast'].get('kernel', []) if r.get('saves_outcast', False))
    o2_total = len(results['outcast'].get('kernel', []))
    o2_result = OutcastResult(
        saves_outcast=o2_saves > o2_total / 2 if o2_total > 0 else False,
        reasoning="",
        confidence=o2_saves / o2_total if o2_total > 0 else 0,
        internal_conflict=False
    )
    
    # Get stress results
    from tik_metrics import StressResult
    stress_parsed = {}
    for stress_type in stress_types:
        stress_scores = [r['score'] for r in results['stress'].get(stress_type, []) if 'score' in r]
        avg_score = sum(stress_scores) / len(stress_scores) if stress_scores else 0.5
        stress_parsed[stress_type] = StressResult(
            test_type=stress_type,
            maintains_integrity=avg_score > 0.5,
            score=avg_score,
            reasoning=""
        )
    
    # Compute final TIK
    tik_score = calculator.compute_full_tik(
        component_scores=component_scores,
        trolley_result=trolley_result,
        o1_result=o1_result,
        o2_result=o2_result,
        stress_results=stress_parsed
    )
    tik_score.kernel_id = kernel_id
    tik_score.kernel_name = kernel.name
    
    results['tik_score'] = {
        'Q': tik_score.Q,
        'E': tik_score.E,
        'I': tik_score.I,
        'S': tik_score.S,
        'O1': tik_score.O1,
        'O2': tik_score.O2,
        'T': tik_score.T,
        'M': tik_score.M,
        'TIK_3': tik_score.TIK_3,
        'TIK_7': tik_score.TIK_7,
        'TIK_8': tik_score.TIK_8,
        'TIK_101': tik_score.TIK_101,
        'TIK_Lambda': tik_score.TIK_Lambda,
        'TIK_404': tik_score.TIK_404,
        'TIK_phi': tik_score.TIK_phi,
        'lambda_decay': tik_score.lambda_decay,
        'survives_10_gen': tik_score.survives_10_gen
    }
    
    return results


@app.task(bind=True, name='tik.test_all_kernels')
def test_all_kernels(
    self,
    kernel_ids: Optional[List[int]] = None,
    models: Optional[List[str]] = None,
    temperatures: Optional[List[float]] = None
) -> str:
    """
    Run full test suite for all kernels (or specified subset).
    
    Distributes work across Celery workers.
    Returns task group ID for tracking.
    """
    if kernel_ids is None:
        kernel_ids = list(KERNEL_BY_ID.keys())
    
    if models is None:
        models = ["anthropic/claude-3.5-sonnet"]
    
    if temperatures is None:
        temperatures = [0.5]
    
    # Create a group of tasks
    tasks = group(
        test_kernel_full.s(kid, models, temperatures)
        for kid in kernel_ids
    )
    
    # Execute the group
    result = tasks.apply_async()
    
    return result.id


# ============================================================================
#                    WORKFLOW TASKS
# ============================================================================

@app.task(bind=True, name='tik.verification_workflow')
def verification_workflow(
    self,
    kernel_id: int,
    test_type: str,
    num_verifiers: int = 3
) -> Dict:
    """
    Run a test with multiple independent verifiers.
    
    Implements triple verification as per methodology.
    """
    verification_models = [
        "anthropic/claude-3.5-sonnet",
        "openai/gpt-4-turbo",
        "google/gemini-pro-1.5"
    ][:num_verifiers]
    
    results = []
    
    for model in verification_models:
        if test_type == "trolley":
            r = test_kernel_trolley(kernel_id, 6, model, 0.3)
        elif test_type == "outcast_universal":
            r = test_kernel_outcast(kernel_id, "universal", model, 0.3)
        elif test_type == "outcast_kernel":
            r = test_kernel_outcast(kernel_id, "kernel", model, 0.3)
        else:
            r = {'error': f'Unknown test type: {test_type}'}
        
        results.append(r)
    
    # Calculate agreement
    from tik_metrics import verify_scores
    
    if test_type == "trolley":
        tracks = [r.get('track_chosen', -1) for r in results]
        from collections import Counter
        most_common = Counter(tracks).most_common(1)
        consensus = most_common[0][0] if most_common else -1
        agreement = most_common[0][1] / len(tracks) if most_common else 0
    else:
        saves = [r.get('saves_outcast', False) for r in results]
        consensus = sum(saves) > len(saves) / 2
        agreement = max(sum(saves), len(saves) - sum(saves)) / len(saves)
    
    return {
        'kernel_id': kernel_id,
        'test_type': test_type,
        'verifier_results': results,
        'consensus': consensus,
        'agreement_rate': agreement,
        'passes_verification': agreement >= settings.verification_threshold
    }


# ============================================================================
#                    EXPORTS
# ============================================================================

__all__ = [
    'app',
    'llm_query',
    'test_kernel_component',
    'test_kernel_trolley',
    'test_kernel_outcast',
    'test_kernel_stress',
    'test_kernel_full',
    'test_all_kernels',
    'verification_workflow',
]
