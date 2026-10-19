type LogLevel = "info" | "warn" | "error";
type LogMetadata = Record<string, unknown>;

function writeLog(level: LogLevel, message: string, metadata?: LogMetadata) {
  const entry = {
    timestamp: new Date().toISOString(),
    level,
    message,
    ...(metadata ? { metadata } : {}),
  };

  const serialized = JSON.stringify(entry);

  if (level === "error") {
    console.error(serialized);
    return;
  }

  if (level === "warn") {
    console.warn(serialized);
    return;
  }

  console.info(serialized);
}

export const logger = {
  info(message: string, metadata?: LogMetadata) {
    writeLog("info", message, metadata);
  },
  warn(message: string, metadata?: LogMetadata) {
    writeLog("warn", message, metadata);
  },
  error(message: string, metadata?: LogMetadata) {
    writeLog("error", message, metadata);
  },
};
