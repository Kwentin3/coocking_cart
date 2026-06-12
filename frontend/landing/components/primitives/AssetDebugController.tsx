"use client";

import { useEffect } from "react";
import { landingVisualDebugConfig, parseVisualDebugToggle } from "@/landing/config/visualDebug.config";

export function AssetDebugController() {
  useEffect(() => {
    const root = document.documentElement;
    const params = new URLSearchParams(window.location.search);
    const requested = parseVisualDebugToggle(params.get(landingVisualDebugConfig.assetIdsQueryParam));
    let stored: boolean | null = null;
    try {
      stored = parseVisualDebugToggle(window.localStorage.getItem(landingVisualDebugConfig.assetIdsStorageKey));
    } catch {
      stored = null;
    }
    const enabled = requested ?? stored;

    if (requested !== null) {
      try {
        window.localStorage.setItem(landingVisualDebugConfig.assetIdsStorageKey, String(requested));
      } catch {
        // The URL parameter still works for the current page load.
      }
    }

    if (enabled === null) {
      return;
    }

    if (enabled) {
      root.dataset.assetDebugIds = "true";
      return;
    }

    delete root.dataset.assetDebugIds;
  }, []);

  return null;
}
