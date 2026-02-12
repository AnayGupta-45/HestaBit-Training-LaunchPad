import Account from '../models/Account.js';

class AccountRepository {
  create(data) {
    return Account.create(data);
  }

  findByEmail(email) {
    return Account.findOne({ email });
  }

  async findPaginatedWithCount({ status }, { limit = 10, cursor }) {
    // CURSOR PAGINATION
    const query = {};
    if (status) query.status = status;

    if (cursor) {
      query.createdAt = { $lt: new Date(cursor) };
    }

    const [items, total] = await Promise.all([
      Account.find(query).sort({ createdAt: -1 }).limit(limit),
      Account.countDocuments(status ? { status } : {}),
    ]);

    return { items, total };
  }
}

export default new AccountRepository();
