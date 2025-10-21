<div>
  <img width="200" align="left" src="ACUCyS_CTF_Logo.png" alt="ACUCyS Logo">
  <h1>ACUCyS CTF</h1>
  <p>
    A Discord bot designed for the ACUCyS CTF event, seamlessly integrating with
    <a href="https://ctfd.io/">CTFd</a> to let users browse challenges, track progress on
    leaderboards, and more — all from within Discord.
  </p>
</div>

## 📂 Project Structure

```
acucys-ctf/
├── emojis/             # Discord application emojis
│
├── src/
│   └── acusys_ctf/     # Project source root
│       ├── cogs/       # Discord slash commands
│       ├── utils/      # Utility/helper functions
│       ├── __init__.py # Main bot code
│       └── __main__.py # Bot entrypoint
│
├── .env                # Environment variables
├── .env.exampple       # Example environment variables
├── .gitattributes      # Git config
├── .gitignore          # Git ignore
├── CONTRIBUTING.md     # Contributing guide
├── poetry.lock         # Dependency lockfile
├── pyproject.toml      # Project metadata & dependencies
├── README.md
```

## 🚀 Getting Started

### Prerequisites

- [Poetry 1.8.0 or higher](https://python-poetry.org/docs/#installation).
- Python 3.12 or higher.
- A running CTFd instance ([CTFd setup](https://docs.ctfd.io/docs/deployment/installation)). [^1].

[^1]: Or use the [demo instance](https://demo.ctfd.io).

### 1. Clone Repository

```bash
git clone https://github.com/duca-club/acucys-ctf.git
cd acucys-ctf
```

### 2. Install Dependencies

```bash
# Change `3.14` if you wish to use a different Python version
poetry env use 3.14
poetry install
```

### 3. Configure Environment

Create a `.env` file using the provided `.env.example` template:

```bash
cp .env.example .env
```

Fill in required values:

- `BOT_MODE=dev`
- `BOT_TOKEN=<your discord bot token>`
- `CTFD_ACCESS_TOKEN=<your CTFd admin token>`
- `CTFD_INSTANCE_URL=<your ctfd instance base url>`

### 4. Run Bot

```bash
poetry run acucys-ctf
```

This starts the discord bot in development mode.

## 🤝 Contributing

Please refer to the [contributing guide](CONTRIBUTING.md) for more details.