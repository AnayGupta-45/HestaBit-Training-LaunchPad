import accountService from '../services/account.service.js';

export const createAccount = async (req, res, next) => {
  try {
    const account = await accountService.createAccount(req.body);
    res.status(201).json({ success: true, data: account });
  } catch (err) {
    next(err);
  }
};

export const getAccounts = async (req, res, next) => {
  try {
    const result = await accountService.getAccounts(req.query);
    res.json({ success: true, data: result });
  } catch (err) {
    next(err);
  }
};
