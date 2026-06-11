import { z } from "zod";
import { claimRefsSchema } from "./common/claim.schema";
import { iconKeySchema } from "./common/icon.schema";
import { limitedTextSchema } from "./common/richText.schema";

export const workflowSchema = z.object({
  id: z.literal("landing.workflow"),
  title: limitedTextSchema(72),
  description: limitedTextSchema(220),
  steps: z.array(
    z.object({
      id: z.string().min(1).max(48),
      title: limitedTextSchema(54),
      description: limitedTextSchema(180),
      iconKey: iconKeySchema,
      claimRefs: claimRefsSchema,
    }),
  ).min(3).max(5),
});

export type WorkflowContent = z.infer<typeof workflowSchema>;
