<div>
  <h1>CTFd Discord Bot</h1>
  <p>
    A Discord bot designed to seamlessly integrate with
    <a href="https://ctfd.io/">CTFd</a> to let users browse challenges,
    track progress on leaderboards, and more — all from within Discord.
  </p>
</div>

## 📂 Project Structure

```
ctfd-discord-bot/
├── emojis/               # Discord application emojis
│
├── src/
│   └── ctfd_discord_bot/ # Project source root
│       ├── cogs/         # Discord slash commands
│       ├── utils/        # Utility/helper functions
│       ├── __init__.py   # Main bot code
│       └── __main__.py   # Bot entrypoint
│
├── .env                  # Environment variables
├── .env.exampple         # Example environment variables
├── .gitattributes        # Git config
├── .gitignore            # Git ignore
├── CONTRIBUTING.md       # Contributing guide
├── poetry.lock           # Dependency lockfile
├── pyproject.toml        # Project metadata & dependencies
└── README.md
```

## 🚀 Getting Started

### Prerequisites

- [Poetry 1.8.0 or higher](https://python-poetry.org/docs/#installation).
- Python 3.12 or higher.
- A running CTFd instance ([CTFd setup](https://docs.ctfd.io/docs/deployment/installation)). [^1].

> [!IMPORTANT]
> This bot handles registration itself, you will need to disable the CTFd registration page in the admin panel.
>
> You will also need to create a public uneditable field in CTFd to store the Discord User IDs.

[^1]: Or use the [demo instance](https://demo.ctfd.io).

### 1. Clone Repository

```bash
git clone https://github.com/duca-club/ctfd-discord-bot.git
cd ctfd-discord-bot
```

### 2. Install Dependencies

```bash
# Change `3.14` if you wish to use a different Python version
poetry env use 3.14
poetry install
```

### 3. Configure Environment

> [!IMPORTANT]
>
> This bot supports sending heartbeats to an Uptime Kuma monitor. Please make sure that the API path for your Uptime Kuma instance `/api/push/*` is publicly reachable.
> Note: only enabled if the bot is running in production mode and push url is set.

Create a `.env` file using the provided `.env.example` template:

```bash
cp .env.example .env
```

Fill in required values:

- `BOT_MODE=dev` *(or prod)*
- `BOT_TOKEN=<your Discord bot token>`
- `EVENT_NAME=<your event name>`
- `DISCORD_ID_FIELD=<the CTFd field ID for the discord user ID>`
- `CTFD_ACCESS_TOKEN=<your CTFd admin token>`
- `CTFD_INSTANCE_URL=<your CTFd instance base url>`
- `FEEDBACK_URL=<the url for the feedback form>`
- `WEBHOOK_URL=<the url for the discord webhook>`
- `WEBHOOK_FREQUENCY=<the frequency to check for new solves>`
- `API_TIMEOUT=<the timeout on any API requests>`
- `CACHE_TIMEOUT=<the timeout to cache any data>`
- `REGISTER_TIMEOUT=<the timeout for someone to respond during registration>`
- `PUSH_URL=<your Uptime Kuma monitor push url>`

### 4. Run Bot

```bash
poetry run ctfd-discord-bot
```

This starts the discord bot in development mode.

## 🤝 Contributing

Please refer to the [contributing guide](CONTRIBUTING.md) for more details.
