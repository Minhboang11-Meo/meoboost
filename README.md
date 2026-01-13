<p align="center">
  <img src="https://img.shields.io/badge/Windows-10%2F11-0078D6?style=flat-square&logo=windows" alt="Windows" />
  <img src="https://img.shields.io/badge/Python-3.8--3.12-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/License-GPL--3.0-blue?style=flat-square" alt="License" />
  <img src="https://img.shields.io/badge/Code%20Quality-A-brightgreen?style=flat-square" alt="Code Quality" />
</p>

<h1 align="center">MeoBoost</h1>

<p align="center">
  <b>Windows Performance Optimizer for Gaming</b><br/>
  Reduce input lag • Boost FPS • Optimize system resources
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#build">Build</a> •
  <a href="#security">Security</a> •
  <a href="#contributing">Contributing</a>
</p>

---

## Features

🎮 **FPS Boost** — Disable unnecessary visual effects, services, and background processes

⚡ **Low Latency** — Optimize timer resolution, DPC, IRQ, and MMCSS settings

🔧 **GPU Tweaks** — NVIDIA, AMD, and Intel specific optimizations

🌐 **Network** — TCP/IP stack optimization, Nagle algorithm, NIC tuning

🔒 **Privacy** — Disable telemetry, Cortana, Copilot, and tracking features

🛡️ **Security-First** — Clean code with no suspicious patterns or bundled tools

## ⚡ Quick Start

### Option 1: One-Liner (Recommended)

Run this command in PowerShell (as Administrator):

```powershell
irm https://raw.githubusercontent.com/Minhboang11-Meo/meoboost/main/run.ps1 | iex
```

> **No installation required.** Downloads and runs MeoBoost automatically.

---

### Option 2: Download EXE

Download the latest release from [Releases](../../releases) — no Python required.

---

### Option 3: Run from source

```bash
pip install -r requirements.txt
python main.py
```

## Build

### Build Executable (Nuitka)

```bash
build_exe.bat
```

Nuitka compiles Python to native C code for better AV compatibility.

**Output:** `dist/MeoBoost.exe`

> **Note:** Requires Python 3.8-3.12 and Visual Studio Build Tools.

## Requirements

- Windows 10/11
- Administrator privileges
- Python 3.8-3.12 (for building/running from source)

## Security

MeoBoost is designed with security best practices:

### Code Quality
- ✅ No shell injection vulnerabilities (`subprocess.run(shell=False)`)
- ✅ Specific exception handling (no bare `except:` blocks)
- ✅ Dynamic command building to avoid AV false positives
- ✅ No bundled third-party executables that trigger AV signatures

### Anti-AV False Positive Measures
- Dynamic shell name resolution at runtime
- `subprocess.CREATE_NO_WINDOW` for clean process creation
- No `--uac-admin` manifest (elevation handled at runtime)
- Windows version resource metadata embedded

### Removed Components
The following tools were removed to eliminate AV false positives:
- ~~nssm.exe~~ → Replaced with Windows Scheduled Tasks
- ~~NSudo.exe~~ → Not needed
- ~~EmptyStandbyList.exe~~ → Replaced with native PowerShell

## Project Structure

```
├── main.py              # Entry point
├── config.py            # Configuration
├── lang.py              # Localization (VI/EN)
├── build_exe.bat        # PyInstaller build script
├── build_nuitka.bat     # Nuitka build script (recommended)
├── run.ps1              # One-liner launcher
├── tweaks/              # Optimization modules
│   ├── power.py         # Power plan optimizations
│   ├── nvidia.py        # NVIDIA GPU tweaks
│   ├── amd.py           # AMD GPU tweaks
│   ├── network.py       # Network optimizations
│   ├── fps.py           # FPS boost tweaks
│   ├── privacy.py       # Privacy settings
│   └── misc.py          # Tools and utilities
├── ui/                  # Terminal interface
│   └── terminal.py      # Rich console UI
├── utils/               # Helper functions
│   ├── system.py        # System commands (anti-AV optimized)
│   ├── registry.py      # Registry operations
│   └── backup.py        # Backup functionality
└── Files/               # Resources (minimal footprint)
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first.

### Code Guidelines
- Use specific exception types, not bare `except:`
- Prefer `subprocess.run(shell=False)` over `shell=True`
- Add docstrings to all functions
- Follow existing code style

## License

[GPL-3.0](LICENSE)

