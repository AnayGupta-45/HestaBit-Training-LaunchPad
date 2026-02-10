import { Redis } from 'ioredis';
import logger from '../utils/logger.js';
import config from '../config/index.js';

export const redisConnection = new Redis({
  host: config.REDIS_HOST || '127.0.0.1',
  port: config.REDIS_PORT ? Number(config.REDIS_PORT) : 6379,
  maxRetriesPerRequest: null,
  retryStrategy(times) {
    const delay = Math.min(times * 300, 2000);

    logger.warn({ attempt: times, delay }, 'Retrying Redis connection');

    return delay;
  },
  enableReadyCheck: true,
});

redisConnection.on('connect', () => {
  logger.info('Redis TCP connection established');
});

redisConnection.on('ready', () => {
  logger.info('Redis connection ready');
});

redisConnection.on('reconnecting', (delay) => {
  logger.warn({ delay }, 'Redis reconnecting');
});

redisConnection.on('end', () => {
  logger.warn('Redis connection closed');
});

redisConnection.on('error', (err) => {
  logger.error({ err }, 'Redis connection error');
});
