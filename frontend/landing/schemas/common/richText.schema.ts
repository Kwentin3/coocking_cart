import { z } from "zod";

export const textBlockSchema = z.object({
  id: z.string().min(1).max(64),
  text: z.string().min(1).max(280),
});

export const limitedTextSchema = (max: number) => z.string().trim().min(1).max(max);
