import { z } from "zod";
import { claimRefsSchema } from "./common/claim.schema";
import { iconKeySchema } from "./common/icon.schema";
import { limitedTextSchema } from "./common/richText.schema";

export const benefitsSchema = z.object({
  id: z.literal("landing.benefits"),
  title: limitedTextSchema(72),
  description: limitedTextSchema(220),
  items: z.array(
    z.object({
      id: z.string().min(1).max(48),
      title: limitedTextSchema(56),
      description: limitedTextSchema(190),
      iconKey: iconKeySchema,
      claimRefs: claimRefsSchema,
    }),
  ).min(3).max(6),
});

export type BenefitsContent = z.infer<typeof benefitsSchema>;
