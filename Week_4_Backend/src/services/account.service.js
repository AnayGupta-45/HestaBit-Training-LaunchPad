import accountRepo from '../repositories/account.repository.js';
import AppError from '../utils/appError.js';

class AccountService {
  async createAccount(payload) {
    const { firstName, lastName, email, password } = payload;

    if (!firstName || !lastName || !email || !password) {
      throw new AppError(
        'firstName, lastName, email, and password are required',
        400,
        'VALIDATION_ERROR'
      );
    }

    const existing = await accountRepo.findByEmail(email);
    if (existing) {
      throw new AppError('Email already registered', 409, 'ACCOUNT_EXISTS');
    }

    return accountRepo.create(payload);
  }

  async getAccounts(queryParams) {
    const { limit = 10, cursor, status } = queryParams;

    const { items, total } = await accountRepo.findPaginatedWithCount(
      { status },
      { limit: Number(limit), cursor }
    );

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
}

export default new AccountService();
