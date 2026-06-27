from abc import ABC, abstractmethod
from typing import Optional, Tuple
import requests


class AIProvider(ABC):
    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> Tuple[str, int, int]:
        """Returns (content, prompt_tokens, completion_tokens)."""
        ...

    @abstractmethod
    def is_available(self) -> bool: ...

    @property
    @abstractmethod
    def provider_name(self) -> str: ...

    @property
    @abstractmethod
    def model_name(self) -> str: ...


class OpenAIProvider(AIProvider):
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        self._api_key = api_key
        self._model = model

    @property
    def provider_name(self) -> str:
        return "openai"

    @property
    def model_name(self) -> str:
        return self._model

    def generate(self, prompt, system_prompt=None, temperature=0.7, max_tokens=4096):
        import openai
        client = openai.OpenAI(api_key=self._api_key)
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        response = client.chat.completions.create(
            model=self._model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        content = response.choices[0].message.content or ""
        usage = response.usage
        return content, usage.prompt_tokens, usage.completion_tokens

    def generate_image(self, prompt: str, size: str = "1792x1024") -> str:
        """Returns base64-encoded PNG image."""
        import openai, base64
        client = openai.OpenAI(api_key=self._api_key)
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=size,
            quality="hd",
            response_format="b64_json",
            n=1,
        )
        return response.data[0].b64_json or ""

    def is_available(self) -> bool:
        return bool(self._api_key)


class ClaudeProvider(AIProvider):
    MODELS = [
        "claude-3-5-sonnet-20241022",
        "claude-3-5-haiku-20241022",
        "claude-3-opus-20240229",
    ]

    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022"):
        self._api_key = api_key
        self._model = model

    @property
    def provider_name(self) -> str:
        return "claude"

    @property
    def model_name(self) -> str:
        return self._model

    def generate(self, prompt, system_prompt=None, temperature=0.7, max_tokens=4096):
        import anthropic
        client = anthropic.Anthropic(api_key=self._api_key)
        kwargs: dict = {
            "model": self._model,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
        }
        if system_prompt:
            kwargs["system"] = system_prompt
        response = client.messages.create(**kwargs)
        content = response.content[0].text
        usage = response.usage
        return content, usage.input_tokens, usage.output_tokens

    def is_available(self) -> bool:
        return bool(self._api_key)


class GeminiProvider(AIProvider):
    def __init__(self, api_key: str, model: str = "gemini-1.5-pro"):
        self._api_key = api_key
        self._model = model

    @property
    def provider_name(self) -> str:
        return "gemini"

    @property
    def model_name(self) -> str:
        return self._model

    def generate(self, prompt, system_prompt=None, temperature=0.7, max_tokens=4096):
        import google.generativeai as genai
        genai.configure(api_key=self._api_key)
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        model = genai.GenerativeModel(self._model)
        cfg = genai.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        )
        response = model.generate_content(full_prompt, generation_config=cfg)
        return response.text, 0, 0

    def is_available(self) -> bool:
        return bool(self._api_key)


class OllamaProvider(AIProvider):
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.2"):
        self._base_url = base_url.rstrip("/")
        self._model = model

    @property
    def provider_name(self) -> str:
        return "ollama"

    @property
    def model_name(self) -> str:
        return self._model

    def generate(self, prompt, system_prompt=None, temperature=0.7, max_tokens=4096):
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        resp = requests.post(
            f"{self._base_url}/api/chat",
            json={
                "model": self._model,
                "messages": messages,
                "options": {"temperature": temperature, "num_predict": max_tokens},
                "stream": False,
            },
            timeout=180,
        )
        resp.raise_for_status()
        data = resp.json()
        content = data.get("message", {}).get("content", "")
        return content, 0, 0

    def list_local_models(self) -> list:
        try:
            resp = requests.get(f"{self._base_url}/api/tags", timeout=5)
            resp.raise_for_status()
            return [m["name"] for m in resp.json().get("models", [])]
        except Exception:
            return []

    def is_available(self) -> bool:
        try:
            resp = requests.get(f"{self._base_url}/api/tags", timeout=3)
            return resp.status_code == 200
        except Exception:
            return False


def create_provider(config) -> AIProvider:
    name = config.get("ai_provider", "openai")
    if name == "openai":
        return OpenAIProvider(
            api_key=config.get("openai_api_key", ""),
            model=config.get("ai_model", "gpt-4o"),
        )
    if name == "claude":
        return ClaudeProvider(
            api_key=config.get("anthropic_api_key", ""),
            model=config.get("ai_model", "claude-3-5-sonnet-20241022"),
        )
    if name == "gemini":
        return GeminiProvider(
            api_key=config.get("gemini_api_key", ""),
            model=config.get("ai_model", "gemini-1.5-pro"),
        )
    if name == "ollama":
        return OllamaProvider(
            base_url=config.get("ollama_base_url", "http://localhost:11434"),
            model=config.get("ollama_model", "llama3.2"),
        )
    return OpenAIProvider(api_key=config.get("openai_api_key", ""))


OPENAI_MODELS = ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"]
CLAUDE_MODELS = [
    "claude-3-5-sonnet-20241022",
    "claude-3-5-haiku-20241022",
    "claude-3-opus-20240229",
]
GEMINI_MODELS = ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-pro"]
