import { z } from "zod";
import { actionIdSchema } from "./common/action.schema";
import { assetKeySchema } from "./common/asset.schema";
import { claimRefsSchema } from "./common/claim.schema";
import { iconKeySchema } from "./common/icon.schema";
import { limitedTextSchema } from "./common/richText.schema";

export const documentsSchema = z.object({
  id: z.literal("landing.documents"),
  title: limitedTextSchema(72),
  description: limitedTextSchema(240),
  previewAssetKeys: z.array(assetKeySchema).min(1).max(3),
  documentTypes: z.array(
    z.object({
      id: z.string().min(1).max(48),
      title: limitedTextSchema(56),
      description: limitedTextSchema(160),
      iconKey: iconKeySchema,
      claimRefs: claimRefsSchema,
    }),
  ).min(3).max(6),
  sampleActionId: actionIdSchema,
  exportActionId: actionIdSchema,
  disclaimer: limitedTextSchema(220),
  claimRefs: claimRefsSchema,
});

export type DocumentsContent = z.infer<typeof documentsSchema>;
