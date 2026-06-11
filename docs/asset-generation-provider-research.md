# AI Asset Generation Provider Research

Статус: research snapshot для AI Asset Generation Pipeline.
Дата доступа к источникам: 2026-06-11.
Область: Gemini Developer API, Gemini native image generation, Imagen, Vertex AI / Gemini Enterprise Agent Platform.

Связанные документы:

* [AI Asset Generation Pipeline](ai-asset-generation-pipeline.md)
* [Asset Generation ADR](asset-generation-adr.md)
* [Asset Provenance and Rights](asset-provenance-and-rights.md)
* [Landing Control Plane Blueprint](landing-control-plane-blueprint.md)

## 1. Источники

Официальные источники, использованные для выводов:

* [Gemini API keys](https://ai.google.dev/gemini-api/docs/api-key), дата доступа: 2026-06-11.
* [Gemini API OAuth quickstart](https://ai.google.dev/gemini-api/docs/oauth), дата доступа: 2026-06-11.
* [Google Gen AI SDK for Gemini Enterprise Agent Platform](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/sdks/overview), дата доступа: 2026-06-11.
* [Gemini API image generation / Nano Banana](https://ai.google.dev/gemini-api/docs/image-generation), дата доступа: 2026-06-11.
* [Generate images using Imagen, Gemini API](https://ai.google.dev/gemini-api/docs/imagen), дата доступа: 2026-06-11.
* [Gemini Developer API pricing](https://ai.google.dev/gemini-api/docs/pricing), дата доступа: 2026-06-11.
* [Gemini API rate limits](https://ai.google.dev/gemini-api/docs/rate-limits), дата доступа: 2026-06-11.
* [Gemini API Additional Terms of Service](https://ai.google.dev/gemini-api/terms), дата доступа: 2026-06-11.
* [Gemini API abuse monitoring](https://ai.google.dev/gemini-api/docs/usage-policies), дата доступа: 2026-06-11.
* [Zero data retention in Gemini Developer API](https://ai.google.dev/gemini-api/docs/zdr), дата доступа: 2026-06-11.
* [Generate images with Imagen on Vertex AI](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/image/generate-images), дата доступа: 2026-06-11.
* [Agent Platform / generative AI pricing](https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing), дата доступа: 2026-06-11.

## 2. Authentication Findings

Gemini Developer API:

* Gemini API requests require authentication through API keys.
* Google distinguishes standard API keys and authorization keys.
* New API keys created in Google AI Studio are auth keys.
* Auth keys are bound to a Google Cloud service account and are restricted to the Gemini API by default.
* Google says unrestricted standard API keys will be rejected by Gemini API starting 2026-06-19.
* Google says standard API keys will be rejected by Gemini API in September 2026.
* API key/auth key values should be stored in environment variables such as `GEMINI_API_KEY` or `GOOGLE_API_KEY`.
* OAuth is available for stricter access controls, but Google's OAuth quickstart explicitly frames its simplified flow as suitable for testing and points production users to broader Google authentication guidance.

Vertex AI / Gemini Enterprise Agent Platform:

* Uses Google Cloud project, billing, Vertex AI API, IAM, Application Default Credentials for local development, and service-account/IAM style production control.
* Google Gen AI SDK provides a unified interface across Gemini Developer API and Gemini API on Gemini Enterprise Agent Platform, with migration possible without rewriting most application code.
* Vertex / Agent Platform path is stronger for production governance: IAM, service accounts, regions, Google Cloud audit/cost controls, quotas and enterprise controls.

Recommendation:

* v1: backend-only Gemini Developer API paid tier with auth key, stored only in backend env/secret manager.
* Production upgrade path: keep provider adapter compatible with Google Gen AI SDK so Vertex / Agent Platform can replace Developer API later.
* Avoid OAuth for v1 unless user-delegated access is required. Asset generation is server-side product infrastructure, not per-user Google data access.

## 3. Developer API vs Vertex / Agent Platform

| Dimension | Gemini Developer API | Vertex AI / Gemini Enterprise Agent Platform |
| --- | --- | --- |
| Best fit | Small v1, quick integration, agent tooling prototype | Production/enterprise, IAM, audit, region and quota governance |
| Credentials | API/auth key; OAuth possible | ADC locally; service account/IAM in production |
| Billing/quota | Google AI Studio / Gemini API project tiers | Google Cloud billing, quotas, IAM and platform controls |
| SDK | Google Gen AI SDK | Same SDK path with enterprise/vertex settings |
| Operational control | Simpler, less enterprise governance | Better for enterprise control and auditability |
| Recommendation | Start here, paid only | Planned migration target |

## 4. Image Provider Findings

Gemini native image generation / Nano Banana:

* Nano Banana is Gemini's native image generation capability.
* The docs list Gemini image models including `gemini-3.1-flash-image`, `gemini-3-pro-image`, and `gemini-2.5-flash-image`.
* Gemini 3 image models support 1K, 2K and 4K output; Gemini 3.1 Flash Image also adds 0.5K output.
* Gemini 3 image models are positioned for image generation and editing workflows.
* Gemini 3.1 Flash Image is optimized for speed/high-volume use cases.
* Gemini 3 Pro Image is positioned for professional asset production and better handling of complex instructions.
* Gemini image models support reference-image workflows; docs mention up to 14 reference images for Gemini 3 image workflows with model-specific limits.
* All generated images include SynthID watermark according to the Gemini image generation docs.

Imagen:

* Imagen is positioned as high-fidelity image generation for realistic and high-quality images from text prompts.
* Gemini API Imagen docs list Imagen 4 models: `imagen-4.0-generate-001`, `imagen-4.0-ultra-generate-001`, `imagen-4.0-fast-generate-001`.
* Imagen can return 1 to 4 output images.
* Gemini API Imagen docs say Imagen prompts are English-only at this time.
* Imagen supports aspect ratios `1:1`, `3:4`, `4:3`, `9:16`, `16:9`.
* Imagen 4 pricing in Gemini Developer API paid tier is listed per image: Fast $0.02, Standard $0.04, Ultra $0.06 as of access date.
* All Imagen-generated images include SynthID watermark according to Gemini API Imagen docs.

Vertex Imagen note:

* Vertex AI Imagen docs on 2026-06-11 show a deprecation/migration caution for several Imagen endpoints and recommend migration before 2026-06-30.
* This means implementation must verify the exact Vertex model endpoint at build time.
* For a new v1, do not hardcode Vertex Imagen endpoint assumptions in docs or code; route through provider registry and provider capability checks.

## 5. Suggested Provider Fit by Asset Kind

| Asset kind | Preferred v1 provider | Reason |
| --- | --- | --- |
| Food photos | Imagen 4 Standard/Ultra or Gemini 3 Pro Image | Realistic food quality matters. Imagen is strong for photorealistic prompts; Gemini Pro Image can be better for contextual edits. |
| Hero human/chef visual | Gemini 3 Pro Image or Imagen with people gate | Needs safety review; no auto-publish. |
| Hero product-like composition | Gemini 3 Pro Image | More contextual instructions and reference-image workflows. |
| Decorative food PNG/WebP | Gemini 3.1 Flash Image | Speed/cost, simple decorative assets, iterations. |
| Background kitchen image | Imagen 4 Standard or Gemini 3.1 Flash Image | Use only if output is low-risk and no real brand/person appears. |
| Audience photos | Imagen 4 Standard with people disabled or adult-only | Requires people policy and manual approval. |
| Product UI mockups | Prefer composed UI in code, not generated raster | Generated text/UI can drift; use real UI components or screenshots. |
| Document previews | Prefer real generated document preview from app | Avoid hallucinated document structure. |
| Avatars/placeholders | Generated only if clearly synthetic/placeholder | Must not imply real testimonial identity. |

## 6. Pricing / Rate Limits

Gemini Developer API:

* Pricing page separates free and paid tiers and marks whether data is used to improve products.
* Paid tier entries show `Used to improve our products: No`; free tier entries show `Yes`.
* Gemini 3 Pro Image is paid-only in the pricing table; image output is priced by image tokens, with listed equivalents per 1K/2K and 4K image.
* Imagen 4 is paid-only in pricing table, priced per image.

Rate limits:

* Gemini API rate limits are project-level, not per API key.
* Limits are measured across RPM, TPM, RPD and, for image-capable models, IPM.
* Rate limits vary by model and usage tier.
* Active rate limits should be checked in AI Studio at implementation time.

Guardrail:

* Do not put free-tier image generation into the production path.
* Implement per-provider and per-project daily spend/candidate caps before enabling users to generate assets repeatedly.

## 7. Terms / Rights / Data Use

Google AI Developer terms state, as of the accessed page:

* Google does not claim ownership over generated content.
* Google may generate same or similar content for others.
* The user/developer is responsible for use of generated content.
* Attribution may be required by applicable law or API Terms depending on use.
* For unpaid services, submitted content and generated responses can be used to improve Google products and may be reviewed by humans; sensitive/confidential/personal information should not be submitted to unpaid services.
* For paid services, Google states prompts/responses are not used to improve products, but abuse monitoring and operational logs can still exist under the terms/policies.

Implications for this project:

* Use paid tier for any real brand/product prompts.
* Store provider/model/prompt hash/time/user approval in provenance.
* Keep manual approval before publication.
* Do not generate logos, known brands, famous characters, or living-person likenesses without explicit rights and a high-risk gate.

## 8. Storage / CDN / Post-Processing

Recommended storage model:

* Candidate assets: object storage under non-public or signed-preview prefix.
* Approved assets: object storage under stable path with immutable versioned filename.
* Published assets: CDN/public URL, registered in Asset Registry.
* Metadata: database table or Git-backed JSON for v1; DB preferred once approvals become multi-user.
* Rejected candidates: retain for a limited period, then delete according to retention policy.

Formats:

* Store original provider output.
* Derive WebP for web delivery.
* Use JPEG for photographic assets where transparency is not needed.
* Use PNG/WebP for transparent or decorative assets.
* Generate responsive sizes for hero/background/content images.

Mandatory metadata:

* checksum/hash;
* width/height;
* source prompt hash;
* provider/model;
* SynthID expected flag;
* approval status;
* rights status;
* storage path and CDN URL.

