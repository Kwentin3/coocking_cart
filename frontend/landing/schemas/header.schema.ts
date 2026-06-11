import { z } from "zod";
import { actionIdSchema } from "./common/action.schema";
import { assetKeySchema } from "./common/asset.schema";
import { limitedTextSchema } from "./common/richText.schema";

export const headerSchema = z.object({
  id: z.literal("landing.header"),
  logoText: limitedTextSchema(32),
  logoAssetKey: assetKeySchema,
  navItems: z.array(
    z.object({
      id: z.string().min(1).max(48),
      label: limitedTextSchema(28),
      href: z.string().startsWith("#"),
    }),
  ).min(3).max(6),
  primaryActionId: actionIdSchema,
  loginActionId: actionIdSchema.optional(),
});

export type HeaderContent = z.infer<typeof headerSchema>;
