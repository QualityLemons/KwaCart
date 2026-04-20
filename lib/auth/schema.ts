// lib/auth/schema.ts
import { z } from "zod";

export const RegisterSchema = z.zodObject({
  email: z.string().email("Invalid email address"),
  password: z.string().min(8, "Password must be at least 8 characters"),
});

export type RegisterInput = z.infer<typeof RegisterSchema>;