import { LandingPage } from "@/landing/LandingPage";
import { getLandingPageModel } from "@/landing/lib/getLandingPageModel";
import type { Metadata } from "next";

export function generateMetadata(): Metadata {
  const model = getLandingPageModel();

  return {
    title: model.content.seo.title,
    description: model.content.seo.description,
  };
}

export default function Page() {
  return <LandingPage />;
}
