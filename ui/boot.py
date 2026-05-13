import asyncio
from rich.live import Live
from rich.panel import Panel
from rich.text import Text
from rich.console import Console

BOOT_STEPS = [
    "Initializing OpenClaw Kernel",
    "Loading AI Router",
    "Mounting Workspace",
    "Verifying Execution Sandbox",
    "Starting UI Shell"
]

async def show_boot_sequence():
    console = Console()
    with Live(console=console, refresh_per_second=4) as live:
        panel = Panel("", title="OPENCLAW AGENT", border_style="#f97316")
        lines = []
        for i, step in enumerate(BOOT_STEPS):
            lines.append(Text(f"[bold #f97316]>[/] {step} ...", style="dim"))
            panel.renderable = Text("\n".join(line.plain for line in lines))
            live.update(panel)
            await asyncio.sleep(0.6)
            lines[-1] = Text(f"[bold green]✓[/] {step} [green]OK[/green]", style="bright")
            live.update(panel)
            await asyncio.sleep(0.2)
        await asyncio.sleep(1.5)
