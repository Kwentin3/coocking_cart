export const landingModes = ["showcase", "beta", "launch", "internal", "maintenance"] as const;

export type LandingMode = (typeof landingModes)[number];

export const landingFunctionKeys = [
  "demoRequest",
  "sampleProject",
  "signup",
  "pricing",
  "documentExport",
  "mvpEntry",
] as const;

export type LandingFunctionKey = (typeof landingFunctionKeys)[number];

export type LandingModeConfig = {
  mode: LandingMode;
  ownerGates: Record<LandingFunctionKey, boolean> & {
    landingMode: boolean;
    publicLaunch: boolean;
  };
  functionAvailability: Record<LandingFunctionKey, boolean>;
  mvpEntry: {
    href?: string;
    urlSource: "NEXT_PUBLIC_MVP_ENTRY_URL";
    accessibleLabel: string;
    visibleLabel: "none";
    placement: "header-right";
    role: "service-entry";
    auth: "handled-by-mvp";
  };
};

function readMvpEntryHref() {
  const rawHref = process.env.NEXT_PUBLIC_MVP_ENTRY_URL?.trim();

  if (!rawHref) {
    return undefined;
  }

  if (
    rawHref.startsWith("/")
    && !rawHref.startsWith("//")
    && !rawHref.includes("\\")
    && !rawHref.includes("?")
    && !rawHref.includes("#")
  ) {
    return rawHref.replace(/\/+$/, "") || "/";
  }

  try {
    const url = new URL(rawHref);
    return url.protocol === "https:" || url.protocol === "http:" ? url.toString() : undefined;
  } catch {
    return undefined;
  }
}

const mvpEntryHref = readMvpEntryHref();

// STICKY-MVP-ENTRY:
// The MVP URL/path is temporary and must come from config/env.
// Do not hardcode deployment domains in sections or components.
export const mvpEntryConfig: LandingModeConfig["mvpEntry"] = {
  href: mvpEntryHref,
  urlSource: "NEXT_PUBLIC_MVP_ENTRY_URL",
  accessibleLabel: "Вход в MVP",
  visibleLabel: "none",
  placement: "header-right",
  role: "service-entry",
  auth: "handled-by-mvp",
};

// STICKY-ACTION-POLICY:
// Default mode is showcase. Future mode changes belong in this config/resolver layer, not in sections.
export const landingModeConfig: LandingModeConfig = {
  mode: "showcase",
  ownerGates: {
    landingMode: true,
    publicLaunch: false,
    demoRequest: true,
    sampleProject: true,
    signup: false,
    pricing: false,
    documentExport: false,
    mvpEntry: true,
  },
  functionAvailability: {
    demoRequest: true,
    sampleProject: true,
    signup: false,
    pricing: false,
    documentExport: false,
    mvpEntry: Boolean(mvpEntryConfig.href),
  },
  mvpEntry: mvpEntryConfig,
};
