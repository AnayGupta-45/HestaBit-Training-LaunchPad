import config from './config/index.js';
import logger from './utils/logger.js';
import appLoader from './loaders/app.js';
import { disconnectDB } from './loaders/db.js';

let server;

async function startServer() {
  try {
    logger.info('Bootstrapping application');

    const app = await appLoader();

    server = app.listen(config.port, () => {
      logger.info(`Server started on Port ${config.port}`);
    });

    server.on('error', (err) => {
      if (err.code === 'EADDRINUSE') {
        logger.error(
          { port: config.port },
          `Port ${config.port} is already in use`
        );
      } else {
        logger.error({ err }, 'Server startup error');
      }
      process.exit(1);
    });
  } catch (err) {
    logger.fatal({ err }, 'Failed to bootstrap application');
    process.exit(1);
  }
}

async function shutDown(signal) {
  logger.info({ signal }, 'Graceful Shutdown Started');

  try {
    if (server) {
      await new Promise((resolve) => server.close(resolve));
      logger.info('HTTP server closed');
    }

    await disconnectDB();
    logger.info('Database disconnected');

    logger.info('Process exiting');
    process.exit(0);
  } catch (err) {
    logger.error({ err }, 'Error during graceful shutdown');
    process.exit(1);
  }
}

process.on('SIGINT', shutDown);
process.on('SIGTERM', shutDown);

process.on('uncaughtException', (err) => {
  logger.fatal({ err }, 'Uncaught Exception');
  process.exit(1);
});

process.on('unhandledRejection', (reason) => {
  logger.fatal({ reason }, 'Unhandled Promise Rejection');
  process.exit(1);
});

startServer();
