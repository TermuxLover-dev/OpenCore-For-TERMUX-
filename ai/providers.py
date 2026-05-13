import json, asyncio, urllib.request, urllib.error
from typing import Dict, List

class BaseProvider:
    def __init__(self, slot):
        self.slot = slot
        self.api_key = slot.api_key
        self.base_url = slot.base_url.rstrip("/")
        self.model = slot.model_name
        self.temperature = slot.temperature
        self.max_tokens = slot.max_tokens

    def _request(self, url, payload, extra_headers=None):
        headers = {"Content-Type": "application/json"}
        if extra_headers:
            headers.update(extra_headers)
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            body = e.read().decode()
            raise RuntimeError(f"HTTP {e.code}: {body[:500]}")
        except Exception as e:
            raise RuntimeError(f"Request failed: {str(e)}")

    async def _post(self, url, payload, extra_headers=None):
        return await asyncio.to_thread(self._request, url, payload, extra_headers)

    def build_messages(self, system_prompt, user_content):
        return [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_content}]

    async def chat(self, messages):
        raise NotImplementedError


class OpenAIProvider(BaseProvider):
    async def chat(self, messages):
        url = f"{self.base_url}/chat/completions"
        payload = {"model": self.model, "messages": messages, "temperature": self.temperature, "max_tokens": self.max_tokens}
        headers = {"Authorization": f"Bearer {self.api_key}"}
        resp = await self._post(url, payload, headers)
        return resp["choices"][0]["message"]["content"]


class OpenRouterProvider(BaseProvider):
    async def chat(self, messages):
        url = f"{self.base_url}/chat/completions"
        payload = {"model": self.model, "messages": messages, "temperature": self.temperature, "max_tokens": self.max_tokens}
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "http://openclaw.local",
            "X-Title": "OpenClaw Agent"
        }
        resp = await self._post(url, payload, headers)
        return resp["choices"][0]["message"]["content"]


class GeminiProvider(BaseProvider):
    async def chat(self, messages):
        url = f"{self.base_url}/models/{self.model}:generateContent?key={self.api_key}"
        sys_msg = next((m for m in messages if m["role"] == "system"), None)
        history = []
        for m in messages:
            if m["role"] == "system": continue
            role = "user" if m["role"] == "user" else "model"
            history.append({"role": role, "parts": [{"text": m["content"]}]})
        payload = {"contents": history, "generationConfig": {"temperature": self.temperature, "maxOutputTokens": self.max_tokens}}
        if sys_msg:
            payload["systemInstruction"] = {"parts": [{"text": sys_msg["content"]}]}
        resp = await self._post(url, payload)
        return resp["candidates"][0]["content"]["parts"][0]["text"]


class GroqProvider(BaseProvider):
    async def chat(self, messages):
        url = f"{self.base_url}/chat/completions"
        payload = {"model": self.model, "messages": messages, "temperature": self.temperature, "max_tokens": self.max_tokens}
        headers = {"Authorization": f"Bearer {self.api_key}"}
        resp = await self._post(url, payload, headers)
        return resp["choices"][0]["message"]["content"]


class DeepSeekProvider(OpenAIProvider):
    # DeepSeek is OpenAI‑compatible, uses the same API structure
    pass


def create_provider(slot):
    provider_map = {
        "openai": OpenAIProvider,
        "openrouter": OpenRouterProvider,
        "gemini": GeminiProvider,
        "groq": GroqProvider,
        "deepseek": DeepSeekProvider,
        "custom": OpenAIProvider     # custom = generic OpenAI‑compatible
    }
    cls = provider_map.get(slot.provider.lower())
    if cls is None:
        raise ValueError(f"Unknown provider: {slot.provider}. Supported: openrouter, gemini, groq, deepseek, custom")
    return cls(slot)
