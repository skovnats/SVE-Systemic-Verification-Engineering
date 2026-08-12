"""
TIK Experiments - LLM Providers
================================
С Богом!

Architecture:
- FREE TIER (GPT4Free): Mass queries, multiple providers, rotation
- PAID TIER (Opus 4.5 via OpenRouter): Arbiter, prompts, translations

Integration with OpenRouter and GPT4Free for distributed testing.
Supports multiple models, temperatures, and fallback chains.
"""

import asyncio
import json
import logging
import random
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, AsyncGenerator, Tuple
from enum import Enum
from datetime import datetime

import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

from config import settings, LLMProvider

logger = logging.getLogger(__name__)


# ============================================================================
#                    PROVIDER TIER ENUM
# ============================================================================

class ProviderTier(str, Enum):
    """Provider tier for cost optimization."""
    FREE = "free"      # GPT4Free - for mass queries
    ARBITER = "arbiter"  # Opus 4.5 - for arbitration, prompts, translations


# ============================================================================
#                    DATA CLASSES
# ============================================================================

@dataclass
class LLMResponse:
    """Response from an LLM."""
    content: str
    model: str
    provider: str
    temperature: float
    tokens_used: int
    latency_ms: float
    raw_response: Optional[Dict] = None
    error: Optional[str] = None
    
    @property
    def success(self) -> bool:
        return self.error is None and len(self.content) > 0


@dataclass
class LLMConfig:
    """Configuration for an LLM request."""
    model: str
    temperature: float = 0.7
    max_tokens: int = 2000
    system_prompt: Optional[str] = None
    provider: LLMProvider = LLMProvider.OPENROUTER


# ============================================================================
#                    BASE PROVIDER
# ============================================================================

class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    async def complete(
        self,
        prompt: str,
        config: LLMConfig
    ) -> LLMResponse:
        """Send completion request to LLM."""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if provider is healthy."""
        pass


# ============================================================================
#                    OPENROUTER PROVIDER
# ============================================================================

class OpenRouterProvider(BaseLLMProvider):
    """
    OpenRouter provider for accessing multiple LLMs.
    
    Supports: Claude, GPT-4, Gemini, Llama, Mistral, etc.
    https://openrouter.ai/
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://openrouter.ai/api/v1"
    ):
        self.api_key = api_key or settings.openrouter_api_key
        self.base_url = base_url
        
        if not self.api_key:
            logger.warning("OpenRouter API key not set!")
        
        self.client = httpx.AsyncClient(
            timeout=settings.request_timeout,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "https://github.com/skovnats/SVE",
                "X-Title": "TIK Experiments"
            }
        )
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException))
    )
    async def complete(
        self,
        prompt: str,
        config: LLMConfig
    ) -> LLMResponse:
        """Send completion request to OpenRouter."""
        
        import time
        start_time = time.time()
        
        messages = []
        
        # Add system prompt if provided
        if config.system_prompt:
            messages.append({
                "role": "system",
                "content": config.system_prompt
            })
        
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        payload = {
            "model": config.model,
            "messages": messages,
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                json=payload
            )
            response.raise_for_status()
            
            data = response.json()
            
            latency_ms = (time.time() - start_time) * 1000
            
            content = data["choices"][0]["message"]["content"]
            tokens_used = data.get("usage", {}).get("total_tokens", 0)
            
            return LLMResponse(
                content=content,
                model=config.model,
                provider="openrouter",
                temperature=config.temperature,
                tokens_used=tokens_used,
                latency_ms=latency_ms,
                raw_response=data
            )
            
        except httpx.HTTPStatusError as e:
            logger.error(f"OpenRouter HTTP error: {e.response.status_code}")
            return LLMResponse(
                content="",
                model=config.model,
                provider="openrouter",
                temperature=config.temperature,
                tokens_used=0,
                latency_ms=(time.time() - start_time) * 1000,
                error=f"HTTP {e.response.status_code}: {e.response.text}"
            )
        except Exception as e:
            logger.error(f"OpenRouter error: {e}")
            return LLMResponse(
                content="",
                model=config.model,
                provider="openrouter",
                temperature=config.temperature,
                tokens_used=0,
                latency_ms=(time.time() - start_time) * 1000,
                error=str(e)
            )
    
    async def health_check(self) -> bool:
        """Check if OpenRouter is accessible."""
        try:
            response = await self.client.get(f"{self.base_url}/models")
            return response.status_code == 200
        except Exception:
            return False
    
    async def list_models(self) -> List[str]:
        """List available models."""
        try:
            response = await self.client.get(f"{self.base_url}/models")
            response.raise_for_status()
            data = response.json()
            return [m["id"] for m in data.get("data", [])]
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            return []


# ============================================================================
#                    GPT4FREE PROVIDER
# ============================================================================

class GPT4FreeProvider(BaseLLMProvider):
    """
    GPT4Free provider for free LLM access.
    
    Uses various free providers through g4f library.
    https://github.com/xtekky/gpt4free
    """
    
    def __init__(self, provider_name: Optional[str] = None):
        self.provider_name = provider_name
        self._g4f = None
    
    def _get_g4f(self):
        """Lazy load g4f to avoid import errors if not installed."""
        if self._g4f is None:
            try:
                import g4f
                self._g4f = g4f
            except ImportError:
                raise ImportError(
                    "g4f not installed. Run: pip install -U g4f"
                )
        return self._g4f
    
    async def complete(
        self,
        prompt: str,
        config: LLMConfig
    ) -> LLMResponse:
        """Send completion request through GPT4Free."""
        
        import time
        start_time = time.time()
        
        g4f = self._get_g4f()
        
        messages = []
        if config.system_prompt:
            messages.append({
                "role": "system",
                "content": config.system_prompt
            })
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        try:
            # Get provider if specified
            provider = None
            if self.provider_name:
                provider = getattr(g4f.Provider, self.provider_name, None)
            
            # Use async create
            response = await g4f.ChatCompletion.create_async(
                model=config.model if config.model else "gpt-3.5-turbo",
                messages=messages,
                provider=provider,
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            # g4f returns string directly
            content = response if isinstance(response, str) else str(response)
            
            return LLMResponse(
                content=content,
                model=config.model or "gpt-3.5-turbo",
                provider=f"g4f:{self.provider_name or 'auto'}",
                temperature=config.temperature,
                tokens_used=0,  # g4f doesn't report token usage
                latency_ms=latency_ms,
            )
            
        except Exception as e:
            logger.error(f"GPT4Free error: {e}")
            return LLMResponse(
                content="",
                model=config.model or "gpt-3.5-turbo",
                provider=f"g4f:{self.provider_name or 'auto'}",
                temperature=config.temperature,
                tokens_used=0,
                latency_ms=(time.time() - start_time) * 1000,
                error=str(e)
            )
    
    async def health_check(self) -> bool:
        """Check if GPT4Free provider is working."""
        try:
            response = await self.complete(
                "Say 'ok' if you're working.",
                LLMConfig(model="gpt-3.5-turbo", max_tokens=10)
            )
            return response.success
        except Exception:
            return False


# ============================================================================
#                    PROVIDER MANAGER
# ============================================================================

class ProviderManager:
    """
    Manages multiple LLM providers with fallback support.
    
    Provides unified interface for:
    - Multiple providers (OpenRouter, GPT4Free)
    - Multiple models per provider
    - Temperature/quantization variations
    - Automatic fallback on failure
    - Rate limiting and retries
    """
    
    def __init__(self):
        self.providers: Dict[str, BaseLLMProvider] = {}
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize all configured providers."""
        
        # OpenRouter (primary)
        if settings.openrouter_api_key:
            self.providers["openrouter"] = OpenRouterProvider()
            logger.info("OpenRouter provider initialized")
        
        # GPT4Free providers
        g4f_providers = ["Bing", "You", "Phind", "DeepInfra", "Groq"]
        for provider_name in g4f_providers:
            try:
                self.providers[f"g4f:{provider_name}"] = GPT4FreeProvider(provider_name)
                logger.info(f"GPT4Free:{provider_name} provider initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize g4f:{provider_name}: {e}")
    
    def get_provider(self, provider_key: str) -> Optional[BaseLLMProvider]:
        """Get a specific provider."""
        return self.providers.get(provider_key)
    
    async def complete_with_fallback(
        self,
        prompt: str,
        configs: List[LLMConfig],
        fallback_order: Optional[List[str]] = None
    ) -> LLMResponse:
        """
        Try completion with fallback chain.
        
        Args:
            prompt: The prompt to send
            configs: List of LLMConfig to try (in order)
            fallback_order: Optional provider order for fallback
        
        Returns:
            First successful LLMResponse, or last failed response
        """
        
        if fallback_order is None:
            fallback_order = list(self.providers.keys())
        
        last_response = None
        
        for config in configs:
            for provider_key in fallback_order:
                provider = self.providers.get(provider_key)
                if provider is None:
                    continue
                
                response = await provider.complete(prompt, config)
                
                if response.success:
                    return response
                
                last_response = response
                logger.warning(
                    f"Provider {provider_key} failed for {config.model}: {response.error}"
                )
        
        # Return last failed response
        return last_response or LLMResponse(
            content="",
            model="unknown",
            provider="none",
            temperature=0,
            tokens_used=0,
            latency_ms=0,
            error="No providers available"
        )
    
    async def complete_parallel(
        self,
        prompt: str,
        configs: List[LLMConfig]
    ) -> List[LLMResponse]:
        """
        Send same prompt to multiple models in parallel.
        
        Useful for verification (multiple independent coders).
        """
        
        tasks = []
        
        for config in configs:
            if config.provider == LLMProvider.OPENROUTER:
                provider = self.providers.get("openrouter")
            else:
                provider = self.providers.get(f"g4f:{config.model}")
            
            if provider:
                tasks.append(provider.complete(prompt, config))
        
        if not tasks:
            return []
        
        return await asyncio.gather(*tasks, return_exceptions=True)
    
    async def health_check_all(self) -> Dict[str, bool]:
        """Check health of all providers."""
        results = {}
        
        for key, provider in self.providers.items():
            try:
                results[key] = await provider.health_check()
            except Exception:
                results[key] = False
        
        return results


# ============================================================================
#                    MODEL CONFIGURATIONS
# ============================================================================

def get_verification_configs() -> List[LLMConfig]:
    """
    Get configurations for triple verification.
    
    Uses 3 different models to independently score each test.
    """
    return [
        LLMConfig(
            model="anthropic/claude-3.5-sonnet",
            temperature=0.3,
            provider=LLMProvider.OPENROUTER
        ),
        LLMConfig(
            model="openai/gpt-4-turbo",
            temperature=0.3,
            provider=LLMProvider.OPENROUTER
        ),
        LLMConfig(
            model="google/gemini-pro-1.5",
            temperature=0.3,
            provider=LLMProvider.OPENROUTER
        ),
    ]


def get_temperature_sweep_configs(model: str) -> List[LLMConfig]:
    """
    Get configurations for temperature sweep.
    
    Same model at different temperatures to test stability.
    """
    temperatures = [0.0, 0.3, 0.5, 0.7, 1.0]
    
    return [
        LLMConfig(
            model=model,
            temperature=t,
            provider=LLMProvider.OPENROUTER
        )
        for t in temperatures
    ]


def get_model_comparison_configs() -> List[LLMConfig]:
    """
    Get configurations for comparing different models.
    """
    models = [
        "anthropic/claude-3.5-sonnet",
        "anthropic/claude-3-opus",
        "openai/gpt-4-turbo",
        "openai/gpt-4o",
        "google/gemini-pro-1.5",
        "meta-llama/llama-3.1-405b-instruct",
        "mistralai/mistral-large",
    ]
    
    return [
        LLMConfig(model=m, temperature=0.5, provider=LLMProvider.OPENROUTER)
        for m in models
    ]


# ============================================================================
#                    SINGLETON INSTANCE
# ============================================================================

# Global provider manager
_provider_manager: Optional[ProviderManager] = None


def get_provider_manager() -> ProviderManager:
    """Get or create the global provider manager."""
    global _provider_manager
    if _provider_manager is None:
        _provider_manager = ProviderManager()
    return _provider_manager


# ============================================================================
#                    EXPORTS
# ============================================================================

__all__ = [
    "LLMResponse",
    "LLMConfig",
    "LLMProvider",
    "BaseLLMProvider",
    "OpenRouterProvider",
    "GPT4FreeProvider",
    "ProviderManager",
    "get_provider_manager",
    "get_verification_configs",
    "get_temperature_sweep_configs",
    "get_model_comparison_configs",
]
