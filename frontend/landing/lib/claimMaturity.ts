export const claimMaturityValues = [
  "implemented_now",
  "mvp_scope",
  "mvp_hypothesis",
  "alpha_next",
  "roadmap_claim",
  "target_product_claim",
  "vision_claim",
  "decision_needed",
  "forbidden_claim",
  "unsupported_claim",
] as const;

export type ClaimMaturity = (typeof claimMaturityValues)[number];

export const claimRefs = [
  "claim.mvp.techcards",
  "claim.target.techcards",
  "claim.target.recipeSystem",
  "claim.target.kitchenDocuments",
  "claim.roadmap.costControl",
  "claim.roadmap.exports",
  "claim.cautious.standards",
  "claim.decision.pricing",
  "claim.decision.onboarding",
] as const;

export type ClaimRef = (typeof claimRefs)[number];

export type ClaimDefinition = {
  id: ClaimRef;
  maturity: ClaimMaturity;
  source: string;
  publicPolicy: "render" | "cautious" | "disabled" | "hidden";
};

export const claimRegistry: Record<ClaimRef, ClaimDefinition> = {
  "claim.mvp.techcards": {
    id: "claim.mvp.techcards",
    maturity: "mvp_scope",
    source: "docs/лэндинг/mvp-landing-traceability-matrix.md",
    publicPolicy: "render",
  },
  "claim.target.techcards": {
    id: "claim.target.techcards",
    maturity: "target_product_claim",
    source: "docs/product/PRODUCT_VISION_v0.1.md",
    publicPolicy: "render",
  },
  "claim.target.recipeSystem": {
    id: "claim.target.recipeSystem",
    maturity: "target_product_claim",
    source: "docs/product/PRODUCT_VISION_v0.1.md",
    publicPolicy: "render",
  },
  "claim.target.kitchenDocuments": {
    id: "claim.target.kitchenDocuments",
    maturity: "target_product_claim",
    source: "docs/лэндинг/LANDING_PRD_v0.1.md",
    publicPolicy: "render",
  },
  "claim.roadmap.costControl": {
    id: "claim.roadmap.costControl",
    maturity: "roadmap_claim",
    source: "docs/product/PRODUCT_CAPABILITY_ROADMAP_v0.1.md",
    publicPolicy: "cautious",
  },
  "claim.roadmap.exports": {
    id: "claim.roadmap.exports",
    maturity: "roadmap_claim",
    source: "docs/product/PRODUCT_CAPABILITY_ROADMAP_v0.1.md",
    publicPolicy: "disabled",
  },
  "claim.cautious.standards": {
    id: "claim.cautious.standards",
    maturity: "mvp_hypothesis",
    source: "docs/лэндинг/LANDING_PRD_v0.1.md",
    publicPolicy: "cautious",
  },
  "claim.decision.pricing": {
    id: "claim.decision.pricing",
    maturity: "decision_needed",
    source: "docs/лэндинг/LANDING_IMPLEMENTATION_HANDOFF_v0.1.md",
    publicPolicy: "hidden",
  },
  "claim.decision.onboarding": {
    id: "claim.decision.onboarding",
    maturity: "decision_needed",
    source: "docs/лэндинг/LANDING_IMPLEMENTATION_HANDOFF_v0.1.md",
    publicPolicy: "hidden",
  },
};

export function isForbiddenMaturity(maturity: ClaimMaturity) {
  return maturity === "forbidden_claim" || maturity === "unsupported_claim";
}

export function getClaim(ref: ClaimRef) {
  return claimRegistry[ref];
}
