import { Ratelimit } from "@upstash/ratelimit"
import { Redis } from "@upstash/redis"

const redis = new Redis({
  url: process.env.UPSTASH_REDIS_REST_URL!,
  token: process.env.UPSTASH_REDIS_REST_TOKEN!,
})

// Free tier: 1 comic per week (fixed window)
export const freeTierRateLimit = new Ratelimit({
  redis,
  limiter: Ratelimit.fixedWindow(1, "7 d"),
  analytics: true,
  prefix: "ratelimit:free-comics",
})