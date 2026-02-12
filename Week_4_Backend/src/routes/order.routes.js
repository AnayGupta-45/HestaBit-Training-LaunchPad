import express from 'express';
import {
  createOrder,
  getOrders,
  getOrderById,
  deleteOrder,
} from '../controllers/order.controller.js';
import { validate } from '../middlewares/validate.js';
import { createOrderSchema } from '../validators/order.schema.js';

const router = express.Router();

router.get('/', getOrders);
router.get('/:id', getOrderById);
router.post('/', validate(createOrderSchema), createOrder);
router.delete('/:id', deleteOrder);

export default router;
