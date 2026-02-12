import { z } from 'zod';

export const createAccountSchema = z
  .object({
    firstName: z.string().min(1).max(50),
    lastName: z.string().min(1).max(50),
    email: z.string().email(),
    password: z.string().min(8).max(100),
    status: z.enum(['active', 'blocked']).optional(),
  })
  .strict();
