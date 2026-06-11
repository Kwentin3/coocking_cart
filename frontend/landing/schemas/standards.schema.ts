import { z } from "zod";
import { claimRefsSchema } from "./common/claim.schema";
import { iconKeySchema } from "./common/icon.schema";
import { limitedTextSchema } from "./common/richText.schema";

export const standardsSchema = z.object({
  id: z.literal("landing.standards"),
  title: limitedTextSchema(72),
  description: limitedTextSchema(260),
  items: z.array(
    z.object({
      id: z.string().min(1).max(48),
      text: limitedTextSchema(120),
      iconKey: iconKeySchema,
    }),
  ).min(2).max(5),
  disclaimer: limitedTextSchema(260),
  claimRefs: claimRefsSchema,
});

export type StandardsContent = z.infer<typeof standardsSchema>;
