# 🦞 OpenCore Agent

<div align="center">
  <img src="https://img.shields.io/badge/status-production%20grade-brightgreen" alt="Production Grade"/>
  <img src="https://img.shields.io/badge/python-3.11%2B-blue" alt="Python 3.11+"/>
  <img src="https://img.shields.io/badge/Termux-ready-orange" alt="Termux Ready"/>
  <img src="https://img.shields.io/badge/license-MIT-yellow" alt="License MIT"/>
  <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code style: black"/>
  <br/>
  <img src="https://img.shields.io/badge/free%20tier-OpenRouter-brightgreen" alt="Free Tier OpenRouter"/>
  <img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg" alt="PRs Welcome"/>
  <br/><br/>
  <i>⚡ An autonomous AI terminal shell — build, execute, and automate with natural language. ⚡</i>
</div>

---

## 🤔 Why I Built OpenCore

I wanted a **professional AI coding agent** that works entirely inside **Termux on Android** – no desktop, no browser, no paid subscriptions.  
Most coding assistants are locked behind cloud IDEs or expensive plans. OpenCore is different:

- 🆓 **Free by default** – uses free API tiers (OpenRouter, Gemini)
- 📱 **Mobile-first** – runs on your phone, inside Termux
- 🧠 **Autonomous** – not a chatbot; it thinks, plans, and executes
- 🛡️ **Sandboxed** – all file operations stay inside `workspace/`
- 🔌 **Multi‑provider** – switch between OpenRouter, Gemini, DeepSeek or your own endpoint

---

## ⚙️ Supported AI Models

| Provider   | Model                                | Cost   | Notes                          |
|------------|--------------------------------------|--------|---------------------------------|
| OpenRouter | `openai/gpt-oss-120b:free`           | FREE   | Default – auto‑routed free model|
| OpenRouter | `google/gemini-2.0-flash-001`        | FREE   | Reliable for small builds      |
| Gemini     | `gemini-2.0-flash`                   | FREE   | 1,500 requests/day             |
| DeepSeek   | `deepseek-chat`                      | $0.14/M| Very cheap, high quality       |
| Custom     | Any OpenAI‑compatible endpoint       | Varies | Bring your own key             |

You can switch models instantly from the `/aislots` menu or by editing `config/settings.json`.

---

## 🚀 Features

- **🧠 Autonomous AI Agent** – it uses `?run`, `?create`, `?mkdir` and other tools by itself
- **📁 Incremental project generation** – large projects are built file‑by‑file, no crashes
- **🛡️ Sandboxed workspace** – all file operations stay inside `workspace/`
- **🎯 Command system** – `/build`, `/read`, `/run`, `/help`
- **🔌 Multi‑provider support** – OpenRouter, Gemini, DeepSeek, or custom endpoints
- **📱 Termux‑optimised** – works perfectly on Android without rooting
- **🎨 Beautiful terminal UI** – Rich‑powered, orange accent theme, Claude Code style

---

## 📦 Installation (Termux)

```bash
# 1. Update packages & install dependencies
pkg update && pkg install python clang make git -y

# 2. Clone the repository
cd ~
git clone https://github.com/TermuxLover-dev/OpenCore-For-TERMUX-.git
cd OpenCore-For-TERMUX-

# 3. Install Python packages
pip install rich pyfiglet

# 4. Compile the C++ engine (optional, for speed)
cd engines/cpp_bridge && make && cd ../..

# 5. Launch the agent
python main.py
🔑 First‑Run Setup
When you start OpenCore for the first time, you'll be guided through a setup wizard:

Choose a provider → Recommended: 1 (OpenRouter – free)

Choose a model → Recommended: 1 (DeepSeek V3) or the default free model

Enter your API key → Get it from openrouter.ai/keys (free, no credit card)

Slot name → Press Enter to accept main

You can change these settings later with the /aislots command.

🖥️ Usage
Main Menu
text
1. AI Chat    → Talk or command the AI
2. Settings   → View your current configuration
3. AI Slots   → Manage API providers
4. Quit       → Exit
Press 1 to enter Chat Mode.

Chat Commands
Command	Description
/build <desc>	Create a full project from a prompt
/read <folder>	Read and summarise a project folder
/run <command>	Execute a shell command
/help	Show help
menu	Return to main menu
Natural Language Automation
The AI can handle requests in plain English.
Just type something like:

text
make a Flask todo app with SQLite, install Flask, and run it on port 5000
The AI will:

Create the files with ?create(...)

Install dependencies with ?install(flask)

Start the server with ?run(python app.py)

🛠️ AI Tool Syntax (for developers)
The AI uses these internal commands, but you don't need to type them.
They are shown in the chat output so you know what's happening:

Tool	What it does
?create(path)	Create a file with the given content
?mkdir(path)	Create a directory
?run(cmd)	Run a shell command
?install(pkg)	Install a package
?delete(path)	Delete a file or folder
?inspect(target)	Show workspace/system info
?log(message)	Log a message to the user
🧱 Architecture
text
[ User Input ] → [ Rich Terminal UI ] → [ Command Router ]
                                              ↓
                                       [ AI Manager ]
                                              ↓
                          [ Tool Engine (parse & execute) ]
                                              ↓
                    ┌──────────────┬───────────┬──────────┐
                    ↓              ↓           ↓
              [ File Ops ]   [ Shell ]   [ Package ]
core/ – agent logic, router, validator, tool engine, executor

ai/ – multi‑slot AI manager, providers (OpenRouter, Gemini, DeepSeek)

ui/ – Rich‑based terminal interface with theme

engines/ – C++ and Bash sidecars for performance

config/ – settings file (auto‑generated)

workspace/ – sandboxed directory for all generated files

🔒 Security
Workspace sandbox: all file paths are resolved relative to workspace/

Command blacklist: dangerous commands (rm -rf /, mkfs, dd, etc.) are blocked

No secrets in logs: API keys are never written to log files

.gitignore: config/settings.json is excluded from version control

📋 Requirements
Python 3.11+

pip packages: rich, pyfiglet

C++ compiler (optional): for the fast execution engine

API key from one of the supported providers (free tiers available)

🤝 Contributing
Pull requests are welcome!
OpenCore is designed to be extensible – you can add new providers, new tools, or UI improvements.
Fork the repo, make your changes, and submit a PR.

📄 License
MIT – feel free to use, modify, and distribute.

<div align="center"> <b>BUILD · EXECUTE · AUTOMATE</b><br/> Made with 🦞 for the Termux community </div> ```
