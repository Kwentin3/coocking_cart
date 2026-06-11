import { z } from "zod";
import { claimRefsSchema } from "./common/claim.schema";
import { limitedTextSchema } from "./common/richText.schema";

export const seoSchema = z.object({
  id: z.literal("landing.seo"),
  title: limitedTextSchema(70),
  description: limitedTextSchema(160),
  claimRefs: claimRefsSchema,
});

export type SeoContent = z.infer<typeof seoSchema>;
