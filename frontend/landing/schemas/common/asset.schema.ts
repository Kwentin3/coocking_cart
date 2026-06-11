import { z } from "zod";
import { assetKeys } from "@/landing/registries/asset.registry";

export const assetKeySchema = z.enum(assetKeys);
