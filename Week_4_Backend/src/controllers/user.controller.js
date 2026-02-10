import userService from '../services/user.service.js';

export const createUser = async (req, res, next) => {
  try {
    const user = await userService.createUser(
      req.body,
      req.headers['x-request-id']
    );

    res.status(201).json({
      success: true,
      data: user,
    });
  } catch (err) {
    next(err);
  }
};

export const getUsers = async (req, res, next) => {
  try {
    const users = await userService.getUsers();

    res.json({
      success: true,
      data: users,
    });
  } catch (err) {
    next(err);
  }
};

export const getUserById = async (req, res, next) => {
  try {
    const user = await userService.getUserById(req.params.id);

    res.json({
      success: true,
      data: user,
    });
  } catch (err) {
    next(err);
  }
};
