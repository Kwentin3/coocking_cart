import { z } from "zod";
import { assetKeySchema } from "./common/asset.schema";
import { claimRefsSchema } from "./common/claim.schema";
import { iconKeySchema } from "./common/icon.schema";
import { limitedTextSchema } from "./common/richText.schema";

export const audienceSchema = z.object({
  id: z.literal("landing.audience"),
  title: limitedTextSchema(72),
  description: limitedTextSchema(220),
  items: z.array(
    z.object({
      id: z.string().min(1).max(48),
      title: limitedTextSchema(48),
      description: limitedTextSchema(180),
      imageAssetKey: assetKeySchema,
      iconKey: iconKeySchema,
      iconVariant: z.enum(["brand", "action"]),
      claimRefs: claimRefsSchema,
    }),
  ).min(3).max(5),
});

export type AudienceContent = z.infer<typeof audienceSchema>;
