from __future__ import annotations

from .contracts import PromptTemplate, VisualAssetContract


FOOD_CUTOUT_SQUARE = PromptTemplate(
    id="food.cutout.square",
    version="0.1",
    display_name="Square food cutout",
    purpose="Generate an isolated foreground food object for a layered landing composition.",
    target_section="hero",
    target_asset_kind="cutout",
    recommended_provider="openai",
    visual_contract=VisualAssetContract(
        asset_kind="cutout",
        background_mode="transparent",
        transparent_background=True,
        layer_role="heroForegroundObject",
        z_slot="foreground",
        overlap_policy="productUiOnly",
        safe_area="preserveProductUiCore",
        crop_policy="mayBleed",
        shadow_policy="cssShadowAllowed",
        aspect_ratio="1:1",
        output_format="png",
        constraints=(
            "transparent background with real alpha",
            "clean alpha edge",
            "no baked environment",
            "no readable text",
            "no logos or branded packaging",
            "centered object with predictable bounding box",
            "roughly 12 percent transparent padding",
        ),
    ),
    required_user_approval=True,
    negative_prompt="text, logo, watermark, brand label, packaging, hands, people, dirty table, dark stock blur",
    template=(
        "Create a production candidate image for the TechKitchen landing page.\n"
        "\n"
        "Subject: {subject}\n"
        "\n"
        "Asset contract:\n"
        "- kind: cutout\n"
        "- background: transparent with real alpha, no baked environment\n"
        "- aspect ratio: square 1:1\n"
        "- composition: centered, stable bounding box, about 12 percent transparent padding\n"
        "- usage: foreground food object that may overlap a product UI scene\n"
        "- restrictions: no text, no logos, no brand labels, no people, no famous characters\n"
        "- style: appetizing professional food photography, natural warm kitchen light, not stock-like\n"
        "- output: clean PNG/WebP-style isolated object suitable for web layering\n"
    ),
)


HERO_BACKDROP_KITCHEN = PromptTemplate(
    id="hero.backdrop.kitchen",
    version="0.1",
    display_name="Hero kitchen backdrop",
    purpose="Generate a calm kitchen or production-context backdrop for the hero scene.",
    target_section="hero",
    target_asset_kind="backdrop",
    recommended_provider="gemini",
    visual_contract=VisualAssetContract(
        asset_kind="backdrop",
        background_mode="environment",
        transparent_background=False,
        layer_role="heroBackdrop",
        z_slot="backdrop",
        overlap_policy="sceneOnly",
        safe_area="preserveTextAndCta",
        crop_policy="coverCrop",
        shadow_policy="none",
        aspect_ratio="16:9",
        output_format="png",
        constraints=(
            "calm readable area for text overlay",
            "no visible third-party logos",
            "no readable labels",
            "warm but not one-note orange",
            "not dark stock-like blur",
        ),
    ),
    required_user_approval=True,
    negative_prompt="logo, readable label, messy kitchen, dark blur, heavy vignette, people close-up",
    template=(
        "Create a production candidate hero backdrop for a restaurant technology landing page.\n"
        "\n"
        "Subject: {subject}\n"
        "\n"
        "Asset contract:\n"
        "- kind: backdrop\n"
        "- background: embedded kitchen or food-production environment\n"
        "- aspect ratio: 16:9\n"
        "- preserve a calm readable area for hero text and CTA\n"
        "- no visible third-party logos, no readable labels, no fake product UI\n"
        "- style: professional restaurant prep area, warm natural light, realistic, not stock-like\n"
    ),
)


FINAL_CTA_BRAND_BAND = PromptTemplate(
    id="finalCta.backdrop.brandBand",
    version="0.1",
    display_name="Final CTA brand band",
    purpose="Generate an embedded visual band for the final conversion section.",
    target_section="finalCta",
    target_asset_kind="backdrop",
    recommended_provider="openai",
    visual_contract=VisualAssetContract(
        asset_kind="backdrop",
        background_mode="embedded",
        transparent_background=False,
        layer_role="finalCtaBrandBand",
        z_slot="backdrop",
        overlap_policy="none",
        safe_area="preserveTextAndCta",
        crop_policy="coverCrop",
        shadow_policy="none",
        aspect_ratio="16:9",
        output_format="png",
        constraints=(
            "high-contrast terracotta or warm kitchen brand band",
            "protected calm center area for UI-rendered text and CTA",
            "no baked text",
            "no visible third-party logos",
            "no readable labels or branded packaging",
            "compatible with inverse text and food-service context",
        ),
    ),
    required_user_approval=True,
    negative_prompt="text, logo, watermark, brand label, packaging, people, readable label, messy kitchen, dark blur",
    template=(
        "Create a production candidate visual asset for the TechKitchen landing page final CTA section.\n"
        "\n"
        "Subject: {subject}\n"
        "\n"
        "Asset contract:\n"
        "- kind: backdrop / embedded brand band\n"
        "- background: embedded warm food-service environment, no alpha requirement\n"
        "- aspect ratio: wide 16:9 style composition\n"
        "- preserve a calm center area for UI-rendered heading, buttons and owner-gate text\n"
        "- visual direction: deep terracotta, warm kitchen board, herbs or ingredients near the edges\n"
        "- restrictions: no baked text, no logos, no brand labels, no people, no fake product UI\n"
        "- style: realistic premium food-service backdrop, not stock-like, not cluttered\n"
        "- output: clean bitmap suitable as a decorative brand band layer\n"
    ),
)


PROMPT_TEMPLATES: dict[str, PromptTemplate] = {
    FOOD_CUTOUT_SQUARE.id: FOOD_CUTOUT_SQUARE,
    FINAL_CTA_BRAND_BAND.id: FINAL_CTA_BRAND_BAND,
    HERO_BACKDROP_KITCHEN.id: HERO_BACKDROP_KITCHEN,
}


def list_prompt_templates() -> list[PromptTemplate]:
    return [PROMPT_TEMPLATES[key] for key in sorted(PROMPT_TEMPLATES)]


def get_prompt_template(template_id: str) -> PromptTemplate:
    try:
        return PROMPT_TEMPLATES[template_id]
    except KeyError as exc:
        raise ValueError(f"Unknown prompt template: {template_id}") from exc
