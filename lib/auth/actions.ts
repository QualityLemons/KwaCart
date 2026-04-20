// lib/auth/actions.ts
"use server";

import { hash } from "bcryptjs"; // or 'argon2'
import { prisma } from "@/lib/prisma"; // your prisma client instance
import { RegisterSchema } from "./schema";

export async function registerUser(data: unknown) {
  // 1. Validate the input data
  const result = RegisterSchema.safeParse(data);
  
  if (!result.success) {
    return { error: "Invalid input fields." };
  }

  const { email, password } = result.data;

  try {
    // 2. Check if user already exists
    const existingUser = await prisma.user.findUnique({
      where: { email },
    });

    if (existingUser) {
      return { error: "User already exists with this email." };
    }

    // 3. Hash the password
    const hashedPassword = await hash(password, 12);

    // 4. Create the user in Prisma
    const user = await prisma.user.create({
      data: {
        email,
        passwordHash: hashedPassword,
      },
    });

    return { success: true, userId: user.id };

  } catch (error) {
    console.error("Registration Error:", error);
    return { error: "Something went wrong. Please try again." };
  }
}