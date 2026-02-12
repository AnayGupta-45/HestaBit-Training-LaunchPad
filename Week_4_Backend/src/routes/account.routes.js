import express from 'express';
import {
  createAccount,
  getAccounts,
} from '../controllers/account.controller.js';
import { validate } from '../middlewares/validate.js';
import { createAccountSchema } from '../validators/account.schema.js';

const router = express.Router();

router.get('/', getAccounts);
router.post('/', validate(createAccountSchema), createAccount);

export default router;
