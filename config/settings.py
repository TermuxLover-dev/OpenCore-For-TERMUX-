import json
import os
from pathlib import Path
from typing import Dict, Any

BASE_DIR = Path(__file__).parent.parent
CONFIG_PATH = BASE_DIR / "config" / "settings.json"

DEFAULT_CONFIG = {
    "first_run_complete": False,
    "system": {
        "system_prompt": "You are an autonomous AI agent. Output ONLY valid JSON action plans.",
        "global_temperature": 0.2,
        "max_tokens": 4096,
        "response_style": "balanced",
        "safety_mode": "strict"
    },
    "workspace": {
        "root_directory": str(BASE_DIR / "workspace"),
        "allowed_paths": [str(BASE_DIR / "workspace")],
        "file_write_policy": "sandbox_only"
    },
    "execution": {
        "allow_shell_execution": True,
        "allow_cpp_execution": True,
        "command_whitelist": ["mkdir", "touch", "cat", "echo", "ls"],
        "command_blacklist": ["rm -rf", "mkfs", "dd", "shutdown", "reboot"]
    },
    "logging": {
        "enable_logs": True,
        "log_level": "INFO",
        "log_directory": str(BASE_DIR / "logs")
    },
    "memory": {
        "enable_session_memory": False,
        "memory_type": "json"
    },
    "ai_slots": {
        "ai1": {
            "provider": "openai",
            "api_key": "",
            "base_url": "https://api.openai.com/v1",
            "model_name": "gpt-4o",
            "temperature": 0.2,
            "max_tokens": 4096,
            "tool_permissions_profile": "full",
            "enabled": True
        },
        "ai2": {
            "provider": "gemini",
            "api_key": "",
            "base_url": "https://generativelanguage.googleapis.com/v1beta",
            "model_name": "gemini-2.0-flash",
            "temperature": 0.2,
            "max_tokens": 4096,
            "tool_permissions_profile": "full",
            "enabled": False
        },
        "ai3": {
            "provider": "groq",
            "api_key": "",
            "base_url": "https://api.groq.com/openai/v1",
            "model_name": "llama-3.3-70b-versatile",
            "temperature": 0.2,
            "max_tokens": 4096,
            "tool_permissions_profile": "full",
            "enabled": False
        },
        "ai4": {
            "provider": "custom",
            "api_key": "",
            "base_url": "http://localhost:11434/v1",
            "model_name": "llama3.2",
            "temperature": 0.2,
            "max_tokens": 4096,
            "tool_permissions_profile": "full",
            "enabled": False
        }
    },
    "active_slot": "ai1"
}

def load_config() -> Dict[str, Any]:
    if not CONFIG_PATH.exists():
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_PATH, "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)
        return DEFAULT_CONFIG.copy()
    with open(CONFIG_PATH) as f:
        return json.load(f)

def save_config(config: Dict[str, Any]):
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)
