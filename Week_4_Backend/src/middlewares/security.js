import helmet from 'helmet';
import cors from 'cors';
import ratelimit from 'express-rate-limit';
import config from '../config/index.js';

export const apiRateLimiter = ratelimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100,
  standardHeaders: true,
  legacyHeaders: false,
});

export const securityHeaders = helmet();

export const corsPolicy = cors({
  origin: config.corsOrigin,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'],
});
