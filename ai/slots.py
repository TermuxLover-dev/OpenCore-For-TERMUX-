from dataclasses import dataclass, field, asdict
from typing import Dict, Optional

@dataclass
class AISlot:
    provider: str
    api_key: str
    base_url: str
    model_name: str
    temperature: float = 0.2
    max_tokens: int = 4096
    tool_permissions_profile: str = "full"
    enabled: bool = True

    def to_dict(self) -> Dict:
        return asdict(self)

class SlotManager:
    def __init__(self, config: Dict):
        self.config = config
        self.slots: Dict[str, AISlot] = {}
        self._load_slots()

    def _load_slots(self):
        for slot_name, data in self.config.get("ai_slots", {}).items():
            self.slots[slot_name] = AISlot(**data)

    def get_active(self) -> AISlot:
        active = self.config.get("active_slot", "ai1")
        return self.slots.get(active)

    def switch_active(self, slot_name: str) -> bool:
        if slot_name in self.slots and self.slots[slot_name].enabled:
            self.config["active_slot"] = slot_name
            from config.settings import save_config
            save_config(self.config)
            return True
        return False

    def toggle_slot(self, slot_name: str, enabled: bool):
        if slot_name in self.slots:
            self.slots[slot_name].enabled = enabled
            self.config["ai_slots"][slot_name]["enabled"] = enabled
            from config.settings import save_config
            save_config(self.config)
