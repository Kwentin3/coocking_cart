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
  claimRefs: claimRefsSchema,
});

export type FinalCtaContent = z.infer<typeof finalCtaSchema>;
