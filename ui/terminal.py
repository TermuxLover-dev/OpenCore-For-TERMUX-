import asyncio, json
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.status import Status
from rich.text import Text
from rich import box
from ui.theme import openclaw_theme

class TerminalUI:
    def __init__(self, agent, config):
        self.agent = agent
        self.config = config
        self.console = Console(theme=openclaw_theme, highlight=False, color_system="truecolor")
        self.running = True
        self.mode = "menu"

    def _header(self):
        return "[bold #f97316]OPENCORE AGENT[/] · " + self._status_text()

    def _status_text(self):
        slot = self.agent.ai_manager.slot_manager.get_active()
        model = slot.model_name if slot else "—"
        safe = self.config["system"]["safety_mode"]
        return f"Model: {model} · Safe: {safe}"

    def _show_menu(self):
        self.console.clear()
        self.console.print()
        self.console.print(Text("OPENCORE", style="bold #f97316"), justify="center")
        self.console.print(Text("BUILD · EXECUTE · AUTOMATE", style="dim #f97316"), justify="center")
        self.console.print()
        self.console.print(self._header(), justify="center")
        self.console.print()
        self.console.print(
            Panel(
                "[bold #f97316]1.[/] AI Chat\n"
                "[bold #f97316]2.[/] Settings\n"
                "[bold #f97316]3.[/] AI Slots\n"
                "[bold #f97316]4.[/] Quit\n\n"
                "[dim]Type a number[/dim]",
                border_style="#f97316", box=box.SQUARE, padding=(1, 2)
            )
        )

    def _show_settings(self):
        self.console.clear()
        text = json.dumps(self.config, indent=2)
        self.console.print(Panel(text[:3000], title="Settings", border_style="#f97316"))
        self.console.print("[dim]Type [bold]menu[/] to return[/]")

    def _show_slots(self):
        self.console.clear()
        lines = []
        for name, slot in self.agent.ai_manager.slot_manager.slots.items():
            marker = "[bold #f97316]★[/]" if name == self.config["active_slot"] else " "
            status = "[green]ON[/]" if slot.enabled else "[red]OFF[/]"
            lines.append(f"  {marker} [bold]{name}[/] | {slot.provider} | {slot.model_name} | {status}")
        self.console.print(Panel("\n".join(lines), title="AI Slots", border_style="#f97316"))
        self.console.print("[dim]Type [bold]menu[/] to return[/]")

    async def run(self):
        self.console.clear()
        self._show_menu()

        while self.running:
            prompt = "> "
            try:
                inp = await asyncio.to_thread(input, prompt)
            except (EOFError, KeyboardInterrupt):
                self.running = False
                break
            inp = inp.strip()
            if not inp:
                continue

            if inp.lower() in ("q", "quit", "exit", "/quit", "/exit"):
                self.running = False
                break
            if inp.lower() in ("menu", "/menu", "m"):
                self.mode = "menu"
                self.console.clear()
                self._show_menu()
                continue
            if inp.lower() in ("help", "/help", "?"):
                self.console.clear()
                self._show_menu()
                continue

            if self.mode == "menu":
                if inp == "1":
                    self.mode = "chat"
                    self.console.clear()
                    self.console.print(self._header())
                    self.console.print("[#f97316]Chat mode active.[/] Type [bold]menu[/] to return.")
                    self.console.print("[dim]Commands: /build /read /run /help[/]\n")
                    continue
                elif inp == "2":
                    self._show_settings()
                    continue
                elif inp == "3":
                    self._show_slots()
                    continue
                elif inp == "4":
                    self.running = False
                    break
                else:
                    self.console.print("[dim]Type 1-4[/]")
                    continue

            if self.mode == "chat":
                # First show "Reasoning..." then "Thinking..." then final response
                with Status("[bold #f97316]Reasoning...[/]", console=self.console, spinner="dots"):
                    resp = await self.agent.handle_input(inp)
                self._render_response(resp)
                self.console.print()

    def _render_response(self, r):
        mode = r.get("mode", "")
        if mode == "idle":
            return

        if mode == "build_done":
            proj = r.get("project", "?")
            files = r.get("files", [])
            self.console.print(f"\n[green]✓[/] Project [bold]{proj}[/] built with {len(files)} files")
            for f in files:
                if f["status"] == "done":
                    self.console.print(f"  [green]●[/] [dim]{f['path']}[/]")
                else:
                    self.console.print(f"  [red]✗[/] {f['file']} — {f.get('error','?')}")
            self.console.print(f"[dim]Workspace: {self.agent.workspace.resolve()}[/]")

        elif mode == "build_error":
            self.console.print(f"\n[red]✗ Build failed:[/] {r['error']}")

        elif mode == "execution":
            for e in r.get("timeline", []):
                path = e.get("result", {}).get("path", e["action"].get("_resolved_path", "?"))
                self.console.print(f"  [green]●[/] Created [dim]{path}[/]")

        elif mode == "run_output":
            self.console.print(f"\n[bold cyan]System:[/] {r['output']}")

        elif mode == "run_error":
            self.console.print(f"\n[red]Execution error:[/] {r['error']}")

        elif mode == "read_response":
            self.console.print(f"\n[bold #f97316]Read Report:[/]\n{r['content']}")

        elif mode == "settings_mode":
            self._show_settings()

        elif mode == "ai_slots_mode":
            self._show_slots()

        elif mode == "reply":
            content = str(r.get("content", ""))
            self.console.print()
            try:
                self.console.print(Panel(Markdown(content), title="[bold #f97316]AI[/]", border_style="#f97316", box=box.SQUARE))
            except Exception:
                self.console.print(content[:1500])

        else:
            self.console.print(str(r)[:500])
