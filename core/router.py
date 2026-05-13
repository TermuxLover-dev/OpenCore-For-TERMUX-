from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

@dataclass
class ExecutionPlan:
    intent: str
    steps: List[str] = field(default_factory=list)
    tools: List[str] = field(default_factory=list)
    risk_level: RiskLevel = RiskLevel.LOW
    requires_confirmation: bool = False

class Router:
    def __init__(self, agent):
        self.agent = agent

    def parse(self, user_input: str) -> Optional[ExecutionPlan]:
        inp = user_input.strip()
        if inp.startswith("/"):
            parts = inp.split(maxsplit=1)
            cmd = parts[0].lower()
            arg = parts[1] if len(parts) > 1 else ""
            return self._handle_command(cmd, arg)
        return ExecutionPlan(
            intent="chat",
            steps=[inp],
            tools=["ai"],
            risk_level=RiskLevel.LOW,
            requires_confirmation=False
        )

    def _handle_command(self, cmd: str, arg: str) -> Optional[ExecutionPlan]:
        mapping = {
            "/build": ("build", ["file_creation"]),
            "/edit": ("edit", ["file_modification"]),
            "/run": ("execute", ["shell_execution"]),
            "/fix": ("debug", ["analysis"]),
            "/install": ("install", ["package_management"]),
            "/search": ("search", ["web_search"]),
            "/read": ("read", ["file_reading"]),
            "/settings": ("settings_mode", []),
            "/aislots": ("ai_slots_mode", []),
            "/ai": ("chat_mode", []),
        }
        if cmd in mapping:
            intent, tools = mapping[cmd]
            return ExecutionPlan(
                intent=intent,
                steps=[arg] if arg else [],
                tools=tools,
                risk_level=RiskLevel.MEDIUM if intent in ("execute","install") else RiskLevel.LOW,
                requires_confirmation=(intent in ("execute","install"))
            )
        return None
