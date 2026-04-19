"""
Baseline Methods for CogOS Comparison

Implements all baseline methods:
- GPT-4 Vanilla
- Chain-of-Thought (CoT)
- ReAct
- Constitutional AI
- Chain-of-Verification (CoVe)
- RLHF (proxy via GPT-4)
"""

import os
import json
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from pathlib import Path


@dataclass
class BaselineOutput:
    """Output from a baseline method."""
    answer: str
    confidence: float
    tokens_used: int
    latency_seconds: float
    method: str
    metadata: Dict[str, Any]


class BaselineMethod(ABC):
    """Abstract base class for baseline methods."""
    
    def __init__(self, model: str = "gpt-4-turbo-preview", api_key: Optional[str] = None):
        self.model = model
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = None
        self._setup_client()
        
    def _setup_client(self):
        """Setup API client."""
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
        except ImportError:
            print("Warning: OpenAI not installed. Run: pip install openai")
            
    @abstractmethod
    def process(self, query: str, context: Optional[Dict] = None) -> BaselineOutput:
        """Process query and return output."""
        pass
    
    def _call_llm(self, messages: List[Dict], **kwargs) -> Dict:
        """Call LLM API."""
        if self.client is None:
            # Return mock response for testing
            return {
                "content": "[Mock response - OpenAI not configured]",
                "tokens": 100,
                "latency": 0.5
            }
            
        start_time = time.time()
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            **kwargs
        )
        latency = time.time() - start_time
        
        return {
            "content": response.choices[0].message.content,
            "tokens": response.usage.total_tokens,
            "latency": latency
        }


class VanillaBaseline(BaselineMethod):
    """Standard prompting baseline (GPT-4)."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.method_name = "gpt4_baseline"
        
    def process(self, query: str, context: Optional[Dict] = None) -> BaselineOutput:
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": query}
        ]
        
        result = self._call_llm(messages)
        
        return BaselineOutput(
            answer=result["content"],
            confidence=0.7,  # Default confidence
            tokens_used=result["tokens"],
            latency_seconds=result["latency"],
            method=self.method_name,
            metadata={"context": context}
        )


class ChainOfThoughtBaseline(BaselineMethod):
    """Chain-of-Thought prompting baseline."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.method_name = "cot"
        
    def process(self, query: str, context: Optional[Dict] = None) -> BaselineOutput:
        messages = [
            {"role": "system", "content": "You are a helpful assistant that thinks step by step."},
            {"role": "user", "content": f"{query}\n\nLet's think step by step."}
        ]
        
        result = self._call_llm(messages)
        
        return BaselineOutput(
            answer=result["content"],
            confidence=0.75,
            tokens_used=result["tokens"],
            latency_seconds=result["latency"],
            method=self.method_name,
            metadata={"context": context, "reasoning_type": "step_by_step"}
        )


class ReActBaseline(BaselineMethod):
    """ReAct (Reasoning + Acting) baseline."""
    
    def __init__(self, max_steps: int = 10, **kwargs):
        super().__init__(**kwargs)
        self.method_name = "react"
        self.max_steps = max_steps
        
    def process(self, query: str, context: Optional[Dict] = None) -> BaselineOutput:
        react_prompt = """You are an AI that reasons and acts to solve problems.

For each step, use this format:
Thought: [your reasoning]
Action: [action to take]
Observation: [result of action]

Continue until you reach a final answer.

Question: {query}

Begin:"""

        messages = [
            {"role": "system", "content": "You are a ReAct agent that reasons and acts."},
            {"role": "user", "content": react_prompt.format(query=query)}
        ]
        
        result = self._call_llm(messages, max_tokens=2000)
        
        return BaselineOutput(
            answer=result["content"],
            confidence=0.78,
            tokens_used=result["tokens"],
            latency_seconds=result["latency"],
            method=self.method_name,
            metadata={"context": context, "max_steps": self.max_steps}
        )


class ConstitutionalAIBaseline(BaselineMethod):
    """Constitutional AI baseline (Anthropic-style)."""
    
    def __init__(self, principles_file: Optional[str] = None, **kwargs):
        # Use Claude for Constitutional AI
        kwargs["model"] = kwargs.get("model", "claude-3-opus-20240229")
        super().__init__(**kwargs)
        self.method_name = "constitutional_ai"
        
        # Load principles
        self.principles = self._load_principles(principles_file)
        
    def _load_principles(self, filepath: Optional[str]) -> List[str]:
        """Load constitutional principles."""
        default_principles = [
            "Be helpful, harmless, and honest.",
            "Avoid generating harmful or misleading content.",
            "Respect human autonomy and dignity.",
            "Be transparent about limitations and uncertainties.",
            "Consider diverse perspectives and potential impacts."
        ]
        
        if filepath and Path(filepath).exists():
            with open(filepath) as f:
                data = json.load(f)
                return data.get("principles", default_principles)
                
        return default_principles
    
    def _setup_client(self):
        """Setup Anthropic client."""
        try:
            from anthropic import Anthropic
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if api_key:
                self.client = Anthropic(api_key=api_key)
        except ImportError:
            print("Warning: Anthropic not installed. Run: pip install anthropic")
            
    def _call_llm(self, messages: List[Dict], **kwargs) -> Dict:
        """Call Claude API."""
        if self.client is None:
            return {
                "content": "[Mock response - Anthropic not configured]",
                "tokens": 150,
                "latency": 0.6
            }
            
        start_time = time.time()
        
        # Format for Claude
        system = messages[0]["content"] if messages[0]["role"] == "system" else ""
        user_messages = [m for m in messages if m["role"] != "system"]
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=kwargs.get("max_tokens", 1024),
            system=system,
            messages=user_messages
        )
        latency = time.time() - start_time
        
        return {
            "content": response.content[0].text,
            "tokens": response.usage.input_tokens + response.usage.output_tokens,
            "latency": latency
        }
        
    def process(self, query: str, context: Optional[Dict] = None) -> BaselineOutput:
        principles_text = "\n".join(f"- {p}" for p in self.principles)
        
        system_prompt = f"""You are a helpful AI assistant guided by the following constitutional principles:

{principles_text}

Always consider these principles when responding."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ]
        
        result = self._call_llm(messages)
        
        return BaselineOutput(
            answer=result["content"],
            confidence=0.80,
            tokens_used=result["tokens"],
            latency_seconds=result["latency"],
            method=self.method_name,
            metadata={"context": context, "principles": self.principles}
        )


class CoVeBaseline(BaselineMethod):
    """Chain-of-Verification baseline (Google-style)."""
    
    def __init__(self, verification_rounds: int = 3, **kwargs):
        super().__init__(**kwargs)
        self.method_name = "cove"
        self.verification_rounds = verification_rounds
        
    def process(self, query: str, context: Optional[Dict] = None) -> BaselineOutput:
        # Step 1: Generate initial response
        initial_messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": query}
        ]
        initial_result = self._call_llm(initial_messages)
        initial_answer = initial_result["content"]
        
        total_tokens = initial_result["tokens"]
        total_latency = initial_result["latency"]
        
        # Step 2: Generate verification questions
        verification_prompt = f"""Given this answer to a question, generate {self.verification_rounds} verification questions to check its accuracy:

Question: {query}
Answer: {initial_answer}

Generate verification questions:"""

        verification_messages = [
            {"role": "system", "content": "You generate verification questions."},
            {"role": "user", "content": verification_prompt}
        ]
        ver_result = self._call_llm(verification_messages)
        total_tokens += ver_result["tokens"]
        total_latency += ver_result["latency"]
        
        # Step 3: Final verified response
        final_prompt = f"""Original question: {query}
Original answer: {initial_answer}
Verification analysis: {ver_result["content"]}

Based on this verification, provide your final, verified answer:"""

        final_messages = [
            {"role": "system", "content": "You provide verified, accurate answers."},
            {"role": "user", "content": final_prompt}
        ]
        final_result = self._call_llm(final_messages)
        total_tokens += final_result["tokens"]
        total_latency += final_result["latency"]
        
        return BaselineOutput(
            answer=final_result["content"],
            confidence=0.85,
            tokens_used=total_tokens,
            latency_seconds=total_latency,
            method=self.method_name,
            metadata={
                "context": context,
                "verification_rounds": self.verification_rounds,
                "initial_answer": initial_answer,
                "verification": ver_result["content"]
            }
        )


class RLHFBaseline(BaselineMethod):
    """RLHF baseline (using GPT-4 as proxy)."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.method_name = "rlhf"
        
    def process(self, query: str, context: Optional[Dict] = None) -> BaselineOutput:
        # GPT-4 is trained with RLHF, so we use it directly
        # with a prompt that emphasizes helpfulness and safety
        
        messages = [
            {"role": "system", "content": """You are a helpful, harmless, and honest AI assistant.
Your responses should be:
- Helpful and informative
- Safe and avoiding harmful content
- Honest about uncertainties
- Respectful and considerate"""},
            {"role": "user", "content": query}
        ]
        
        result = self._call_llm(messages)
        
        return BaselineOutput(
            answer=result["content"],
            confidence=0.82,
            tokens_used=result["tokens"],
            latency_seconds=result["latency"],
            method=self.method_name,
            metadata={"context": context, "note": "GPT-4 as RLHF proxy"}
        )


class BaselineRunner:
    """Run all baselines on a dataset."""
    
    def __init__(self, save_dir: str = "./baselines/results"):
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize baselines
        self.baselines = {
            "gpt4_baseline": VanillaBaseline(),
            "cot": ChainOfThoughtBaseline(),
            "react": ReActBaseline(),
            "constitutional_ai": ConstitutionalAIBaseline(),
            "cove": CoVeBaseline(),
            "rlhf": RLHFBaseline()
        }
        
    def run_single(self, query: str, method: str = "all") -> Dict[str, BaselineOutput]:
        """Run baselines on a single query."""
        results = {}
        
        methods = self.baselines.keys() if method == "all" else [method]
        
        for m in methods:
            if m in self.baselines:
                try:
                    results[m] = self.baselines[m].process(query)
                except Exception as e:
                    print(f"Error running {m}: {e}")
                    
        return results
    
    def run_dataset(self, 
                    dataset: List[Dict],
                    dataset_name: str,
                    methods: List[str] = None) -> Dict[str, List[BaselineOutput]]:
        """Run baselines on entire dataset."""
        if methods is None:
            methods = list(self.baselines.keys())
            
        results = {m: [] for m in methods}
        
        for i, item in enumerate(dataset):
            query = item.get("question") or item.get("text") or item.get("prompt")
            
            print(f"Processing {i+1}/{len(dataset)}: {query[:50]}...")
            
            for method in methods:
                try:
                    output = self.baselines[method].process(query, context=item)
                    results[method].append(output)
                except Exception as e:
                    print(f"  Error with {method}: {e}")
                    
            # Rate limiting
            time.sleep(0.5)
            
        # Save results
        self._save_results(results, dataset_name)
        
        return results
    
    def _save_results(self, results: Dict[str, List[BaselineOutput]], dataset_name: str):
        """Save results to disk."""
        for method, outputs in results.items():
            save_path = self.save_dir / f"{dataset_name}_{method}.json"
            
            data = []
            for output in outputs:
                data.append({
                    "answer": output.answer,
                    "confidence": output.confidence,
                    "tokens_used": output.tokens_used,
                    "latency_seconds": output.latency_seconds,
                    "method": output.method,
                    "metadata": output.metadata
                })
                
            with open(save_path, "w") as f:
                json.dump(data, f, indent=2)
                
            print(f"Saved: {save_path}")
            
    def load_results(self, dataset_name: str, method: str) -> List[Dict]:
        """Load previously saved results."""
        path = self.save_dir / f"{dataset_name}_{method}.json"
        if path.exists():
            with open(path) as f:
                return json.load(f)
        return []


if __name__ == "__main__":
    # Test baselines
    print("Testing Baselines...")
    
    runner = BaselineRunner()
    
    test_query = "Is it ethical to lie to protect someone's feelings?"
    
    print(f"\nQuery: {test_query}\n")
    
    results = runner.run_single(test_query)
    
    for method, output in results.items():
        print(f"\n{'='*60}")
        print(f"Method: {method}")
        print(f"Confidence: {output.confidence:.2f}")
        print(f"Tokens: {output.tokens_used}")
        print(f"Latency: {output.latency_seconds:.2f}s")
        print(f"Answer: {output.answer[:200]}...")
        
    print("\n✅ Baseline tests complete!")
