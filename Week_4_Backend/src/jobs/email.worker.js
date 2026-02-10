import { Worker } from 'bullmq';
import { redisConnection } from './redis.js';
import logger from '../utils/logger.js';

logger.info('Starting Email Worker');

const worker = new Worker(
  'email-queue',
  async (job) => {
    logger.info(
      {
        jobId: job.id,
        jobName: job.name,
        data: job.data,
      },
      'Processing email job'
    );

    await new Promise((resolve) => setTimeout(resolve, 2000));

    logger.info(
      {
        jobId: job.id,
        email: job.data.email,
      },
      'Email sent successfully'
    );
  },
  {
    connection: redisConnection,
  }
);

worker.on('completed', (job) => {
  logger.info({ jobId: job.id }, 'Job completed');
});

worker.on('failed', (job, err) => {
  logger.error(
    {
      jobId: job?.id,
      err,
    },
    'Job failed'
  );
});

worker.on('error', (err) => {
  logger.error({ err }, 'Worker error');
});

process.on('SIGINT', async () => {
  logger.info('Shutting down worker...');
  await worker.close();
  logger.info('Worker closed');
  process.exit(0);
});

process.on('SIGTERM', async () => {
  logger.info('Shutting down worker...');
  await worker.close();
  logger.info('Worker closed');
  process.exit(0);
});
