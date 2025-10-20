import { EmbedBuilder, MessageFlags } from "discord.js";
import type { CommandData, SlashCommandProps } from "commandkit";
import { logger } from "../../utils/logger.ts";

export const data: CommandData = {
    name: "ping",
    description: "returns latency stats for bot response time",
};

export async function run({ interaction, client }: SlashCommandProps): Promise<void> {
    try {
        await interaction.deferReply({ flags: MessageFlags.Ephemeral });

        const reply = await interaction.fetchReply();

        // Calculate roundtrip latency based on the difference between when the reply is created and when the interaction was received
        const ping = reply.createdTimestamp - interaction.createdTimestamp;

        const pong = new EmbedBuilder()
            .setTitle("<:wifi:1365101662028435466> Pong!")
            .addFields(
                { name: "Roundtrip Latency", value: `\`${ping}ms\``, inline: true },
                { name: "Websocket Heartbeat", value: `\`${client.ws.ping}ms\``, inline: true },
            )
            .setColor(0x00aeef);

        await interaction.editReply({ embeds: [pong] });
        logger("Successfully ran /ping command", "success", interaction.user.username);
    } catch (error) {
        await interaction.editReply("`[ERROR] exit code 1: command failed`");
        logger(String(error), "error", interaction.user.username);
    }
}
