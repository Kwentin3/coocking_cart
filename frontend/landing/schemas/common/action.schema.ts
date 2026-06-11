import { z } from "zod";
import { actionIds } from "@/landing/registries/cta.registry";

export const actionIdSchema = z.enum(actionIds);
