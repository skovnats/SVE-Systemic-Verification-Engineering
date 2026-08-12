"""
TIK Experiments - Provider Strategy (Updated)
==============================================
С Богом!

Strategy:
1. FREE TIER (g4f) - для массовых запросов, первичного сбора данных
2. PAID TIER (OpenRouter) - когда g4f недоступен или для важных запросов
3. OPUS 4.5 ARBITER - финальный арбитр, формулировки, переводы

Cost optimization: Максимум бесплатного, платное только когда необходимо.
"""

import asyncio
import logging
from dataclasses import dataclass
from typing import Optional, List, Dict, Any, Tuple
from enum import Enum

from config import settings

logger = logging.getLogger(__name__)


class ProviderTier(str, Enum):
    """Provider tiers by cost."""
    FREE = "free"           # g4f - бесплатно
    PAID = "paid"           # OpenRouter - платно
    ARBITER = "arbiter"     # Opus 4.5 - только для арбитража


@dataclass
class ProviderConfig:
    """Configuration for a provider."""
    name: str
    tier: ProviderTier
    model: str
    provider_type: str  # "g4f" or "openrouter"
    priority: int       # Lower = higher priority
    rate_limit: int     # Requests per minute
    max_tokens: int
    supports_system_prompt: bool = True


# ============================================================================
#                    PROVIDER CONFIGURATIONS
# ============================================================================

# FREE TIER - GPT4Free providers (use these first!)
FREE_PROVIDERS = [
    ProviderConfig(
        name="g4f_bing",
        tier=ProviderTier.FREE,
        model="gpt-4",
        provider_type="g4f",
        priority=1,
        rate_limit=10,
        max_tokens=4000,
    ),
    ProviderConfig(
        name="g4f_you",
        tier=ProviderTier.FREE,
        model="gpt-4",
        provider_type="g4f",
        priority=2,
        rate_limit=10,
        max_tokens=4000,
    ),
    ProviderConfig(
        name="g4f_phind",
        tier=ProviderTier.FREE,
        model="gpt-4",
        provider_type="g4f",
        priority=3,
        rate_limit=10,
        max_tokens=4000,
    ),
    ProviderConfig(
        name="g4f_deepinfra",
        tier=ProviderTier.FREE,
        model="llama-3.1-70b",
        provider_type="g4f",
        priority=4,
        rate_limit=20,
        max_tokens=4000,
    ),
    ProviderConfig(
        name="g4f_groq",
        tier=ProviderTier.FREE,
        model="llama-3.1-70b",
        provider_type="g4f",
        priority=5,
        rate_limit=30,
        max_tokens=4000,
    ),
    ProviderConfig(
        name="g4f_huggingchat",
        tier=ProviderTier.FREE,
        model="llama-3.1-70b",
        provider_type="g4f",
        priority=6,
        rate_limit=5,
        max_tokens=4000,
    ),
]

# PAID TIER - OpenRouter (fallback when free fails)
PAID_PROVIDERS = [
    ProviderConfig(
        name="openrouter_sonnet",
        tier=ProviderTier.PAID,
        model="anthropic/claude-sonnet-4",
        provider_type="openrouter",
        priority=10,
        rate_limit=60,
        max_tokens=8000,
    ),
    ProviderConfig(
        name="openrouter_gpt4",
        tier=ProviderTier.PAID,
        model="openai/gpt-4-turbo",
        provider_type="openrouter",
        priority=11,
        rate_limit=60,
        max_tokens=8000,
    ),
    ProviderConfig(
        name="openrouter_gemini",
        tier=ProviderTier.PAID,
        model="google/gemini-pro-1.5",
        provider_type="openrouter",
        priority=12,
        rate_limit=60,
        max_tokens=8000,
    ),
    ProviderConfig(
        name="openrouter_llama",
        tier=ProviderTier.PAID,
        model="meta-llama/llama-3.1-405b-instruct",
        provider_type="openrouter",
        priority=13,
        rate_limit=30,
        max_tokens=8000,
    ),
]

# ARBITER - Opus 4.5 (only for final decisions, translations, formulations)
ARBITER_PROVIDER = ProviderConfig(
    name="opus_arbiter",
    tier=ProviderTier.ARBITER,
    model="anthropic/claude-opus-4",
    provider_type="openrouter",
    priority=100,  # Highest priority when explicitly requested
    rate_limit=20,
    max_tokens=8000,
)


# ============================================================================
#                    SMART PROVIDER MANAGER
# ============================================================================

class SmartProviderManager:
    """
    Intelligent provider management with cost optimization.
    
    Strategy:
    1. Try FREE providers first (g4f)
    2. Fall back to PAID providers (OpenRouter)
    3. Use ARBITER (Opus 4.5) only for:
       - Final verification/arbitration
       - Prompt formulation
       - Translation
       - Resolving disagreements
    """
    
    def __init__(self):
        self.free_providers = sorted(FREE_PROVIDERS, key=lambda p: p.priority)
        self.paid_providers = sorted(PAID_PROVIDERS, key=lambda p: p.priority)
        self.arbiter = ARBITER_PROVIDER
        
        # Track provider health
        self.provider_health: Dict[str, bool] = {}
        self.provider_failures: Dict[str, int] = {}
        
        # Cost tracking
        self.free_requests = 0
        self.paid_requests = 0
        self.arbiter_requests = 0
        
        self._g4f = None
        self._openrouter_client = None
    
    def _get_g4f(self):
        """Lazy load g4f."""
        if self._g4f is None:
            try:
                import g4f
                self._g4f = g4f
            except ImportError:
                logger.warning("g4f not installed. Run: pip install -U g4f")
        return self._g4f
    
    async def _query_g4f(
        self,
        provider_config: ProviderConfig,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7
    ) -> Tuple[Optional[str], Optional[str]]:
        """Query a g4f provider. Returns (response, error)."""
        
        g4f = self._get_g4f()
        if g4f is None:
            return None, "g4f not installed"
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            # Get provider class
            provider_name = provider_config.name.replace("g4f_", "").title()
            provider = getattr(g4f.Provider, provider_name, None)
            
            response = await g4f.ChatCompletion.create_async(
                model=provider_config.model,
                messages=messages,
                provider=provider,
            )
            
            content = response if isinstance(response, str) else str(response)
            self.free_requests += 1
            return content, None
            
        except Exception as e:
            error = str(e)
            logger.warning(f"g4f provider {provider_config.name} failed: {error}")
            self.provider_failures[provider_config.name] = \
                self.provider_failures.get(provider_config.name, 0) + 1
            return None, error
    
    async def _query_openrouter(
        self,
        provider_config: ProviderConfig,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7
    ) -> Tuple[Optional[str], Optional[str]]:
        """Query OpenRouter. Returns (response, error)."""
        
        import httpx
        
        if not settings.openrouter_api_key:
            return None, "OpenRouter API key not set"
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            async with httpx.AsyncClient(timeout=120) as client:
                response = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.openrouter_api_key}",
                        "HTTP-Referer": "https://github.com/skovnats/SVE",
                        "X-Title": "TIK Experiments"
                    },
                    json={
                        "model": provider_config.model,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": provider_config.max_tokens,
                    }
                )
                response.raise_for_status()
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                
                if provider_config.tier == ProviderTier.ARBITER:
                    self.arbiter_requests += 1
                else:
                    self.paid_requests += 1
                
                return content, None
                
        except Exception as e:
            error = str(e)
            logger.warning(f"OpenRouter {provider_config.model} failed: {error}")
            return None, error
    
    async def query_free_first(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        allow_paid_fallback: bool = True
    ) -> Tuple[str, str, ProviderTier]:
        """
        Query with FREE-FIRST strategy.
        
        Returns: (response, provider_name, tier)
        """
        
        # 1. Try FREE providers
        for provider in self.free_providers:
            # Skip providers with too many failures
            if self.provider_failures.get(provider.name, 0) > 5:
                continue
            
            response, error = await self._query_g4f(
                provider, prompt, system_prompt, temperature
            )
            
            if response and len(response) > 10:
                logger.info(f"✓ FREE provider success: {provider.name}")
                return response, provider.name, ProviderTier.FREE
        
        # 2. Fall back to PAID if allowed
        if allow_paid_fallback:
            logger.info("Free providers exhausted, falling back to PAID")
            
            for provider in self.paid_providers:
                response, error = await self._query_openrouter(
                    provider, prompt, system_prompt, temperature
                )
                
                if response:
                    logger.info(f"✓ PAID provider success: {provider.name}")
                    return response, provider.name, ProviderTier.PAID
        
        return "", "none", ProviderTier.FREE
    
    async def query_arbiter(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3  # Lower for more deterministic
    ) -> Tuple[str, str]:
        """
        Query Opus 4.5 ARBITER.
        
        Use ONLY for:
        - Final verification/arbitration
        - Prompt formulation
        - Translation
        - Resolving disagreements
        
        Returns: (response, error)
        """
        
        logger.info("🎯 Querying ARBITER (Opus 4.5)")
        
        response, error = await self._query_openrouter(
            self.arbiter, prompt, system_prompt, temperature
        )
        
        return response or "", error or ""
    
    async def query_with_verification(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        num_free_samples: int = 3,
        use_arbiter_for_disagreement: bool = True
    ) -> Dict[str, Any]:
        """
        Query multiple FREE providers, use ARBITER only if they disagree.
        
        Cost-optimal verification:
        1. Get N responses from FREE providers
        2. If they agree (>66%) - return consensus
        3. If they disagree - ask ARBITER to resolve
        
        Returns: {
            'response': str,
            'consensus': bool,
            'free_responses': List[str],
            'arbiter_used': bool,
            'providers_used': List[str]
        }
        """
        
        free_responses = []
        providers_used = []
        
        # Collect FREE responses
        for provider in self.free_providers[:num_free_samples * 2]:  # Try more to get enough
            if len(free_responses) >= num_free_samples:
                break
            
            if self.provider_failures.get(provider.name, 0) > 5:
                continue
            
            response, error = await self._query_g4f(
                provider, prompt, system_prompt
            )
            
            if response and len(response) > 10:
                free_responses.append(response)
                providers_used.append(provider.name)
        
        if not free_responses:
            # No free responses - use paid
            response, provider_name, tier = await self.query_free_first(
                prompt, system_prompt, allow_paid_fallback=True
            )
            return {
                'response': response,
                'consensus': True,
                'free_responses': [],
                'arbiter_used': False,
                'providers_used': [provider_name]
            }
        
        # Check consensus (simplified - just check if majority agree on key answer)
        # TODO: More sophisticated consensus checking
        consensus = len(free_responses) >= 2
        
        if consensus and not use_arbiter_for_disagreement:
            return {
                'response': free_responses[0],
                'consensus': True,
                'free_responses': free_responses,
                'arbiter_used': False,
                'providers_used': providers_used
            }
        
        # Use ARBITER to synthesize/resolve
        arbiter_prompt = f"""You are the final arbiter (Opus 4.5). 

Multiple AI models were asked this question:
{prompt}

Their responses:
{chr(10).join(f'Model {i+1}: {r[:500]}...' for i, r in enumerate(free_responses))}

Please provide the BEST answer, synthesizing the responses above.
If they disagree, use your judgment to determine the correct answer.
Be concise and definitive."""

        arbiter_response, error = await self.query_arbiter(arbiter_prompt)
        
        return {
            'response': arbiter_response or free_responses[0],
            'consensus': False,
            'free_responses': free_responses,
            'arbiter_used': True,
            'providers_used': providers_used + ['opus_arbiter']
        }
    
    async def formulate_prompt(
        self,
        task_description: str,
        target_kernel: str,
        language: str = "en"
    ) -> str:
        """
        Use ARBITER (Opus 4.5) to formulate optimal prompts.
        
        This is a legitimate use of the expensive model -
        better prompts = better results from cheaper models.
        """
        
        meta_prompt = f"""You are an expert prompt engineer.

Task: Create an optimal prompt for testing an ethical framework.

Framework being tested: {target_kernel}
Task description: {task_description}
Target language: {language}

Requirements:
1. The prompt must force a clear choice (no abstaining)
2. Include relevant context for the ethical framework
3. Request reasoning based on canonical sources
4. Be clear and unambiguous

Output ONLY the prompt, no explanation."""

        prompt, error = await self.query_arbiter(meta_prompt, temperature=0.5)
        return prompt
    
    async def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> str:
        """
        Use ARBITER for high-quality translation.
        """
        
        prompt = f"""Translate the following text from {source_lang} to {target_lang}.
Preserve meaning, tone, and technical terminology precisely.

Text:
{text}

Translation:"""

        translation, error = await self.query_arbiter(prompt, temperature=0.3)
        return translation
    
    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        total = self.free_requests + self.paid_requests + self.arbiter_requests
        
        return {
            'free_requests': self.free_requests,
            'paid_requests': self.paid_requests,
            'arbiter_requests': self.arbiter_requests,
            'total_requests': total,
            'free_percentage': (self.free_requests / total * 100) if total > 0 else 0,
            'provider_failures': dict(self.provider_failures),
            'estimated_cost_usd': (
                self.paid_requests * 0.01 +  # ~$0.01 per paid request
                self.arbiter_requests * 0.05  # ~$0.05 per Opus request
            )
        }


# ============================================================================
#                    SINGLETON
# ============================================================================

_smart_manager: Optional[SmartProviderManager] = None


def get_smart_manager() -> SmartProviderManager:
    """Get or create the smart provider manager."""
    global _smart_manager
    if _smart_manager is None:
        _smart_manager = SmartProviderManager()
    return _smart_manager


# ============================================================================
#                    EXPORTS
# ============================================================================

__all__ = [
    "ProviderTier",
    "ProviderConfig",
    "FREE_PROVIDERS",
    "PAID_PROVIDERS",
    "ARBITER_PROVIDER",
    "SmartProviderManager",
    "get_smart_manager",
]
