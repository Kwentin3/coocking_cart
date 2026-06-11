# Asset Provenance and Rights Contract

Статус: рабочий контракт для AI-generated assets.
Дата доступа к внешним источникам: 2026-06-11.

Связанные документы:

* [AI Asset Generation Pipeline](ai-asset-generation-pipeline.md)
* [Provider Research](asset-generation-provider-research.md)
* [Asset Generation ADR](asset-generation-adr.md)
* [Asset & Icon Registry Contract](лэндинг/LANDING_ASSET_ICON_REGISTRY_CONTRACT_v0.1.md)

## 1. Purpose

Этот документ фиксирует, какие metadata и gates нужны, чтобы AI-generated assets можно было безопасно использовать в публичном лендинге.

Generated asset считается publishable только если:

* известен источник;
* известен provider/model;
* известен prompt hash;
* есть approval;
* есть rights status;
* есть safety flags;
* есть rollback target.

## 2. External Terms Snapshot

По [Gemini API Additional Terms](https://ai.google.dev/gemini-api/terms), дата доступа 2026-06-11:

* Google не заявляет ownership на generated content.
* Google может сгенерировать такой же или похожий контент другим пользователям.
* разработчик/пользователь отвечает за использование результата;
* attribution может потребоваться в зависимости от применимого права и условий API.

По [Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing), дата доступа 2026-06-11:

* pricing table маркирует free tier как `Used to improve our products: Yes`;
* paid tier маркируется как `No`.

По [Zero data retention in Gemini Developer API](https://ai.google.dev/gemini-api/docs/zdr), дата доступа 2026-06-11:

* paid services не используют prompts/responses для улучшения продуктов;
* это не отменяет необходимость учитывать abuse monitoring and operational metadata.

По [Imagen docs](https://ai.google.dev/gemini-api/docs/imagen) и [Gemini image generation docs](https://ai.google.dev/gemini-api/docs/image-generation), дата доступа 2026-06-11:

* generated images include SynthID watermark.

## 3. Provenance Metadata

```ts
export type AssetRightsStatus =
  | "unchecked"
  | "approved_for_internal_preview"
  | "approved_for_public_landing"
  | "blocked"
  | "needs_legal_review";

export type AssetProvenance = {
  source: "manual" | "generated" | "licensed" | "stock" | "internal";
  generatedCandidateId?: string;
  provider?: string;
  model?: string;
  providerRequestId?: string;
  generatedAt?: string;
  generatedBy?: string;
  promptHash?: string;
  promptSummary?: string;
  promptStored: boolean;
  promptTemplateKey?: string;
  promptTemplateVersion?: string;
  inputAssetKeys?: string[];
  referenceAssetKeys?: string[];
  synthIdWatermarkExpected?: boolean;
  rightsStatus: AssetRightsStatus;
  rightsReviewedBy?: string;
  rightsReviewedAt?: string;
  commercialUseChecked: boolean;
  containsPeople: boolean;
  containsRecognizablePerson: boolean;
  containsBrandElements: boolean;
  containsThirdPartyLogo: boolean;
  containsKnownCharacter: boolean;
  containsArtistStyleRequest: boolean;
  approvalStatus: "draft" | "pending_review" | "approved" | "rejected" | "published" | "archived";
  approvedBy?: string;
  approvedAt?: string;
  publishedBy?: string;
  publishedAt?: string;
};
```

## 4. Rights Rules

Запрещено без отдельного high-risk approval:

* использовать чужие логотипы;
* имитировать конкретные бренды;
* имитировать известных персонажей;
* имитировать конкретных живых художников или узнаваемый contemporary style;
* генерировать узнаваемых реальных людей;
* использовать reference images без подтвержденных прав;
* публиковать testimonial avatar так, будто это реальный клиент, если это placeholder.

Разрешено для обычного approval:

* food decor без брендов;
* generic kitchen background без людей;
* neutral dish photo без чужих trade dress;
* abstract/document-neutral visual;
* clearly synthetic placeholder with internal marker.

## 5. People Policy

Default v1:

* `personGeneration` should be disabled where provider supports it for decor/background assets.
* People-containing assets require manual review.
* Recognizable real persons are blocked unless explicit rights are documented.
* Children/minors should not be generated for landing assets.
* Generated testimonial avatars must be labeled internally as synthetic placeholders and cannot be presented as real customer photos.

Cutout/layering note:

* `cutout` with a person/human subject is still a people asset even if background is transparent.
* Transparent background does not reduce rights/safety requirements.
* Hero human cutouts require explicit manual approval before public landing use.
* Edge decor and food cutouts can be lower risk, but still need provenance and approval before publication.

## 6. Prompt Storage Policy

Prompts can reveal internal brand strategy. Store them deliberately.

Recommended v1:

* store full prompt for approved/published assets only if access-controlled;
* always store `promptHash`;
* store `promptSummary` for audit and future regeneration;
* do not include raw secrets, customer data, private business plans or credentials in prompts;
* never expose prompts to public frontend.

## 7. Publication Gate

An asset can be published only if:

* candidate status is `approved`;
* `rightsStatus` is `approved_for_public_landing`;
* `commercialUseChecked` is true;
* checksum is present;
* storage path is stable;
* CDN/public URL is known, if public delivery is enabled;
* rollback asset key is known when replacing an existing asset;
* provenance fields are complete.

## 8. Audit Events

Required events:

* `asset_generation_requested`;
* `asset_generation_completed`;
* `asset_candidate_rejected`;
* `asset_candidate_approved`;
* `asset_candidate_published`;
* `asset_registry_updated`;
* `asset_replacement_rolled_back`;
* `asset_rights_review_requested`;
* `asset_rights_review_completed`.

Audit log must not include raw provider credentials.
