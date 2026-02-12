import { z } from 'zod';

const orderItemSchema = z
  .object({
    productId: z.string().min(1),
    productName: z.string().min(1).max(100),
    price: z.number().nonnegative(),
    quantity: z.number().int().min(1),
  })
  .strict();

export const createOrderSchema = z
  .object({
    accountId: z.string().min(1),
    items: z.array(orderItemSchema).min(1),
  })
  .strict();
