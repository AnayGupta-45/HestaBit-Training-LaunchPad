import express from 'express';
import {
  createUser,
  getUsers,
  getUserById,
} from '../controllers/user.controller.js';
import { validate } from '../middlewares/validate.js';
import { createUserSchema } from '../validators/user.schema.js';

const router = express.Router();

router.get('/', getUsers);
router.get('/:id', getUserById);
router.post('/', validate(createUserSchema), createUser);

export default router;
