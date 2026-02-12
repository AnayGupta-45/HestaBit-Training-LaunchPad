import productRoutes from './product.routes.js';
import userRoutes from '../routes/user.routes.js';
import orderRoutes from '../routes/order.routes.js';
import accountRoutes from '../routes/account.routes.js';

export default function mountRoutes(app) {
  app.use('/users', userRoutes);
  app.use('/products', productRoutes);
  app.use('/accounts', accountRoutes);
  app.use('/order', orderRoutes);
}
