import { z } from "zod";
import { actionIdSchema } from "./common/action.schema";
import { assetKeySchema } from "./common/asset.schema";
import { claimRefsSchema } from "./common/claim.schema";
import { iconKeySchema } from "./common/icon.schema";
import { limitedTextSchema } from "./common/richText.schema";

export const heroSchema = z.object({
  id: z.literal("landing.hero"),
  eyebrow: limitedTextSchema(40),
  title: limitedTextSchema(92),
  description: limitedTextSchema(260),
  primaryActionId: actionIdSchema,
  secondaryActionId: actionIdSchema,
  trustItems: z.array(
    z.object({
      id: z.string().min(1).max(48),
      iconKey: iconKeySchema,
      text: limitedTextSchema(72),
    }),
  ).min(2).max(4),
  visual: z.object({
    layoutKey: z.literal("hero.targetProduct.v1"),
    productUiAssetKey: assetKeySchema,
    dishAssetKey: assetKeySchema,
    metricTitle: limitedTextSchema(36),
    metricValue: limitedTextSchema(36),
    metricNote: limitedTextSchema(72),
    mockupStatus: limitedTextSchema(44),
  }),
  claimRefs: claimRefsSchema,
});

export type HeroContent = z.infer<typeof heroSchema>;
