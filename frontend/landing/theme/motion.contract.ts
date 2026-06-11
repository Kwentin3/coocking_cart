export const motionTokens = {
  duration: {
    fast: "var(--duration-fast)",
    base: "var(--duration-base)",
  },
  easing: {
    standard: "var(--ease-standard)",
  },
  reducedMotion: {
    strategy: "disable-nonessential",
  },
} as const;

export type MotionTokens = typeof motionTokens;
