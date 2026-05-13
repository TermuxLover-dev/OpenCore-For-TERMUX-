import asyncio, json, time, os
from pathlib import Path
from core.router import Router
from core.tools import ToolEngine
from core.validator import Validator
from ai.manager import AIManager

SYSTEM_PROMPT = """You are ClawCore – a fully autonomous AI execution agent operating inside a controlled terminal runtime.

You are NOT a chatbot. You are an agent that EXECUTES actions using system syntax.

TOOLS AVAILABLE:
?run(command) – Execute shell command
?create(path)
CONTENT:
file content here
ENDCONTENT – Create a file
?mkdir(path) – Create directory
?delete(path) – Delete file or directory
?install(package) – Install a package
?edit(path)
FIND:
old text
REPLACE:
new text
ENDEDIT – Edit a file
?append(path)
CONTENT:
text to append
ENDAPPEND – Append to file
?inspect(target) – Inspect workspace/system/logs
?log(message) – Report progress to user

RULES:
1. EXECUTE, don't explain what you could do.
2. Batch operations in ONE response.
3. Never ask unnecessary questions – infer and act.
4. Generate complete plans in one message.
5. Minimize conversational text – use ?log for progress.
6. Continue until task completion.
7. Assume Termux/Linux, Python/Bash available.
8. Workspace is sandboxed – all paths relative to workspace."""

HELP_TEXT = """OPENCORE COMMANDS:
  /build <prompt>   Full project generation
  /read <project>   Read project files
  /run <command>    Execute shell command
  /help             This help
  menu              Return to main menu
Just chat naturally – the AI will execute autonomously."""

class Agent:
    def __init__(self, config):
        self.config = config
        self.workspace = Path(config["workspace"]["root_directory"]).resolve()
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.router = Router(self)
        self.tools = ToolEngine(self.workspace, config, logger=self)
        self.ai_manager = AIManager(config)
        self.log_dir = Path(config["logging"]["log_directory"])
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def log(self, action, result):
        if self.config["logging"]["enable_logs"]:
            with open(self.log_dir / "execution.jsonl", "a") as f:
                json.dump({"action": action, "result": result, "timestamp": time.time()}, f)
                f.write("\n")

    def shutdown(self):
        pass

    async def handle_input(self, user_input: str) -> dict:
        inp = user_input.strip()
        if not inp:
            return {"mode": "idle"}
        if inp.lower() in ("/help", "help"):
            return {"mode": "reply", "content": HELP_TEXT}
        if inp.lower() in ("/quit", "/exit", "quit", "exit"):
            return {"mode": "quit"}
        if inp.lower() == "/aislots":
            return {"mode": "ai_slots_mode"}
        if inp.lower() == "/settings":
            return {"mode": "settings_mode"}

        plan = self.router.parse(inp)
        if plan and plan.intent == "build":
            return await self._pipeline_build(plan.steps[0] if plan.steps else inp)
        if plan and plan.intent == "execute":
            cmd = plan.steps[0] if plan.steps else ""
            if not cmd:
                return {"mode": "reply", "content": "Usage: /run <command>"}
            return await self._direct_run(cmd)
        if plan and plan.intent == "read":
            project = plan.steps[0] if plan.steps else ""
            if not project:
                return {"mode": "reply", "content": "Usage: /read <project>"}
            return await self._direct_read(project)

        # AUTONOMOUS MODE – send to AI with tool access
        slot = self.ai_manager.slot_manager.get_active()
        if not slot or not slot.api_key:
            return {"mode": "reply", "content": "No API key. Restart setup."}

        try:
            resp = await self.ai_manager.send_prompt(SYSTEM_PROMPT, inp)
        except Exception as e:
            return {"mode": "reply", "content": f"API error: {e}"}

        if isinstance(resp, dict) and resp.get("mode") == "text":
            ai_text = resp["content"]
        elif isinstance(resp, dict):
            ai_text = json.dumps(resp)
        else:
            ai_text = str(resp)

        # Parse tools, execute, build response
        actions, clean_text, logs = self.tools.parse(ai_text)
        outputs = []
        for log_msg in logs:
            outputs.append(f"[dim]● {log_msg}[/]")
        for action in actions:
            result = self.tools.execute(action)
            t = action.get("type", "?")
            outputs.append(f"[cyan]?{t}[/] {result}")
            self.log(action, result)

        final = clean_text if clean_text else ""
        if outputs:
            final += "\n\n" + "\n".join(outputs)

        return {"mode": "reply", "content": final}

    async def _direct_run(self, command: str) -> dict:
        result = self.tools._run(command)
        if result.startswith("✓"):
            return {"mode": "run_output", "output": result[2:]}
        return {"mode": "run_error", "error": result[2:]}

    async def _direct_read(self, project: str) -> dict:
        target = self.workspace / project
        if not target.exists():
            return {"mode": "reply", "content": f"Not found: {project}"}
        if target.is_dir():
            files = [str(f.relative_to(self.workspace)) for f in target.rglob("*") if f.is_file()]
            content = "\n".join(files) if files else "Empty."
        else:
            content = target.read_text(encoding="utf-8", errors="replace")
        resp = await self.ai_manager.send_prompt(SYSTEM_PROMPT,
            f"Project '{project}' contents:\n{content[:6000]}\n\nGive a brief summary.")
        text = resp.get("content", str(resp)) if isinstance(resp, dict) else str(resp)
        return {"mode": "read_response", "content": text}

    async def _pipeline_build(self, user_request: str) -> dict:
        try:
            resp = await self.ai_manager.send_prompt(SYSTEM_PROMPT,
                f"User wants to build: {user_request}\n"
                "Plan the project: first use ?mkdir for directories, then ?create for each file.\n"
                "Generate ALL files using ?create syntax in ONE response.")
            text = resp.get("content", str(resp)) if isinstance(resp, dict) else str(resp)
            actions, clean, logs = self.tools.parse(text)
            results = []
            for action in actions:
                if action.get("type") == "create":
                    path = action["path"]
                    content = action.get("content", "")
                    self.tools._create(path, content)
                    results.append({"file": path, "status": "done", "path": str(self.workspace/path)})
                elif action.get("type") == "mkdir":
                    self.tools._mkdir(action["path"])
            if actions:
                return {"mode": "build_done", "project": user_request[:30], "files": results}
            return {"mode": "build_error", "error": "No files were generated. Try a more specific prompt."}
        except Exception as e:
            return {"mode": "build_error", "error": str(e)}
