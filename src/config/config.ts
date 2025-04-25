import "dotenv/config";

function getEnvVar(name: string): string {
    const value = process.env[name];
    if (!value) {
        throw new Error(`Missing required environment variable: ${name}`);
    }
    return value;
}

interface Config {
    DISCORD_TOKEN: string;
    CTFD_URL: string;
    CTFD_API_TOKEN: string;
    GUILD_ID: string;
    DEV_ROLE_ID: string;
}

const config: Config = {
    DISCORD_TOKEN: getEnvVar("DISCORD_TOKEN"),
    CTFD_URL: getEnvVar("CTFD_URL"),
    CTFD_API_TOKEN: getEnvVar("CTFD_API_TOKEN"),
    GUILD_ID: getEnvVar("GUILD_ID"),
    DEV_ROLE_ID: getEnvVar("DEV_ROLE_ID"),
};

export default config;
