import type { Client } from "discord.js";
import { logger } from "../../utils/logger.ts";

export default function log(client: Client<true>) {
    logger(`Successfully logged in`, "debug", client.user.tag);
}
