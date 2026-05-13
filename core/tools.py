import re, subprocess, os, shutil
from pathlib import Path
from typing import List, Dict, Tuple

class ToolEngine:
    def __init__(self, workspace: Path, config: dict, logger=None):
        self.workspace = workspace
        self.config = config
        self.logger = logger

    def parse(self, text: str) -> Tuple[List[Dict], str, List[str]]:
        """Extract all tool calls (XML or ? syntax) and return (actions, clean_text, logs)."""
        tools = []
        logs = []

        # ===== XML‑style (LongCat / Claude‑tools format) =====
        # <tool_calls>...</tool_calls> wrapper
        wrapper_match = re.search(r'<tool_calls>(.*?)</tool_calls>', text, re.DOTALL)
        xml_block = wrapper_match.group(1) if wrapper_match else text

        # Individual <create path="...">content</create>
        for m in re.finditer(r'<create\s+path="(.*?)">(.*?)</create>', xml_block, re.DOTALL):
            tools.append({"type": "create", "path": m.group(1).strip(), "content": m.group(2).strip()})
        # <run command="..."/>
        for m in re.finditer(r'<run\s+command="(.*?)"\s*/>', xml_block):
            tools.append({"type": "run", "command": m.group(1).strip()})
        # <mkdir path="..."/>
        for m in re.finditer(r'<mkdir\s+path="(.*?)"\s*/>', xml_block):
            tools.append({"type": "mkdir", "path": m.group(1).strip()})
        # <delete path="..."/>
        for m in re.finditer(r'<delete\s+path="(.*?)"\s*/>', xml_block):
            tools.append({"type": "delete", "path": m.group(1).strip()})
        # <install package="..."/>
        for m in re.finditer(r'<install\s+package="(.*?)"\s*/>', xml_block):
            tools.append({"type": "install", "package": m.group(1).strip()})
        # <log message="..."/>
        for m in re.finditer(r'<log\s+message="(.*?)"\s*/>', xml_block):
            logs.append(m.group(1).strip())

        # LongCat alternative: <longcat_tool_call>create ... </longcat_tool_call>
        lc_match = re.search(r'<longcat_tool_call>create\s*<longcat_arg_key>path</longcat_arg_key>\s*<longcat_arg_value>(.*?)</longcat_arg_value>\s*<longcat_arg_key>content</longcat_arg_key>\s*<longcat_arg_value>(.*?)</longcat_arg_value>\s*</longcat_tool_call>', xml_block, re.DOTALL)
        if lc_match:
            tools.append({"type": "create", "path": lc_match.group(1).strip(), "content": lc_match.group(2).strip()})

        # ===== ? syntax (legacy) =====
        for m in re.finditer(r'\?run\((.+?)\)', text):
            tools.append({"type": "run", "command": m.group(1).strip()})
        for m in re.finditer(r'\?create\((.+?)\)\s*\nCONTENT:\s*\n(.*?)\nENDCONTENT', text, re.DOTALL):
            tools.append({"type": "create", "path": m.group(1).strip(), "content": m.group(2)})
        for m in re.finditer(r'\?mkdir\((.+?)\)', text):
            tools.append({"type": "mkdir", "path": m.group(1).strip()})
        for m in re.finditer(r'\?delete\((.+?)\)', text):
            tools.append({"type": "delete", "path": m.group(1).strip()})
        for m in re.finditer(r'\?install\((.+?)\)', text):
            tools.append({"type": "install", "package": m.group(1).strip()})
        for m in re.finditer(r'\?log\((.+?)\)', text):
            logs.append(m.group(1).strip())

        # Clean tool calls from visible text
        clean = re.sub(r'<tool_calls>.*?</tool_calls>', '', text, flags=re.DOTALL)
        clean = re.sub(r'<longcat_tool_call>.*?</longcat_tool_call>', '', clean, flags=re.DOTALL)
        clean = re.sub(r'<create\s+path=".*?">.*?</create>', '', clean, flags=re.DOTALL)
        clean = re.sub(r'<(?:run|mkdir|delete|install|log|edit)\s+.*?/>', '', clean)
        clean = re.sub(r'\?run\(.+?\)', '', clean)
        clean = re.sub(r'\?create\(.+?\)\s*\nCONTENT:\s*\n.*?\nENDCONTENT', '', clean, flags=re.DOTALL)
        clean = re.sub(r'\?(?:mkdir|delete|install|log)\(.+?\)', '', clean)
        clean = re.sub(r'\n{3,}', '\n\n', clean).strip()

        return tools, clean, logs

    def execute(self, tool: Dict) -> str:
        t = tool["type"]
        if t == "run":   return self._run(tool["command"])
        if t == "create": return self._create(tool["path"], tool.get("content",""))
        if t == "mkdir":  return self._mkdir(tool["path"])
        if t == "delete": return self._delete(tool["path"])
        if t == "install":return self._install(tool["package"])
        return ""

    def _run(self, cmd: str) -> str:
        for banned in self.config["execution"]["command_blacklist"]:
            if banned in cmd:
                return f"✗ Blocked: {banned}"
        try:
            proc = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=str(self.workspace), timeout=60)
            return f"✓ {proc.stdout.strip()}" if proc.returncode == 0 else f"✗ {proc.stderr.strip()}"
        except subprocess.TimeoutExpired:
            return "✗ Timeout"
        except Exception as e:
            return f"✗ {e}"

    def _create(self, path: str, content: str) -> str:
        target = (self.workspace / path).resolve()
        if not str(target).startswith(str(self.workspace)):
            target = self.workspace / Path(path).name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return f"✓ Created {path}"

    def _mkdir(self, path: str) -> str:
        (self.workspace / path).mkdir(parents=True, exist_ok=True)
        return f"✓ Created dir {path}"

    def _delete(self, path: str) -> str:
        target = (self.workspace / path).resolve()
        if not str(target).startswith(str(self.workspace)):
            return "✗ Outside workspace"
        if target.is_file(): target.unlink()
        elif target.is_dir(): shutil.rmtree(target)
        else: return "✗ Not found"
        return f"✓ Deleted {path}"

    def _install(self, pkg: str) -> str:
        return self._run(f"pkg install {pkg} -y 2>/dev/null || pip install {pkg} -q")
