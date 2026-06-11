import { z } from "zod";
import { limitedTextSchema } from "./common/richText.schema";

export const testimonialsSchema = z.object({
  id: z.literal("landing.testimonials"),
  mode: z.enum(["hidden", "internal-placeholder", "approved"]),
  title: limitedTextSchema(72),
  items: z.array(
    z.object({
      id: z.string().min(1).max(48),
      quote: limitedTextSchema(220),
      author: limitedTextSchema(72),
      role: limitedTextSchema(72),
      isReal: z.boolean(),
      approved: z.boolean(),
    }),
  ).max(4),
});

export type TestimonialsContent = z.infer<typeof testimonialsSchema>;
