# AI Asset Generation Pipeline

Статус: архитектурный blueprint, без реализации кода.
Версия: 0.1.
Дата доступа к внешним источникам: 2026-06-11.

Связанные документы:

* [Landing Control Plane Blueprint](landing-control-plane-blueprint.md)
* [Provider Research](asset-generation-provider-research.md)
* [Asset Generation ADR](asset-generation-adr.md)
* [Asset Provenance and Rights](asset-provenance-and-rights.md)
* [Asset & Icon Registry Contract](лэндинг/LANDING_ASSET_ICON_REGISTRY_CONTRACT_v0.1.md)
* [Landing Production Asset Brief](лэндинг/LANDING_PRODUCTION_ASSET_BRIEF_v0.1.md)
* [Landing Product Positioning Summary](лэндинг/product-positioning-canonical-summary.md)
* [Product Vision](product/PRODUCT_VISION_v0.1.md)
* [Capability Roadmap](product/PRODUCT_CAPABILITY_ROADMAP_v0.1.md)

## 1. Executive Summary

AI Asset Generation Pipeline добавляет в Landing Control Plane управляемый контур генерации изображений через Gemini / Imagen / Vertex AI или другой provider.

Главный инвариант:

**Агент не публикует generated image напрямую в лендинг. Агент создает Generated Asset Candidate, пользователь смотрит preview, затем вручную approve/reject, и только после approve ассет может попасть в Asset Registry.**

Рекомендация для v1:

* backend-only integration;
* paid Gemini Developer API auth key;
* Google Gen AI SDK как совместимый SDK для будущей миграции на Vertex / Gemini Enterprise Agent Platform;
* object storage для candidates и approved assets;
* ручной approval перед публикацией;
* provenance metadata обязательно;
* no auto-publish;
* no free tier для реальных брендовых или коммерческих ассетов.

## 2. Problem Statement

Лендинг «ТехКухня» требует hero visuals, food photos, decorative assets, backgrounds, audience photos и document-related visuals. Если эти ассеты генерируются вручную вне системы, Asset Registry быстро расходится с фактическими файлами. Если агент сразу вставляет результат генерации в сайт, появляется риск публикации неподходящих изображений, проблем с правами, неуправляемых расходов и сложного rollback.

Нужен pipeline, который делает генерацию управляемой:

* provider capabilities известны заранее;
* prompt templates версионируются;
* candidates отделены от published assets;
* approve/reject фиксируется;
* Asset Registry обновляется только после validation;
* section content использует только asset key.

## 3. Goals / Non-Goals

Goals:

* спроектировать provider registry;
* спроектировать prompt template registry;
* спроектировать GeneratedAssetCandidate;
* спроектировать approval workflow;
* расширить Asset Registry;
* расширить `landingctl`;
* описать security/privacy/rights/provenance;
* описать preview/diff/rollback;
* дать provider recommendation.

Non-goals для v1:

* не строить полноценный DAM;
* не делать auto-publish;
* не генерировать product UI mockups вместо реальных UI-компонентов;
* не использовать free tier для production assets;
* не использовать reference images без подтвержденных прав;
* не решать юридическую экспертизу автоматически.

## 4. User Workflow

1. Пользователь в чате просит ассет: например «нужна новая hero-фотография повара для теплой ресторанной темы».
2. Агент вызывает `landingctl inspect hero`.
3. Агент получает allowed asset kinds, aspect ratios, style constraints, prompt templates and risk level.
4. Агент выбирает prompt template.
5. Агент создает draft prompt.
6. Пользователь подтверждает генерацию, если запрос medium/high risk.
7. CLI вызывает provider через backend-only credentials.
8. Система сохраняет candidates в preview storage.
9. Пользователь смотрит preview gallery.
10. Пользователь approve/reject candidate.
11. Approved asset проходит post-processing.
12. Asset сохраняется в approved storage/CDN.
13. Asset Registry получает new asset key.
14. Section content patch заменяет asset key.
15. Система запускает validate / preview / diff.
16. Пользователь подтверждает publish.

## 5. Target Architecture

```text
Agent Chat
  -> Agent Operation
  -> landingctl assets generate
  -> Prompt Template Registry
  -> Generation Provider Registry
  -> Gemini / Imagen / Vertex AI
  -> Generated Asset Candidate
  -> Preview Gallery
  -> User Approval
  -> Post-processing
  -> Object Storage
  -> Asset Registry
  -> Section Content Patch
  -> Validate / Preview / Diff / Publish
```

Новые компоненты:

| Компонент | Ответственность |
| --- | --- |
| Generation Provider Registry | Capabilities, auth mode, model list, pricing/rate metadata, production readiness. |
| Prompt Template Registry | Версионированные templates для asset kinds and sections. |
| Asset Generation Request | Нормализованный запрос на генерацию. |
| Generated Asset Candidate | Временный результат provider call до approval. |
| Preview Gallery | UI/route для сравнения candidates. |
| Approval Workflow | State machine approve/reject/publish/archive. |
| Post-processing Pipeline | Resize/crop/format conversion/checksum/metadata. |
| Object Storage | Candidate and approved asset storage. |
| Asset Registry Publishing | Создание/обновление stable asset key. |
| Provenance Metadata | Provider/model/prompt/source/rights/safety/audit fields. |
| Safety / Rights Gate | Проверка людей, логотипов, брендов, reference images, commercial use. |
| Rollback | Возврат предыдущего asset key and registry metadata. |

## 6. Provider Research Summary

Сводка исследования вынесена в [Provider Research](asset-generation-provider-research.md).

Ключевые факты:

* Gemini API использует API keys; новые ключи в AI Studio создаются как auth keys.
* Google объявляет ограничения для standard keys: 2026-06-19 для unrestricted standard keys и September 2026 для standard keys в целом.
* OAuth доступен, но для v1 asset generation не нужен, так как сценарий backend-only и не требует user-delegated Google access.
* Google Gen AI SDK позволяет прототипировать на Developer API и мигрировать на Gemini Enterprise Agent Platform.
* Gemini native image generation поддерживает Nano Banana image models, image editing/reference workflows и SynthID watermark.
* Imagen 4 в Gemini API подходит для photorealistic generation, поддерживает 1-4 outputs, английские prompts, ограниченный набор aspect ratios.
* Paid tier предпочтителен: pricing docs показывают, что free tier data can be used to improve products, paid tier marked as not used to improve products.
* Rate limits project-level and model/tier-dependent; image models can have IPM.

## 7. Provider Selection Recommendation

v1:

* `gemini-native-image` через Gemini Developer API paid tier как default provider.
* `imagen` через Gemini Developer API как optional provider для photorealistic food/background.
* `mock-provider` для dev/test и CLI tests.

Production upgrade:

* `vertex-ai-gemini-image` / `vertex-ai-imagen` через Agent Platform with service account/IAM.

Не рекомендовано для v1:

* direct Vertex-first rollout без подтвержденной инфраструктурной потребности;
* free tier;
* auto-publish generated assets.

## 8. Authentication Strategy

v1:

* credentials только на backend;
* использовать paid Gemini Developer API auth key;
* хранить key в env или secret manager;
* не отдавать key агенту в prompt/context;
* не писать key в logs, diffs, preview metadata;
* separate dev/stage/prod credentials;
* restrict key to Gemini API where applicable;
* maintain billing project and spending alerts.

Production:

* migrate provider to Vertex / Agent Platform;
* use service account / IAM / ADC;
* use least privilege;
* enable Cloud audit/cost controls;
* configure region and quota explicitly.

OAuth:

* не нужен для v1;
* использовать только если появится сценарий user-delegated Google access.

## 9. GenerationProviderRegistry

```ts
export type GenerationProvider = {
  key: string;
  displayName: string;
  providerFamily: "google-gemini" | "google-imagen" | "vertex-ai" | "mock" | "other";
  authMode: "backend-api-key" | "oauth" | "adc" | "service-account" | "none";
  models: Array<{
    id: string;
    status: "stable" | "preview" | "deprecated" | "unknown";
    supportsTextToImage: boolean;
    supportsImageToImage: boolean;
    supportsEditing: boolean;
    supportsReferenceImages: boolean;
    supportsTransparentBackground: boolean;
    supportedAssetKinds: GeneratedAssetKind[];
    supportedAspectRatios: string[];
    supportedOutputFormats: Array<"png" | "webp" | "jpg">;
    maxOutputSize?: string;
    maxImagesPerRequest?: number;
  }>;
  pricingMetadata?: {
    unit: "image" | "token" | "request";
    notes: string;
    lastCheckedAt: string;
    sourceUrl: string;
  };
  rateLimitMetadata?: {
    dimensions: Array<"RPM" | "TPM" | "RPD" | "IPM">;
    projectLevel: boolean;
    notes: string;
  };
  productionReadiness: "dev-only" | "v1-ok" | "production-ok" | "needs-review";
  safetyNotes: string[];
};
```

Initial providers:

* `gemini-native-image`;
* `imagen`;
* `vertex-ai-gemini-image`;
* `vertex-ai-imagen`;
* `mock-provider`.

## 10. PromptTemplateRegistry

Prompts are content-governed artifacts. They must not be hardcoded in CLI/API code.

Prompt templates that generate hero, audience, documents or CTA visuals must align with [Product Vision](product/PRODUCT_VISION_v0.1.md), [Capability Roadmap](product/PRODUCT_CAPABILITY_ROADMAP_v0.1.md) and [Landing Product Positioning Summary](лэндинг/product-positioning-canonical-summary.md).

Important refinement: visuals may sell the Target Product, not only the MVP-safe chat prototype. A hero visual can therefore suggest a mature system around технологические карты, рецептуры, расчеты, документы and стандартизацию кухни. Prompt templates must rely on Product Vision first, then Capability Roadmap for maturity boundaries.

Safety rules still apply:

* do not generate visuals that imply `forbidden_claim`;
* do not generate visuals that imply `unsupported_claim`;
* do not show legal approval, automatic compliance or AI autonomous document approval;
* do not show ready 1С/iiko/r_keeper/StoreHouse import unless integration is approved and implemented;
* do not show DOCX/PDF export as currently available unless export exists;
* if a visual shows a roadmap/target-product function, that function must be present in Capability Roadmap;
* do not show roadmap/vision UI states as current availability without an explicit visual marker or owner-approved framing.

```ts
export type PromptTemplate = {
  id: string;
  version: string;
  purpose: string;
  targetAssetKind: GeneratedAssetKind;
  targetSection: LandingSectionId;
  recommendedProvider: string;
  allowedStyleTokens: string[];
  forbiddenClaims: string[];
  forbiddenVisualElements: string[];
  aspectRatio: string;
  outputFormat: "png" | "webp" | "jpg";
  negativePrompt?: string;
  exclusionRules: string[];
  requiredUserApproval: boolean;
  notesForAgent: string[];
  template: string;
};
```

Minimum templates:

* `hero.chef.visual`;
* `hero.dish.visual`;
* `hero.background.kitchen`;
* `audience.restaurant.photo`;
* `audience.chef.photo`;
* `audience.production.photo`;
* `audience.technologist.photo`;
* `documents.dish.sample`;
* `finalCta.food.decor`;
* `standards.food.decor`;
* `decor.herbs`;
* `decor.spices`;
* `decor.vegetables`;
* `avatar.testimonial.placeholder`.

Prompt rules:

* no known brand names unless rights are documented;
* no living artist style imitation;
* no fake legal claims in document previews;
* no readable UI text in generated product mockups unless explicitly approved;
* prefer English prompts for Imagen;
* prompt template version must be stored in candidate provenance.

## 11. GeneratedAssetCandidate Model

```ts
export type GeneratedAssetKind =
  | "photo"
  | "decor"
  | "background"
  | "product-ui"
  | "illustration"
  | "avatar"
  | "document-preview";

export type GeneratedAssetCandidate = {
  id: string;
  status:
    | "draft_prompt"
    | "generating"
    | "generated"
    | "pending_review"
    | "approved"
    | "rejected"
    | "published"
    | "archived"
    | "failed";

  provider: string;
  model: string;
  providerRequestId?: string;

  prompt: string;
  negativePrompt?: string;
  promptHash: string;
  promptTemplateKey?: string;
  promptTemplateVersion?: string;

  targetAssetKey?: string;
  targetSection?: string;
  assetKind: GeneratedAssetKind;

  aspectRatio: string;
  outputFormat: "png" | "webp" | "jpg";

  previewUrl: string;
  storageUrl?: string;
  cdnUrl?: string;

  width?: number;
  height?: number;
  sizeBytes?: number;
  checksum?: string;

  generatedAt: string;
  generatedBy: string;
  approvedAt?: string;
  approvedBy?: string;
  publishedAt?: string;
  publishedBy?: string;

  rejectionReason?: string;

  provenance: {
    sourcePromptHash: string;
    promptStored: boolean;
    inputAssetKeys?: string[];
    referenceAssetKeys?: string[];
    synthIdWatermarkExpected?: boolean;
    rightsChecked: boolean;
    rightsStatus:
      | "unchecked"
      | "approved_for_internal_preview"
      | "approved_for_public_landing"
      | "blocked"
      | "needs_legal_review";
    containsPeople: boolean;
    containsBrandElements: boolean;
    containsRecognizablePerson: boolean;
    containsThirdPartyLogo: boolean;
    containsKnownCharacter: boolean;
    commercialUseChecked: boolean;
  };
};
```

## 12. AssetApprovalWorkflow

Allowed state flow:

```text
draft_prompt
  -> generating
  -> generated
  -> pending_review
  -> approved -> published -> archived
  -> rejected -> archived
  -> failed
```

Rules:

* generated asset не попадает в production registry без approve;
* rejected asset cannot be referenced by landing content;
* published asset получает stable `assetKey`;
* previous asset remains registered or archived for rollback;
* publishing updates metadata and provenance;
* people/logo/brand/reference-image cases require safety/rights gate;
* auto-publish is high risk and disabled for v1.

## 13. AssetRegistry Integration

Generated fields to add to asset registry:

```ts
export type LandingAsset = {
  key: LandingAssetKey;
  source: "manual" | "generated" | "licensed" | "stock" | "internal";
  generatedCandidateId?: string;
  provider?: string;
  model?: string;
  promptHash?: string;
  provenance?: AssetProvenance;
  rightsStatus?: AssetRightsStatus;
  approvalStatus?: "manual" | "approved" | "published" | "archived";
  approvedBy?: string;
  approvedAt?: string;
  version: number;
  replacesAssetKey?: LandingAssetKey;
  rollbackAssetKey?: LandingAssetKey;
  cdnUrl?: string;
  storagePath?: string;
};
```

Generated vs manual:

* manual assets may have `source: "manual"` and no provider metadata;
* generated assets must include candidate id, provider, model, prompt hash and rights status;
* generated assets require approval fields before public use;
* generated assets can replace existing keys only through `assets replace`.

## 14. Storage and CDN Strategy

Recommended v1:

```text
object-storage/
  landing-assets/
    candidates/
      <candidateId>/original.png
      <candidateId>/preview.webp
      <candidateId>/metadata.json
    approved/
      <assetKey>/v1/original.png
      <assetKey>/v1/desktop.webp
      <assetKey>/v1/mobile.webp
      <assetKey>/v1/metadata.json
```

Rules:

* candidates are not public by default;
* preview uses signed URLs or backend proxy;
* approved assets get stable storage path;
* published assets get CDN URL;
* rejected candidates have retention policy;
* original provider output is preserved for audit;
* derived formats are generated by post-processing.

Format policy:

* WebP for web delivery;
* JPEG for photos without transparency;
* PNG/WebP with alpha for `cutout` and `edgeDecor` assets;
* embedded-background image formats for `contentImage` and `documentPreview` assets;
* original retained;
* checksum for every stored file.

Asset kind prompt guidance:

For the first public landing production package, use [Landing Production Asset Brief](лэндинг/LANDING_PRODUCTION_ASSET_BRIEF_v0.1.md) as the operative brief for hero backdrop, hero human cutout, hero food cutout, final CTA brand band, edge decor and optional content image candidates.

| Asset kind | Prompt/output requirement |
| --- | --- |
| `cutout` | Transparent background, clean alpha, no baked environment, predictable bounding box, optional separate shadow. |
| `contentImage` | Composed photo/illustration with embedded background and stable crop. |
| `backdrop` | Environment image or brand band background with calm center and overlay-ready area. |
| `productUi` | Readable UI mockup; no unsupported current-availability claim. |
| `edgeDecor` | Transparent food/decor objects for page edges; no text; no center obstruction. |
| `documentPreview` | Embedded background, readable document/card crop, no fake legal finality. |

## 15. CLI/API Proposal

CLI:

```bash
landingctl assets providers list
landingctl assets providers inspect <providerKey>

landingctl assets prompt-templates list
landingctl assets prompt-templates inspect <templateKey>

landingctl assets generate --section hero --kind photo --template hero.chef.visual
landingctl assets generate --asset-key hero.chef --template hero.chef.visual --count 4

landingctl assets candidates list --section hero
landingctl assets candidates inspect <candidateId>
landingctl assets candidates preview <candidateId>

landingctl assets approve <candidateId> --asset-key hero.chef.v2
landingctl assets reject <candidateId> --reason "reason text"

landingctl assets publish <candidateId>
landingctl assets replace hero.chef --with hero.chef.v2

landingctl assets validate <assetKey>
landingctl assets validate-candidate <candidateId>
landingctl assets provenance <assetKey>

landingctl validate hero
landingctl preview
landingctl diff
landingctl rollback
```

API can be added later:

* `GET /landing/assets/providers`
* `GET /landing/assets/providers/{providerKey}`
* `GET /landing/assets/prompt-templates`
* `POST /landing/assets/generations`
* `GET /landing/assets/candidates`
* `GET /landing/assets/candidates/{candidateId}`
* `POST /landing/assets/candidates/{candidateId}/approve`
* `POST /landing/assets/candidates/{candidateId}/reject`
* `POST /landing/assets/candidates/{candidateId}/publish`
* `POST /landing/assets/replace`
* `GET /landing/assets/{assetKey}/provenance`

## 16. Preview / Approval UI

Minimum v1 UI:

* candidate gallery;
* metadata panel;
* provider/model/prompt template/version;
* generated dimensions and output format;
* old asset vs candidate comparison;
* section preview with candidate injected temporarily;
* approve/reject controls;
* rights checklist;
* warning if image contains people/brand/logo/reference inputs.

No candidate should be publishable from gallery without explicit approval.

## 17. Risk Model

| Risk | Operations | Requirements |
| --- | --- | --- |
| Low | inspect providers, inspect templates, draft prompt, generate candidate without publish, reject candidate | validation, audit event |
| Medium | approve candidate, publish approved asset, replace asset key in section content, edit prompt template, switch provider for asset kind | validation, preview, diff, user confirmation, audit event |
| High | enable auto-publish, change provider credentials, change provider contract, change safety policy, publish people/logo/brand/reference-image asset, change storage/CDN policy | explicit approval, security review, build/preview, audit log, rollback plan |

Default policy:

* generating a candidate is not publishing, so it can be low risk if prompt does not include people/brands/reference images;
* approving/publishing is at least medium risk;
* people/brand/logo/reference images are high risk.

## 18. Security and Privacy

Requirements:

* credentials only on backend;
* no API keys in frontend;
* no raw provider credentials in agent context;
* use secret manager or env;
* separate dev/stage/prod credentials;
* least-privilege provider credentials;
* provider calls logged without secrets;
* no private brand/customer/user materials in free tier;
* prompt/provenance access-controlled;
* prompt may contain internal visual strategy, so do not expose it publicly;
* provider request/response logs must redact secrets and signed URLs.

Data use policy:

* paid tier only for real project assets;
* free tier only for throwaway experiments without confidential data;
* implementation must re-check current Google terms before enabling production generation.

## 19. Rights / Provenance / SynthID

Rules:

* generated asset records must store provider/model/prompt hash/time/user;
* SynthID expected flag is stored when provider docs say generated images include SynthID;
* commercial-use check is required before public landing use;
* Google does not claim ownership over generated content, but may generate similar content for others;
* responsibility for using generated content remains with the project;
* no famous characters, third-party logos, brand imitation or living artist style imitation without explicit review;
* people images require extra safety gate;
* generated testimonial avatars cannot be presented as real customer photos.

Detailed contract: [Asset Provenance and Rights](asset-provenance-and-rights.md).

## 20. Rate Limits / Billing Guardrails

Guardrails:

* per-provider daily candidate count;
* per-user/session generation count;
* max candidates per request, default 4;
* spend cap by environment;
* IPM/RPM/RPD aware queue;
* retry with backoff for rate limit errors;
* no background batch generation without explicit task;
* pricing metadata stored with provider registry and last-checked date;
* alert when actual provider pricing/rate limits differ from registry snapshot.

## 21. Monitoring and Audit Log

Required audit events:

* `asset_generation_requested`;
* `asset_generation_started`;
* `asset_generation_completed`;
* `asset_generation_failed`;
* `asset_candidate_previewed`;
* `asset_candidate_approved`;
* `asset_candidate_rejected`;
* `asset_candidate_published`;
* `asset_registry_updated`;
* `asset_replacement_rolled_back`;
* `asset_rights_review_requested`;
* `asset_rights_review_completed`.

Monitoring:

* provider error rate;
* blocked safety rate;
* average generation latency;
* candidates per day;
* approved/published ratio;
* spend estimate;
* storage growth;
* rejected cleanup backlog.

## 22. Rollback and Cleanup

Rollback:

* replacing `hero.chef` with `hero.chef.v2` stores `rollbackAssetKey: "hero.chef"`;
* old asset remains available until retention/archive policy allows deletion;
* rollback updates section content and registry metadata;
* rollback does not delete candidate/provenance.

Cleanup:

* rejected candidates retained for configured period;
* failed candidates can be deleted sooner unless needed for debugging;
* approved but unpublished candidates should expire or require re-review;
* storage cleanup must not delete published or rollback assets.

## 23. Implementation Phases

### Phase A — Research and ADR

* verify Gemini/Imagen/Vertex docs;
* decide provider strategy;
* decide paid tier and billing project;
* record ADR.

### Phase B — Contracts

* `GenerationProviderRegistry`;
* `PromptTemplateRegistry`;
* `GeneratedAssetCandidate` schema;
* `AssetProvenance` schema;
* `AssetApprovalWorkflow`.

### Phase C — Storage

* candidate storage;
* approved asset storage;
* CDN/public URLs;
* metadata DB or Git-backed JSON;
* retention policy.

### Phase D — CLI/API

* generate;
* candidates list/inspect/preview;
* approve/reject;
* publish;
* replace;
* validate;
* provenance.

### Phase E — UI/Preview

* preview gallery;
* approval screen;
* side-by-side comparison;
* section preview.

### Phase F — Production Hardening

* credentials;
* rate limits;
* billing guardrails;
* audit log;
* safety gate;
* rollback;
* monitoring.

## 24. Acceptance Criteria

1. AI Asset Generation Pipeline has its own docs.
2. Provider facts cite official sources and access date.
3. Provider selection is explicit.
4. Auth strategy is backend-only.
5. GeneratedAssetCandidate contract exists.
6. PromptTemplateRegistry exists.
7. GenerationProviderRegistry exists.
8. Approval workflow exists.
9. Asset Registry integration includes provenance fields.
10. CLI/API operations are defined.
11. Security/privacy requirements are defined.
12. Rights/provenance/SynthID requirements are defined.
13. Billing/rate-limit guardrails exist.
14. Rollback and cleanup are defined.
15. No auto-publish in v1.
16. No code implementation starts without explicit confirmation.

## 25. Open Questions

1. Final v1 provider: Gemini Developer API only, or Gemini + Imagen?
2. Paid billing project owner?
3. Object storage: Google Cloud Storage, Selectel/S3-compatible, local first, other?
4. Metadata storage: Git-backed JSON first or DB immediately?
5. Default number of candidates: 2, 3 or 4?
6. Are people-containing images allowed at all for v1?
7. Are reference images allowed at all for v1?
8. Store full prompt or only hash + summary?
9. Retention period for rejected candidates?
10. Who can approve assets?
11. Is manual legal review required for public hero images?
12. Should SynthID verification be part of acceptance?
13. Which asset kinds must remain manual only?

## 26. Agent Recommendations

Simplify v1:

* one paid Gemini provider path;
* one object storage backend;
* one CLI, no API until preview UI appears;
* generate candidates only, no direct registry mutation;
* no people/reference images unless explicitly approved.

Accept now:

* provider registry;
* prompt template registry;
* candidate model;
* approval workflow;
* provenance fields in Asset Registry;
* billing/rate limit caps;
* paid tier only.

Defer:

* full DAM;
* visual mini-CMS;
* multiple providers beyond Google + mock;
* auto-publish;
* automatic legal checks;
* public prompt gallery.

Create later as standalone docs if Landing Control Plane moves from blueprint to implementation:

* `docs/agent-operations.md` — agent operation catalog, risk gates and approval events.
* `docs/landingctl-cli.md` — CLI/API command contract, request/response examples and exit codes.
* `docs/risk-model.md` — shared risk policy for content, assets, providers and credentials.
* `docs/security-privacy.md` — credentials, prompt storage, data-use policy and audit scope.
* `docs/preview-diff-rollback.md` — preview gallery, metadata diff, section diff and rollback playbooks.
* `docs/asset-registry.md` — standalone registry schema if the current landing contract becomes too large.

Minimum safe MVP:

* `mock-provider`;
* one real backend provider behind feature flag;
* candidate generation for decorative non-people assets;
* preview gallery;
* manual approval;
* asset registry publish;
* section preview and rollback.
