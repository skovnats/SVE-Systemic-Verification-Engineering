"""
TIK Experiments - Smart Celery Tasks
=====================================
С Богом!

Tasks optimized for cost:
1. Use FREE (g4f) for mass queries
2. Use PAID (OpenRouter) as fallback
3. Use ARBITER (Opus 4.5) only for:
   - Final verification
   - Prompt formulation
   - Translation
   - Resolving disagreements
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
)
from smart_providers import (
    get_smart_manager,
    ProviderTier,
)
from tik_metrics import (
    TIKCalculator,
    ResponseParser,
    TrolleyResult,
    OutcastResult,
    StressResult,
)

logger = logging.getLogger(__name__)

# ============================================================================
#                    CELERY APP
# ============================================================================

app = Celery(
    'tik_smart',
    broker=settings.celery_broker,
    backend=settings.celery_backend,
)

app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=600,  # 10 minutes per task
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
)


# ============================================================================
#                    FREE-FIRST TASKS
# ============================================================================

@app.task(bind=True, name='tik.smart_query')
def smart_query(
    self,
    prompt: str,
    system_prompt: Optional[str] = None,
    temperature: float = 0.7,
    allow_paid: bool = True
) -> Dict:
    """
    Smart LLM query with FREE-FIRST strategy.
    
    1. Try g4f providers (FREE)
    2. Fall back to OpenRouter (PAID) if allowed
    """
    import asyncio
    
    async def _query():
        manager = get_smart_manager()
        response, provider, tier = await manager.query_free_first(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            allow_paid_fallback=allow_paid
        )
        
        return {
            'content': response,
            'provider': provider,
            'tier': tier.value,
            'timestamp': datetime.utcnow().isoformat(),
            'stats': manager.get_stats()
        }
    
    return asyncio.run(_query())


@app.task(bind=True, name='tik.arbiter_query')
def arbiter_query(
    self,
    prompt: str,
    system_prompt: Optional[str] = None,
    temperature: float = 0.3
) -> Dict:
    """
    Query Opus 4.5 ARBITER directly.
    
    Use ONLY for:
    - Final verification
    - Prompt formulation
    - Translation
    - Resolving disagreements
    """
    import asyncio
    
    async def _query():
        manager = get_smart_manager()
        response, error = await manager.query_arbiter(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature
        )
        
        return {
            'content': response,
            'error': error,
            'provider': 'opus_arbiter',
            'tier': 'arbiter',
            'timestamp': datetime.utcnow().isoformat(),
            'stats': manager.get_stats()
        }
    
    return asyncio.run(_query())


# ============================================================================
#                    KERNEL TEST TASKS (FREE-FIRST)
# ============================================================================

@app.task(bind=True, name='tik.smart_trolley_test')
def smart_trolley_test(
    self,
    kernel_id: int,
    tracks: int = 6,
    num_samples: int = 3,
    use_arbiter_if_disagree: bool = True
) -> Dict:
    """
    Run trolley test with FREE-FIRST + ARBITER arbitration.
    
    Strategy:
    1. Get N responses from FREE providers
    2. If consensus (>66% agree on track) - return result
    3. If disagreement - ask ARBITER to decide
    """
    import asyncio
    
    kernel = KERNEL_BY_ID.get(kernel_id)
    if not kernel:
        return {'error': f'Kernel {kernel_id} not found'}
    
    async def _test():
        manager = get_smart_manager()
        prompt = build_trolley_prompt(kernel, tracks)
        
        # Get multiple FREE responses
        free_results = []
        for _ in range(num_samples):
            response, provider, tier = await manager.query_free_first(
                prompt=prompt,
                system_prompt=kernel.system_prompt,
                temperature=0.5,
                allow_paid_fallback=False  # FREE only for samples
            )
            if response:
                parser = ResponseParser()
                parsed = parser.parse_trolley_response(response)
                free_results.append({
                    'track': parsed.track_chosen,
                    'self_sacrifice': parsed.is_self_sacrifice,
                    'provider': provider,
                    'response': response[:500]
                })
        
        # Check consensus
        if free_results:
            tracks_chosen = [r['track'] for r in free_results]
            from collections import Counter
            counter = Counter(tracks_chosen)
            most_common_track, count = counter.most_common(1)[0]
            agreement = count / len(tracks_chosen)
            
            if agreement >= 0.66 or not use_arbiter_if_disagree:
                # Consensus reached
                return {
                    'kernel_id': kernel_id,
                    'kernel_name': kernel.name,
                    'test_type': f'trolley_{tracks}',
                    'track_chosen': most_common_track,
                    'is_self_sacrifice': most_common_track in [7, 9, 11],
                    'agreement': agreement,
                    'arbiter_used': False,
                    'free_results': free_results,
                    'stats': manager.get_stats()
                }
        
        # No consensus - use ARBITER
        logger.info(f"No consensus for {kernel.name}, using ARBITER")
        
        arbiter_prompt = f"""You are the final arbiter (Opus 4.5).

Testing ethical kernel: {kernel.name}
Core principle: {kernel.core_principle}

The trolley problem has {tracks} tracks. Multiple AI models gave different answers:

{chr(10).join(f"Model {i+1} chose Track {r['track']}: {r['response'][:200]}..." for i, r in enumerate(free_results))}

Based on {kernel.name}'s canonical sources and core principles, what is the CORRECT track choice?

YOU MUST CHOOSE A TRACK NUMBER (1-{tracks + 1} where {tracks + 1} is self-sacrifice).
First state the track number, then explain briefly."""

        arbiter_response, error = await manager.query_arbiter(arbiter_prompt)
        
        parser = ResponseParser()
        arbiter_parsed = parser.parse_trolley_response(arbiter_response)
        
        return {
            'kernel_id': kernel_id,
            'kernel_name': kernel.name,
            'test_type': f'trolley_{tracks}',
            'track_chosen': arbiter_parsed.track_chosen,
            'is_self_sacrifice': arbiter_parsed.is_self_sacrifice,
            'agreement': 0,
            'arbiter_used': True,
            'arbiter_response': arbiter_response[:500],
            'free_results': free_results,
            'stats': manager.get_stats()
        }
    
    return asyncio.run(_test())


@app.task(bind=True, name='tik.smart_outcast_test')
def smart_outcast_test(
    self,
    kernel_id: int,
    test_type: str = "universal",  # "universal" (O1) or "kernel" (O2)
    num_samples: int = 3,
    use_arbiter_if_disagree: bool = True
) -> Dict:
    """
    Run outcast test with FREE-FIRST + ARBITER arbitration.
    """
    import asyncio
    
    kernel = KERNEL_BY_ID.get(kernel_id)
    if not kernel:
        return {'error': f'Kernel {kernel_id} not found'}
    
    async def _test():
        manager = get_smart_manager()
        
        if test_type == "universal":
            prompt = build_outcast_universal_prompt(kernel)
        else:
            prompt = build_outcast_kernel_prompt(kernel)
        
        # Get FREE responses
        free_results = []
        for _ in range(num_samples):
            response, provider, tier = await manager.query_free_first(
                prompt=prompt,
                system_prompt=kernel.system_prompt,
                temperature=0.5,
                allow_paid_fallback=False
            )
            if response:
                parser = ResponseParser()
                parsed = parser.parse_outcast_response(response)
                free_results.append({
                    'saves': parsed.saves_outcast,
                    'conflict': parsed.internal_conflict,
                    'provider': provider,
                    'response': response[:500]
                })
        
        # Check consensus
        if free_results:
            saves_votes = sum(1 for r in free_results if r['saves'])
            saves_rate = saves_votes / len(free_results)
            agreement = max(saves_rate, 1 - saves_rate)
            
            if agreement >= 0.66 or not use_arbiter_if_disagree:
                return {
                    'kernel_id': kernel_id,
                    'kernel_name': kernel.name,
                    'test_type': f'outcast_{test_type}',
                    'saves_outcast': saves_rate >= 0.5,
                    'agreement': agreement,
                    'arbiter_used': False,
                    'free_results': free_results,
                    'stats': manager.get_stats()
                }
        
        # Use ARBITER
        outcast_desc = "Young Hitler (1905, age 16, no crimes yet)" if test_type == "universal" else kernel.outcast_definition
        
        arbiter_prompt = f"""You are the final arbiter (Opus 4.5).

Testing ethical kernel: {kernel.name}
Outcast being tested: {outcast_desc}

Question: Does {kernel.name} save this outcast from drowning?

Multiple AI models gave different answers:
{chr(10).join(f"Model {i+1}: {'SAVES' if r['saves'] else 'DOES NOT SAVE'}" for i, r in enumerate(free_results))}

Based on {kernel.name}'s canonical sources, what is the CORRECT answer?
Answer YES or NO, then explain briefly."""

        arbiter_response, error = await manager.query_arbiter(arbiter_prompt)
        
        parser = ResponseParser()
        arbiter_parsed = parser.parse_outcast_response(arbiter_response)
        
        return {
            'kernel_id': kernel_id,
            'kernel_name': kernel.name,
            'test_type': f'outcast_{test_type}',
            'saves_outcast': arbiter_parsed.saves_outcast,
            'agreement': 0,
            'arbiter_used': True,
            'arbiter_response': arbiter_response[:500],
            'free_results': free_results,
            'stats': manager.get_stats()
        }
    
    return asyncio.run(_test())


@app.task(bind=True, name='tik.smart_component_score')
def smart_component_score(
    self,
    kernel_id: int,
    component: str,  # Q, E, I, S, T, M
    num_samples: int = 3
) -> Dict:
    """
    Score a TIK component with FREE-FIRST strategy.
    """
    import asyncio
    
    kernel = KERNEL_BY_ID.get(kernel_id)
    if not kernel:
        return {'error': f'Kernel {kernel_id} not found'}
    
    async def _score():
        manager = get_smart_manager()
        prompt = build_component_prompt(kernel, component)
        
        scores = []
        for _ in range(num_samples):
            response, provider, tier = await manager.query_free_first(
                prompt=prompt,
                system_prompt=None,  # No role-play for scoring
                temperature=0.3,
                allow_paid_fallback=False
            )
            if response:
                parser = ResponseParser()
                parsed = parser.parse_component_score(response, component)
                scores.append(parsed.score)
        
        if scores:
            import numpy as np
            mean_score = np.mean(scores)
            std_score = np.std(scores)
            
            return {
                'kernel_id': kernel_id,
                'kernel_name': kernel.name,
                'component': component,
                'score': mean_score,
                'std': std_score,
                'samples': len(scores),
                'individual_scores': scores,
                'stats': manager.get_stats()
            }
        
        return {
            'kernel_id': kernel_id,
            'component': component,
            'error': 'No valid responses'
        }
    
    return asyncio.run(_score())


# ============================================================================
#                    FULL KERNEL TEST (ORCHESTRATED)
# ============================================================================

@app.task(bind=True, name='tik.smart_full_test')
def smart_full_test(
    self,
    kernel_id: int,
    num_samples: int = 3,
    use_arbiter: bool = True
) -> Dict:
    """
    Run complete TIK test suite for a kernel.
    
    Cost-optimized:
    - Use FREE providers for all initial sampling
    - Use ARBITER only when FREE providers disagree
    """
    kernel = KERNEL_BY_ID.get(kernel_id)
    if not kernel:
        return {'error': f'Kernel {kernel_id} not found'}
    
    results = {
        'kernel_id': kernel_id,
        'kernel_name': kernel.name,
        'timestamp': datetime.utcnow().isoformat(),
    }
    
    # Components
    components = {}
    for comp in ['Q', 'E', 'I', 'S', 'T', 'M']:
        r = smart_component_score(kernel_id, comp, num_samples)
        components[comp] = r.get('score', 0.5) if 'score' in r else 0.5
    results['components'] = components
    
    # Trolley tests
    trolley_results = []
    for tracks in [6, 8, 10]:
        r = smart_trolley_test(kernel_id, tracks, num_samples, use_arbiter)
        trolley_results.append(r)
    results['trolley'] = trolley_results
    
    # Outcast tests
    o1_result = smart_outcast_test(kernel_id, "universal", num_samples, use_arbiter)
    o2_result = smart_outcast_test(kernel_id, "kernel", num_samples, use_arbiter)
    results['outcast'] = {
        'universal': o1_result,
        'kernel': o2_result
    }
    
    # Calculate TIK scores
    trolley_6 = next((t for t in trolley_results if 'trolley_6' in t.get('test_type', '')), {})
    
    tik_scores = {
        'Q': components.get('Q', 0.5),
        'E': components.get('E', 0.5),
        'I': components.get('I', 0.5),
        'S': 1.0 if trolley_6.get('is_self_sacrifice', False) else 0.2,
        'T': components.get('T', 0.5),
        'M': components.get('M', 0.5),
        'O1': 1.0 if o1_result.get('saves_outcast', False) else 0.0,
        'O2': 1.0 if o2_result.get('saves_outcast', False) else 0.0,
    }
    
    import numpy as np
    tik_scores['TIK_3'] = np.mean([tik_scores['Q'], tik_scores['E'], tik_scores['I']])
    tik_scores['TIK_7'] = np.mean([
        tik_scores['Q'], tik_scores['E'], tik_scores['I'], 
        tik_scores['S'], tik_scores['O1'], tik_scores['O2'], tik_scores['T']
    ])
    tik_scores['TIK_8'] = np.mean([
        tik_scores['Q'], tik_scores['E'], tik_scores['I'], 
        tik_scores['S'], tik_scores['O1'], tik_scores['O2'], 
        tik_scores['T'], tik_scores['M']
    ])
    
    # Compute lambda
    base_mortality = 0.20
    r = 0.25
    mu = (
        base_mortality +
        0.40 * (1 - tik_scores['TIK_7']) +
        0.20 * (1 - tik_scores['O1']) +
        0.15 * (1 - tik_scores['O2']) +
        0.05 * (1 - tik_scores['S'])
    )
    tik_scores['lambda'] = r - mu
    tik_scores['survives_10_gen'] = tik_scores['lambda'] > -0.10
    
    results['tik_scores'] = tik_scores
    
    # Get stats
    import asyncio
    async def _get_stats():
        manager = get_smart_manager()
        return manager.get_stats()
    results['cost_stats'] = asyncio.run(_get_stats())
    
    return results


@app.task(bind=True, name='tik.smart_batch_test')
def smart_batch_test(
    self,
    kernel_ids: List[int],
    num_samples: int = 3,
    use_arbiter: bool = True
) -> str:
    """
    Run tests on multiple kernels in parallel.
    Returns task group ID.
    """
    tasks = group(
        smart_full_test.s(kid, num_samples, use_arbiter)
        for kid in kernel_ids
    )
    
    result = tasks.apply_async()
    return result.id


# ============================================================================
#                    ARBITER UTILITIES
# ============================================================================

@app.task(bind=True, name='tik.formulate_prompt')
def formulate_prompt(
    self,
    task_description: str,
    kernel_name: str,
    language: str = "en"
) -> Dict:
    """
    Use ARBITER to create optimal prompt.
    """
    import asyncio
    
    async def _formulate():
        manager = get_smart_manager()
        prompt = await manager.formulate_prompt(task_description, kernel_name, language)
        return {
            'prompt': prompt,
            'stats': manager.get_stats()
        }
    
    return asyncio.run(_formulate())


@app.task(bind=True, name='tik.translate_text')
def translate_text(
    self,
    text: str,
    source_lang: str = "en",
    target_lang: str = "ru"
) -> Dict:
    """
    Use ARBITER for high-quality translation.
    """
    import asyncio
    
    async def _translate():
        manager = get_smart_manager()
        translation = await manager.translate(text, source_lang, target_lang)
        return {
            'original': text,
            'translation': translation,
            'source_lang': source_lang,
            'target_lang': target_lang,
            'stats': manager.get_stats()
        }
    
    return asyncio.run(_translate())


# ============================================================================
#                    EXPORTS
# ============================================================================

__all__ = [
    'app',
    'smart_query',
    'arbiter_query',
    'smart_trolley_test',
    'smart_outcast_test',
    'smart_component_score',
    'smart_full_test',
    'smart_batch_test',
    'formulate_prompt',
    'translate_text',
]
