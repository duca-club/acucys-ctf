import { EmbedBuilder, SlashCommandBuilder } from "discord.js";
import type { CommandOptions, SlashCommandProps } from "commandkit";
import { logger } from "../../utils/logger.ts";
import { getChallenges } from "../../utils/ctfd.ts";
import fuzzysort from "fuzzysort";

let categoriesCache: string[] | null = null;

async function loadCategories(): Promise<string[]> {
    if (categoriesCache) return categoriesCache;
    const all = await getChallenges();
    categoriesCache = Array.from(new Set(all.map((c) => c.category))).sort();
    // cache timeout 30s
    setTimeout(() => (categoriesCache = null), 30 * 1000);
    return categoriesCache;
}

export const data = new SlashCommandBuilder()
    .setName("challenges")
    .setDescription("Browse challenges")
    .addStringOption((opt) =>
        opt.setName("category").setDescription("Challenge category to filter").setRequired(true).setAutocomplete(true),
    );

export async function run({ interaction }: SlashCommandProps) {
    await interaction.deferReply();
    const raw = interaction.options.getString("category", true);
    const key = raw.toLowerCase();

    try {
        const all = await getChallenges();
        const filtered = all.filter((c) => c.category.toLowerCase() === key);

        if (filtered.length === 0) {
            return interaction.editReply(`No challenges found in **${raw}**.`);
        }

        const embed = new EmbedBuilder()
            .setTitle(`<:container:1365101550707540038> ${raw} Challenges`)
            .setDescription(`All currently available ${raw} challenges:`)
            .setColor(0x0fa626);

        for (const c of filtered) {
            embed.addFields({
                name: c.name,
                value: `<:score:1365101561528713376> ${c.value} points <:check:1365101535461117982> ${c.solves} solves`,
                inline: true,
            });
        }

        await interaction.editReply({ embeds: [embed] });
        logger(`Successfully ran /challenges category ${raw}`, "success", interaction.user.username);
    } catch (error) {
        await interaction.editReply("Something went wrong. Please try again later.");
        logger(String(error), "error", interaction.user.username);
    }
}

export async function autocomplete({ interaction }: CommandOptions["autocomplete"]) {
    const input = interaction.options.getFocused().toString();
    const cats = await loadCategories();

    const results = fuzzysort.go(input, cats, { limit: 25, threshold: -10000 });
    const choices = results.length
        ? results.map((r) => ({ name: r.target, value: r.target }))
        : cats
              .filter((c) => c.toLowerCase().startsWith(input.toLowerCase()))
              .slice(0, 25)
              .map((c) => ({ name: c, value: c }));

    await interaction.respond(choices);
}
