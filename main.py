#!/usr/bin/env python3
import asyncio, json, time, sys, os
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import box

sys.path.insert(0, str(Path(__file__).parent))
from config.settings import load_config, save_config
from core.agent import Agent
from ui.terminal import TerminalUI

def setup_wizard(config):
    console = Console(highlight=False, color_system="truecolor")

    if config.get("ai_slots") and config.get("active_slot"):
        slot_name = config["active_slot"]
        old = config["ai_slots"].get(slot_name, {})
        if old.get("api_key"):
            console.print(Panel(
                f"Existing slot: [bold #f97316]{slot_name}[/]\n"
                f"Provider: [bold]{old.get('provider','?')}[/]\n"
                f"Model: [bold]{old.get('model_name','?')}[/]",
                title="Saved Configuration", border_style="#f97316"
            ))
            keep = console.input("  Keep this config? [[bold #f97316]Y/n[/]]: ").strip().lower()
            if keep in ("", "y", "yes"):
                console.print("\n[bold green]Starting OpenCore…[/]\n")
                time.sleep(0.5)
                return

    console.clear()
    console.print()
    console.print(Text("OPENCORE AGENT", style="bold #f97316"), justify="center")
    console.print(Text("BUILD · EXECUTE · AUTOMATE", style="dim #f97316"), justify="center")
    console.print()

    console.print(Panel(
        "[bold #f97316]Select a Provider[/]\n\n"
        "[bold #f97316]1.[/] OpenRouter    [green](unlimited free tier, recommended)[/]\n"
        "[bold #f97316]2.[/] Google Gemini [red](~50 req/day, quota limited)[/]\n"
        "[bold #f97316]3.[/] DeepSeek      (free credits, cheap)\n"
        "[bold #f97316]4.[/] Custom        (OpenAI‑compatible endpoint)",
        border_style="#f97316", box=box.SQUARE
    ))

    choice = console.input("  Pick [bold #f97316][1–4][/]: ").strip()
    provider_map = {"1": "openrouter", "2": "gemini", "3": "deepseek", "4": "custom"}
    provider = provider_map.get(choice, "openrouter")

    base_url = ""
    model = ""
    api_key = ""

    if provider == "openrouter":
        base_url = "https://openrouter.ai/api/v1"
        console.print("\n[bold]Recommended free models:[/]")
        console.print("  [bold #f97316]1.[/] DeepSeek V3 [green](unlimited, smart)[/]")
        console.print("  [bold #f97316]2.[/] Google Gemini 2.0 Flash")
        console.print("  [bold #f97316]3.[/] Llama 4")
        console.print("  [bold #f97316]4.[/] Mistral 7B")
        console.print("  [bold #f97316]5.[/] Enter your own")
        mc = console.input("  Pick [bold #f97316][1–5][/]: ").strip()
        model_map = {
            "1": "deepseek/deepseek-chat:free",
            "2": "google/gemini-2.0-flash-001",
            "3": "meta-llama/llama-4:free",
            "4": "mistralai/mistral-7b-instruct:free",
        }
        model = model_map.get(mc)
        if not model:
            model = console.input("  Model name: ").strip()
    elif provider == "gemini":
        base_url = "https://generativelanguage.googleapis.com/v1beta"
        model = console.input("  Model [[bold]gemini-2.0-flash[/]]: ").strip() or "gemini-2.0-flash"
    elif provider == "deepseek":
        base_url = "https://api.deepseek.com/v1"
        model = console.input("  Model [[bold]deepseek-chat[/]]: ").strip() or "deepseek-chat"
    elif provider == "custom":
        base_url = console.input("  Base URL: ").strip()
        model = console.input("  Model name: ").strip()

    api_key = console.input("  API key: ").strip()

    slot_name = console.input("  Slot name [[bold]main[/]]: ").strip() or "main"

    config["ai_slots"][slot_name] = {
        "provider": provider,
        "api_key": api_key,
        "base_url": base_url,
        "model_name": model,
        "temperature": 0.3,
        "max_tokens": 4096,
        "tool_permissions_profile": "full",
        "enabled": True
    }
    config["active_slot"] = slot_name
    config["first_run_complete"] = True
    save_config(config)

    console.print(f"\n[bold green]✓[/] Using [bold]{provider}[/] – [bold]{model}[/]")
    if provider in ("gemini",):
        console.print("[yellow]⚠ Gemini has low daily quotas; avoid large builds.[/]")
    console.print("[dim]Starting OpenCore…[/]\n")
    time.sleep(1)

async def main():
    config = load_config()
    setup_wizard(config)
    agent = Agent(config)
    ui = TerminalUI(agent, config)
    try:
        await ui.run()
    except KeyboardInterrupt:
        print("\nShutting down OpenCore.")
    finally:
        agent.shutdown()
        print("Goodbye.")

if __name__ == "__main__":
    asyncio.run(main())
