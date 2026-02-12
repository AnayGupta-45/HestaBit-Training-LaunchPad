import orderRepo from '../repositories/order.repository.js';
import AppError from '../utils/appError.js';

class OrderService {
  async createOrder(payload) {
    const { accountId, items } = payload;

    if (!accountId || !items || items.length === 0) {
      throw new AppError(
        'accountId and at least one item are required',
        400,
        'VALIDATION_ERROR'
      );
    }

    const totalAmount = items.reduce(
      (sum, item) => sum + item.price * item.quantity,
      0
    );

    return orderRepo.create({ ...payload, totalAmount });
  }

  async getOrders(queryParams) {
    const { limit = 10, cursor, status } = queryParams;

    const items = await orderRepo.findByCursor({
      limit: Number(limit),
      cursor,
      status,
    });

    const total = await orderRepo.countActive(status ? { status } : {});

    const nextCursor =
      items.length === Number(limit)
        ? items[items.length - 1].createdAt.toISOString()
        : null;

    return {
      items,
      meta: {
        total,
        limit: Number(limit),
        nextCursor,
      },
    };
  }

  async getOrderById(id) {
    const order = await orderRepo.findById(id);
    if (!order) {
      throw new AppError('Order not found', 404, 'ORDER_NOT_FOUND');
    }
    return order;
  }

  async deleteOrder(id) {
    const order = await orderRepo.findById(id);
    if (!order) {
      throw new AppError('Order not found', 404, 'ORDER_NOT_FOUND');
    }
    if (order.deletedAt) {
      throw new AppError('Order already deleted', 400, 'ORDER_ALREADY_DELETED');
    }
    return orderRepo.softDelete(id);
  }
}

export default new OrderService();
