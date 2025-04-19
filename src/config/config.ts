import { readFileSync } from "fs";
import { load } from "js-yaml";
import { z } from "zod";

// Enhanced configuration schema with more validation rules
const ConfigSchema = z
  .object({
    environment: z.enum(["development", "staging", "production"]),
    api: z.object({
      baseUrl: z.string().url(),
      timeout: z.number().positive(),
      retries: z.number().min(0).max(5),
      rateLimit: z.object({
        requests: z.number().positive(),
        period: z.number().positive(),
      }),
      auth: z.object({
        type: z.enum(["none", "basic", "jwt", "oauth"]),
        credentials: z.record(z.string()).optional(),
      }),
    }),
    database: z.object({
      url: z.string().url(),
      poolSize: z.number().positive(),
      retry: z.object({
        attempts: z.number().min(0).max(10),
        delay: z.number().positive(),
      }),
      ssl: z.boolean(),
    }),
    logging: z.object({
      level: z.enum(["debug", "info", "warn", "error"]),
      format: z.enum(["json", "text"]),
      output: z.array(z.enum(["console", "file", "elasticsearch"])),
      retention: z.object({
        days: z.number().positive(),
        maxSize: z.string().regex(/^\d+[KMG]B$/),
      }),
    }),
    distributed: z.object({
      masterUrl: z.string().url(),
      workerCount: z.number().positive(),
      loadBalancing: z.object({
        strategy: z.enum(["round-robin", "least-loaded", "capability-based"]),
        maxQueueSize: z.number().positive(),
      }),
      monitoring: z.object({
        enabled: z.boolean(),
        metricsPort: z.number().min(1024).max(65535),
        samplingInterval: z.number().positive(),
      }),
    }),
    security: z.object({
      ssl: z.object({
        enabled: z.boolean(),
        certPath: z.string().optional(),
        keyPath: z.string().optional(),
      }),
      cors: z.object({
        enabled: z.boolean(),
        allowedOrigins: z.array(z.string()),
      }),
      rateLimiting: z.object({
        enabled: z.boolean(),
        maxRequests: z.number().positive(),
        windowMs: z.number().positive(),
      }),
    }),
    performance: z.object({
      cache: z.object({
        enabled: z.boolean(),
        ttl: z.number().positive(),
        maxSize: z.string().regex(/^\d+[KMG]B$/),
      }),
      compression: z.object({
        enabled: z.boolean(),
        level: z.number().min(0).max(9),
      }),
      timeout: z.object({
        global: z.number().positive(),
        api: z.number().positive(),
        database: z.number().positive(),
      }),
    }),
  })
  .refine(
    (data) => {
      // Custom validation: Ensure SSL cert paths are provided if SSL is enabled
      if (data.security.ssl.enabled) {
        return data.security.ssl.certPath && data.security.ssl.keyPath;
      }
      return true;
    },
    {
      message: "SSL certificate paths must be provided when SSL is enabled",
      path: ["security", "ssl"],
    }
  );

type Config = z.infer<typeof ConfigSchema>;

class ConfigManager {
  private static instance: ConfigManager;
  private config: Config;

  private constructor() {
    this.config = this.loadConfig();
  }

  public static getInstance(): ConfigManager {
    if (!ConfigManager.instance) {
      ConfigManager.instance = new ConfigManager();
    }
    return ConfigManager.instance;
  }

  private loadConfig(): Config {
    try {
      // Try to load YAML config first
      const yamlConfig = load(readFileSync("config.yaml", "utf8"));
      return this.validateConfig(yamlConfig);
    } catch (yamlError) {
      try {
        // Fallback to JSON config
        const jsonConfig = JSON.parse(readFileSync("config.json", "utf8"));
        return this.validateConfig(jsonConfig);
      } catch (jsonError) {
        throw new Error(
          "Failed to load configuration from both YAML and JSON files"
        );
      }
    }
  }

  private validateConfig(config: unknown): Config {
    try {
      return ConfigSchema.parse(config);
    } catch (error) {
      if (error instanceof z.ZodError) {
        const formattedError = error.format();
        console.error("Configuration validation failed:", formattedError);
        throw new Error(
          "Invalid configuration: " + JSON.stringify(formattedError, null, 2)
        );
      }
      throw error;
    }
  }

  public getConfig(): Config {
    return this.config;
  }

  public get<T extends keyof Config>(key: T): Config[T] {
    return this.config[key];
  }

  public validate(): void {
    this.validateConfig(this.config);
  }
}

export const config = ConfigManager.getInstance();
