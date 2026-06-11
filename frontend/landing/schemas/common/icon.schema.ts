import { z } from "zod";
import { iconKeys } from "@/landing/registries/icon.registry";

export const iconKeySchema = z.enum(iconKeys);
