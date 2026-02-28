import { z } from "zod";

export const loginSchema = z.object({
	email: z
		.email({
			error: "Invalid email address",
		})
		.trim(),
	password: z
		.string()
		.trim()
		.min(1, "Password is required")
		.min(6, "Password must be at least 6 characters"),
});

export type LoginFormData = z.infer<typeof loginSchema>;

export const registerSchema = z.object({
	username: z
		.string()
		.trim()
		.min(1, "Username is required")
		.min(3, "Username must be at least 3 characters"),
	email: z.email("Invalid email address"),
	password: z
		.string()
		.trim()
		.min(1, "Password is required")
		.min(6, "Password must be at least 6 characters"),
});

export type RegisterFormData = z.infer<typeof registerSchema>;
