import { z } from "zod";
import { actionIdSchema } from "./common/action.schema";
import { assetKeySchema } from "./common/asset.schema";
import { claimRefsSchema } from "./common/claim.schema";
import { limitedTextSchema } from "./common/richText.schema";

export const finalCtaSchema = z.object({
  id: z.literal("landing.finalCta"),
  title: limitedTextSchema(72),
  description: limitedTextSchema(240),
  primaryActionId: actionIdSchema,
  secondaryActionId: actionIdSchema,
  decorativeAssetKey: assetKeySchema,
  ownerGateTitle: limitedTextSchema(72),
  ownerGateItems: z.array(limitedTextSchema(120)).min(3).max(9),
  claimRefs: claimRefsSchema,
});

export type FinalCtaContent = z.infer<typeof finalCtaSchema>;
