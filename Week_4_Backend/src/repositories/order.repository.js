import Order from '../models/Order.js';

class OrderRepository {
  create(data) {
    return Order.create(data);
  }

  findById(id) {
    return Order.findOne({ _id: id, deletedAt: null }).populate('accountId');
  }

  //CURSOR PAGINATION
  findByCursor({ limit = 10, status, cursor }) {
    const query = { deletedAt: null };

    if (status) query.status = status;

    if (cursor) query.createdAt = { $lt: new Date(cursor) };

    return Order.find(query)
      .sort({ createdAt: -1 })
      .limit(limit)
      .populate('accountId');
  }

  countActive(filters = {}) {
    const query = { deletedAt: null, ...filters };
    return Order.countDocuments(query);
  }

  softDelete(id) {
    return Order.findByIdAndUpdate(
      id,
      { deletedAt: new Date() },
      { new: true }
    );
  }
}

export default new OrderRepository();
