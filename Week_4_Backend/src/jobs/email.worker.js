import { Worker } from 'bullmq';
import { redisConnection } from './redis.js';

console.log('Starting Email Worker...');

const worker = new Worker(
  'email-queue',
  async (job) => {
    console.log('Processing Job:', job.name);
    console.log('Job Data:', job.data);

    await new Promise((resolve) => setTimeout(resolve, 2000));

    console.log(`Email sent to ${job.data.email}`);
  },
  {
    connection: redisConnection,
  }
);

worker.on('completed', (job) => {
  console.log(`Job ${job.id} completed`);
});

worker.on('failed', (job, err) => {
  console.error(`Job ${job?.id} failed:`, err);
});

worker.on('error', (err) => {
  console.error('Worker Error:', err);
});
