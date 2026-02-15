import logger from '../utils/logger.js';

export default function errorMiddleware(err, req, res, next) {
  logger.error(
    {
      requestId: req.requestId,
      err,
      path: req.originalUrl,
      method: req.method,
    },
    err.message
  );

  res.status(err.statusCode || 500).json({
    success: false,
    message: err.message || 'Internal Server Error',
    code: err.code || 'INTERNAL_ERROR',
    timestamp: new Date().toISOString(),
    path: req.originalUrl,
  });
}
