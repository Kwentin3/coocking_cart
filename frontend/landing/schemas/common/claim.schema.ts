import { z } from "zod";
import { claimRefs } from "@/landing/lib/claimMaturity";

export const claimRefSchema = z.enum(claimRefs);
export const claimRefsSchema = z.array(claimRefSchema).default([]);
