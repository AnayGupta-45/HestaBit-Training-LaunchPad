import pino from 'pino';
import path from 'path';
import fs from 'fs';

const logDir = path.join(process.cwd(), 'logs');

if (!fs.existsSync(logDir)) {
  fs.mkdirSync(logDir, { recursive: true });
}

const appStream = fs.createWriteStream(path.join(logDir, 'app.log'), {
  flags: 'a',
});

const errorStream = fs.createWriteStream(path.join(logDir, 'error.log'), {
  flags: 'a',
});

const streams = [
  { level: 'info', stream: appStream },
  { level: 'error', stream: errorStream },
  { level: 'info', stream: process.stdout },
  { level: 'error', stream: process.stderr },
];

const logger = pino(
  {
    level: process.env.LOG_LEVEL || 'info',
    timestamp: pino.stdTimeFunctions.isoTime,
  },
  pino.multistream(streams)
);

export default logger;
