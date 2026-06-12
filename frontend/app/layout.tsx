import type { Metadata, Viewport } from "next";
import { AssetDebugController } from "@/landing/components/primitives/AssetDebugController";
import { landingVisualDebugConfig } from "@/landing/config/visualDebug.config";
import "./globals.css";

export const metadata: Metadata = {
  title: "ТехКухня",
  description: "Управляемый лендинг целевого продукта ТехКухня.",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ru" data-asset-debug-ids={landingVisualDebugConfig.assetIdsEnabledByDefault ? "true" : undefined}>
      <body>
        <AssetDebugController />
        {children}
      </body>
    </html>
  );
}
