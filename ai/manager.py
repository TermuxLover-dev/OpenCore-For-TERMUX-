import json, re
from typing import Dict
from ai.slots import SlotManager
from ai.providers import create_provider

class AIManager:
    def __init__(self, config: Dict):
        self.config = config
        self.slot_manager = SlotManager(config)

    async def get_active_provider(self):
        slot = self.slot_manager.get_active()
        if not slot or not slot.enabled:
            raise ValueError("No active AI slot available.")
        return create_provider(slot)

    def _clean_response(self, text: str) -> Dict:
        if not isinstance(text, str):
            if isinstance(text, dict) and "content" in text:
                return {"mode": "text", "content": str(text["content"])}
            return {"mode": "text", "content": str(text)}
        try:
            parsed = json.loads(text)
            if isinstance(parsed, dict):
                if "content" in parsed:
                    return {"mode": "text", "content": str(parsed["content"])}
                if "actions" in parsed or "project" in parsed:
                    return parsed
            return {"mode": "text", "content": text}
        except json.JSONDecodeError:
            start = text.find('{'); end = text.rfind('}')
            if start != -1 and end != -1:
                try:
                    parsed = json.loads(text[start:end+1])
                    if "content" in parsed:
                        return {"mode": "text", "content": str(parsed["content"])}
                    if "actions" in parsed:
                        return parsed
                except:
                    pass
        return {"mode": "text", "content": text}

    async def send_prompt(self, system_prompt: str, user_content: str) -> Dict:
        provider = await self.get_active_provider()
        messages = provider.build_messages(system_prompt, user_content)
        raw = await provider.chat(messages)
        return self._clean_response(raw)
