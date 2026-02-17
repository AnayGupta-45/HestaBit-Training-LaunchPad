import productRepo from '../repositories/product.repository.js';
import AppError from '../utils/appError.js';

class ProductService {
  async createProduct(payload) {
    const { name, price } = payload;

    if (!name || price == null) {
      throw new AppError(
        'Product name and price are required',
        400,
        'VALIDATION_ERROR'
      );
    }

    return productRepo.create(payload);
  }

  async getProducts(queryParams) {
    const {
      page = 1,
      limit = 10,
      includeDeleted = false,
      search,
      minPrice,
      maxPrice,
      tags,
      sort,
    } = queryParams;

    const filters = {
      includeDeleted,
      search,
      minPrice,
      maxPrice,
      tags,
    };

    const options = {
      page: Number(page),
      limit: Number(limit),
      sort,
    };

    const { items, total } = await productRepo.findWithFilters(
      filters,
      options
    );

    return {
      items,
      meta: {
        total,
        page: options.page,
        limit: options.limit,
      },
    };
  }

  async deleteProduct(id) {
    const product = await productRepo.findById(id);

    if (!product) {
      throw new AppError('Product Not Found', 404, 'PRODUCT_NOT_FOUND');
    }
    if (product.deletedAt) {
      throw new AppError(
        'Product already deleted',
        400,
        'PRODUCT_ALREADY_DELETED'
      );
    }
    return productRepo.softDelete(id);
  }
}

export default new ProductService();
