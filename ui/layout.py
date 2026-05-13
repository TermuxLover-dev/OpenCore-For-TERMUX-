from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

def make_header(agent):
    slot = agent.ai_manager.slot_manager.get_active()
    slot_name = agent.config.get("active_slot", "---")
    model = slot.model_name if slot else "none"
    ws = str(agent.workspace)
    safety = agent.config["system"]["safety_mode"]
    header = Table.grid(padding=(0,2))
    header.add_column(justify="left")
    header.add_column(justify="center")
    header.add_column(justify="right")
    header.add_row(
        Text("OPENCLAW AGENT", style="header"),
        Text(f"slot: {slot_name} ({model})", style="header.text"),
        Text(f"ws: {ws}  SAFE: {safety}", style="header.text")
    )
    return Panel(header, style="panel.border")

def make_chat_layout():
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="main"),
        Layout(name="input", size=3)
    )
    layout["main"].split_row(
        Layout(name="conversation", ratio=3),
        Layout(name="timeline", ratio=2)
    )
    return layout

def make_settings_layout():
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="body")
    )
    layout["body"].split_row(
        Layout(name="categories", ratio=1),
        Layout(name="details", ratio=3)
    )
    return layout

def make_aislots_layout():
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="body")
    )
    layout["body"].split_row(
        Layout(name="slots_list", ratio=1),
        Layout(name="slot_detail", ratio=3)
    )
    return layout
