<div>
  <img width="200" align="left" src="ACUCyS_CTF_Logo.png" alt="ACUCyS Logo">
  <h1>ACUCyS CTF</h1>
  <p>
    A Discord bot designed for the ACUCyS CTF event, seamlessly integrating with
    <a href="https://ctfd.io/">CTFd</a> to let users browse challenges, track progress on
    leaderboards, and more — all from within Discord.
  </p>
</div>

![NodeJS](https://img.shields.io/badge/NodeJS-v22%2B-%235FA04E?style=for-the-badge&logo=nodedotjs&logoColor=white&logoSize=auto)
![Prettier](https://img.shields.io/badge/Prettier-%23F7B93E?style=for-the-badge&logo=prettier&logoColor=black&logoSize=auto)

## 📂 Project Structure

```
acucys-ctf/
├── .husky/         # Git pre-commit hooks
│
├── emojis/         # Discord application emojis
│
├── src/
│   ├── commands/   # Discord slash commands
│   ├── events/     # Discord event handlers
│   ├── utils/      # Utility/helper functions
│   └── index.ts
│
├── .env            # Environment variables
├── .env.exampple   # Example environment variables
├── .gitattributes  # Git config
├── .gitignore      # Git ignore
├── .prettierrc     # Prettier config
├── CONTRIBUTING.md
├── package-lock.json
├── package.json    # Project metadata & dependencies
├── README.md
└── tsconfig.json   # TypeScript configuration
```

## 🚀 Getting Started

### Prerequisites

- Node.js v22 or higher
- A running CTFd instance ([CTFd setup](https://docs.ctfd.io/docs/deployment/installation))

### 1. Clone Repository

```bash
git clone https://github.com/duca-club/acucys-ctf.git
cd acucys-ctf
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Configure Environment

Create a `.env` file using the provided `.env.example` template:

```bash
cp .env.example .env
```

Fill in required values:

- `DISCORD_TOKEN=<your discord bot token>`
- `CTFD_URL=<your ctfd instance base url>`
- `CTFD_API_TOKEN=<your CTFd admin token>`
- `GUILD_ID=<discord server ID for dev commands>`
- `DEV_ROLE_ID=<discord role ID for dev commands>`

### 4. Run Bot

```bash
npm run dev
```

This starts the discord bot in development mode.

## 🤝 Contributing

Please refer to the [contributing guide](CONTRIBUTING.md) for more details.

_</> with <3 by dec1bel_
