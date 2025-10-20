import colors from "colors";
import moment from "moment";

/**
 * The allowed log types
 */
export type LogType = "info" | "warn" | "error" | "debug" | "success";

// A configuration map for log levels with labels and corresponding color functions
const logFormats: Record<LogType, { label: string; color: (text: string) => string }> = {
    info: { label: "INFO", color: colors.cyan },
    warn: { label: "WARN", color: colors.yellow },
    error: { label: "ERROR", color: colors.red },
    debug: { label: "DEBUG", color: colors.blue },
    success: { label: "SUCCESS", color: colors.green },
};

/**
 * Logs a message with a consistent, structured format
 * @param content - The message to log
 * @param type - The type of log message. Defaults to 'debug'
 * @param discordUser - (Optional) The Discord user (for example, "User#1234") who initiated the action
 */
export const logger = (content: string, type: LogType = "debug", discordUser?: string): void => {
    // Use moment to format the current timestamp
    const timestamp = moment().format("HH:mm:ss DD-MM-YYYY");

    // Retrieve the label and color function based on log type
    const { label, color } = logFormats[type];

    // If a Discord user is provided, prepend it to the log message
    const user = discordUser ? ` [${discordUser}]` : "";

    // Build the final log message using a consistent pipe-separated format
    const logMessage = `[${timestamp}] [${label}]${user} ${content}`;

    console.log(color(logMessage));
};

// /**
//  * Logs a message with a timestamp.
//  * @param content - The message to log.
//  * @param type - The type of log message. Defaults to 'debug'.
//  */
// export const logger = (content: string, type: LogType = "debug", discordUser?: string): void => {
//     const timestamp: string = `[${moment().format("YYYY-MM-DD HH:mm:ss")}]:`;
//     const userString = discordUser ? ` (User: ${discordUser})` : '';
//     switch (type) {
//         case "info":
//             console.log(`ℹ️ ${timestamp} ${content}${userString}`);
//             break;
//         case "warn":
//             console.log(`⚠️ ${colors.yellow(timestamp)} ${colors.yellow(content)}${userString}`);
//             break;
//         case "error":
//             console.log(`❌ ${colors.red(timestamp)} ${colors.red(content)}${userString}`);
//             break;
//         case "debug":
//             console.log(`${colors.blue(timestamp)} ${colors.blue(content)}${userString}`);
//             break;
//         case "success":
//             console.log(`✅ ${colors.green(timestamp)} ${colors.green(content)}${userString}`);
//             break;
//         default:
//             // This default should never be reached due to the type constraint, but it is here for extra safety.
//             throw new TypeError("Logger type must be one of: info, warn, error, debug, success.");
//     }
// };
