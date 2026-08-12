import os
import litellm
from litellm import completion, batch_completion
from litellm.caching import Cache
from g4f.client import ClientFactory
from gpt4all import GPT4All

"""
hub = APIHub()

# 1-9. Standard APIs (OpenRouter, Deepseek, OpenAI, Anthropic, etc.)
# Litellm syntax: "provider/model" (e.g., "openrouter/anthropic/claude-3-haiku")
res_standard = hub.generate(
    model="deepseek/deepseek-chat", 
    messages=[{"role": "user", "content": "Hello!"}]
)

# 10. G4F
res_g4f = hub.generate(
    model="model-router", 
    messages=[{"role": "user", "content": "Explain quantum computing"}],
    provider="g4f",
    g4f_provider="azure"
)

# 2. Local
res_local = hub.generate(
    model="orca-mini-3b-gguf2-q4_0.gguf", 
    messages=[{"role": "user", "content": "Hi"}],
    provider="local"
)

# Batch standard
batch_res = hub.batch_generate(
    model="gpt-4o-mini",
    list_of_messages=[[{"role": "user", "content": "1+1"}], [{"role": "user", "content": "2+2"}]]
)

hub = APIHub()

# 1. Standard Paid Call
res_openai = hub.generate("gpt-4o-mini", [{"role": "user", "content": "Explain OOP"}])

# 2. Free G4F Call (Tokens might update, cost remains +$0.00)
res_g4f = hub.generate("model-router", [{"role": "user", "content": "Hello"}], provider="g4f")

# 3. View tracked statistics
hub.print_stats()



hub = APIHub()

# Use aliases directly for free NeurIPS-grade reasoning
res1 = hub.generate("deepseek-free", [{"role": "user", "content": "Analyze the trolley problem."}])
res2 = hub.generate("llama-free", [{"role": "user", "content": "Explain Kantian ethics."}])
res3 = hub.generate("gpt4-free", [{"role": "user", "content": "What is an ontological hole?"}])

hub.print_stats()
"""

# Map your custom keys to litellm standard environment variables
os.environ["OPENAI_API_KEY"] = os.getenv("OPEN_AI_KEY", "")
os.environ["ANTHROPIC_API_KEY"] = os.getenv("ANTHROPIC_AI_KEY", "")
os.environ["DEEPSEEK_API_KEY"] = os.getenv("DEEPSEEK_AI_KEY", "")
os.environ["PERPLEXITY_API_KEY"] = os.getenv("PERPLEXITY_AI_KEY", "")
os.environ["GROQ_API_KEY"] = os.getenv("GROK_AI_KEY1", "") # Or GROK_AI_KEY2
os.environ["OPENROUTER_API_KEY"] = os.getenv("OPENROUTER_API", "")
os.environ["GEMINI_API_KEY"] = os.getenv("GOOGLE_API_KEY", "")
# Gemini uses GEMINI_API_KEY, Ollama uses OLLAMA_API_BASE if remote

class APIHub:
    # Quick-access aliases for NeurIPS-grade free/cheap models
    MODEL_ALIASES = {
        "llama-free": {"model": "groq/llama-3.3-70b-versatile", "provider": "standard"},
        "gemini-free": {"model": "gemini/gemini-1.5-flash", "provider": "standard"},
        "deepseek-free": {"model": "openrouter/deepseek/deepseek-r1:free", "provider": "standard"},
        "qwen-free": {"model": "openrouter/qwen/qwen-2.5-72b-instruct:free", "provider": "standard"},
        "gpt4-free": {"model": "gpt-4", "provider": "g4f"},
        "gpt-4o-mini": {"model": "gpt-4o-mini", "provider": "standard"} # Ultra-cheap paid
    }

    def __init__(self, cache_type="local"):
        # 0. Optimization: Enable caching
        litellm.cache = Cache(type=cache_type)
        self.g4f_client = None

        # Telemetry counter
        self.stats = {
            "total_calls": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_cost_usd": 0.0
        }

    def _update_telemetry(self, response, provider_type="standard"):
        self.stats["total_calls"] += 1
        
        if provider_type == "standard" and hasattr(response, "usage"):
            self.stats["prompt_tokens"] += response.usage.prompt_tokens
            self.stats["completion_tokens"] += response.usage.completion_tokens
            
            # litellm calculates precise cost based on model pricing lists
            try:
                self.stats["total_cost_usd"] += completion_cost(completion_response=response)
            except Exception:
                pass 
        elif provider_type == "g4f" and hasattr(response, "usage") and response.usage:
            # G4F occasionally returns token counts, but cost is $0
            self.stats["prompt_tokens"] += getattr(response.usage, "prompt_tokens", 0)
            self.stats["completion_tokens"] += getattr(response.usage, "completion_tokens", 0)

    def _get_g4f_client(self, provider="azure", api_key=None):
        if not self.g4f_client:
            if api_key:
                self.g4f_client = ClientFactory.create_client(provider, api_key=api_key)
            else:
                self.g4f_client = ClientFactory.create_client(provider)
        return self.g4f_client

    def generate(self, model, messages, provider="standard", g4f_provider="azure", **kwargs):
        # Resolve alias if used
        if model in self.MODEL_ALIASES:
            provider = self.MODEL_ALIASES[model]["provider"]
            model = self.MODEL_ALIASES[model]["model"]

        if provider == "standard":
            response = completion(model=model, messages=messages, **kwargs)
            self._update_telemetry(response, "standard")
            return response.choices[0].message.content

        elif provider == "g4f":
            client = self._get_g4f_client(provider=g4f_provider)
            response = client.chat.completions.create(model=model, messages=messages, **kwargs)
            self._update_telemetry(response, "g4f")
            return response.choices[0].message.content

        elif provider == "local":
            local_model = GPT4All(model) 
            prompt = "\n".join([m["content"] for m in messages])
            self.stats["total_calls"] += 1
            return local_model.generate(prompt)

    def batch_generate(self, model, list_of_messages, provider="standard", **kwargs):
        if model in self.MODEL_ALIASES:
            provider = self.MODEL_ALIASES[model]["provider"]
            model = self.MODEL_ALIASES[model]["model"]

        """
        0. Batching calls
        """
        if provider == "standard":
            responses = batch_completion(model=model, messages=list_of_messages, **kwargs)
            for r in responses:
                self._update_telemetry(r, "standard")
            return [r.choices[0].message.content for r in responses]
        else:
            # Fallback sequential for g4f/local
            return [self.generate(model, msgs, provider, **kwargs) for msgs in list_of_messages]

    def get_free_openrouter_models():
    res = requests.get("https://openrouter.ai/api/v1/models").json()
    return [
        m["id"] for m in res.get("data", []) 
        if float(m["pricing"]["prompt"]) == 0 and float(m["pricing"]["completion"]) == 0
    ]

    def print_stats(self):
        print("\n" + "="*30)
        print("📊 API Hub Telemetry")
        print("="*30)
        print(f"Total Calls:      {self.stats['total_calls']}")
        print(f"Prompt Tokens:    {self.stats['prompt_tokens']}")
        print(f"Completed Tokens: {self.stats['completion_tokens']}")
        print(f"Total Cost:       ${self.stats['total_cost_usd']:.6f}")
        print("="*30 + "\n")

    @staticmethod
    def get_g4f_providers():
        return [
            "pollinations", "api.airforce", "master", "audio", 
            "azure", "custom", "deepinfra", "gemini", "groq", 
            "huggingface", "nvidia", "ollama", "openrouter", 
            "puter", "perplexity"
        ]