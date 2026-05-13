import asyncio, json, time, shlex, os
from pathlib import Path
from typing import Dict, List

class Executor:
    def __init__(self, config, logger=None):
        self.config = config
        self.workspace = Path(config["workspace"]["root_directory"]).resolve()
        self.logger = logger

    async def dispatch_actions(self, actions: List[Dict]) -> List[Dict]:
        timeline = []
        for action in actions:
            result = await self._execute_file_action(action)
            timeline.append({"action": action, "result": result})
            if self.logger:
                self.logger.log(action, result)
        return timeline

    async def write_file(self, path: str, content: str) -> Dict:
        """Write a single file to disk, creating directories."""
        target = Path(path).resolve()
        # Safety: ensure inside workspace
        if not str(target).startswith(str(self.workspace)):
            target = self.workspace / target.name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return {"status": "created", "path": str(target)}

    async def _execute_file_action(self, action: Dict) -> Dict:
        a_type = action.get("type", "create_file")
        path = action.get("_resolved_path", action.get("path", "untitled.txt"))
        content = action.get("content", "")
        if a_type in ("create_file", "modify_file"):
            # Use the same safe writer
            target = Path(path).resolve()
            if not str(target).startswith(str(self.workspace)):
                target = self.workspace / target.name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
            return {"status": "created", "path": str(target)}
        elif a_type == "delete_file":
            Path(path).unlink(missing_ok=True)
            return {"status": "deleted", "path": str(path)}
        elif a_type == "read_file":
            if Path(path).exists():
                return {"content": Path(path).read_text(encoding="utf-8")}
            return {"error": "File not found"}
        return {"status": "ok"}
