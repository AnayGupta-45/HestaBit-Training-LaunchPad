import { Redis } from 'ioredis';

export const redisConnection = new Redis({
  host: '127.0.0.1',
  port: 6379,
  maxRetriesPerRequest: null,
  retryStrategy(times) {
    console.log(`Retrying Redis connection... attempt ${times}`);
    return Math.min(times * 300, 2000);
  },
  enableReadyCheck: true,
});

redisConnection.on('connect', () => {
  console.log('Redis connected');
});

redisConnection.on('ready', () => {
  console.log('Redis ready');
});

redisConnection.on('error', (err) => {
  console.error('Redis error:', err.message);
});
