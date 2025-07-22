# MySQL 数据库配置指南

## 概述

本项目已配置为使用MySQL作为主要的关系数据库，用于存储原始数据、处理结果和系统日志。MySQL替代了原来的MongoDB和PostgreSQL，提供了统一的数据存储解决方案。

## MySQL的优势

### 1. **广泛使用和成熟稳定**
- 全球最流行的开源关系数据库
- 经过20多年的发展，非常成熟稳定
- 大量的文档和社区支持

### 2. **性能优秀**
- 针对读操作进行了优化
- 支持多种存储引擎（InnoDB、MyISAM等）
- 优秀的查询优化器

### 3. **JSON支持**
- MySQL 5.7+原生支持JSON数据类型
- 可以存储和查询JSON文档
- 兼具关系数据库和文档数据库的优势

### 4. **易于管理**
- 丰富的管理工具（MySQL Workbench、phpMyAdmin等）
- 简单的备份和恢复
- 完善的权限管理系统

## 数据库结构

### 核心表结构

#### 1. raw_products（原始产品数据）
```sql
CREATE TABLE raw_products (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(500) NOT NULL,
    brand VARCHAR(255),
    category VARCHAR(100),
    price DECIMAL(10,2),
    currency VARCHAR(10) DEFAULT 'CNY',
    description TEXT,
    ingredients JSON,           -- 存储成分列表
    effects JSON,              -- 存储功效列表
    image_urls JSON,           -- 存储图片URL列表
    rating DECIMAL(3,2),
    review_count INT,
    source VARCHAR(100),       -- 数据来源
    crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    raw_data JSON             -- 完整的原始数据
);
```

#### 2. raw_brands（原始品牌数据）
```sql
CREATE TABLE raw_brands (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    name_en VARCHAR(255),
    country VARCHAR(100),
    founded_year INT,
    description TEXT,
    website VARCHAR(500),
    logo_url VARCHAR(500),
    price_range VARCHAR(50),
    target_audience JSON,      -- 目标用户群体
    source VARCHAR(100),
    crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    raw_data JSON
);
```

#### 3. raw_reviews（原始评论数据）
```sql
CREATE TABLE raw_reviews (
    id VARCHAR(255) PRIMARY KEY,
    product_id VARCHAR(255),
    user_id VARCHAR(255),
    rating DECIMAL(3,2),
    content TEXT,
    sentiment_score DECIMAL(3,2),  -- 情感分析分数
    helpful_count INT DEFAULT 0,
    source VARCHAR(100),
    created_at TIMESTAMP,
    crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    raw_data JSON
);
```

#### 4. crawl_logs（爬取日志）
```sql
CREATE TABLE crawl_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    source VARCHAR(100) NOT NULL,
    data_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    items_count INT DEFAULT 0,
    error_message TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 5. processed_data（处理后数据）
```sql
CREATE TABLE processed_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    data_type VARCHAR(50) NOT NULL,
    source_id VARCHAR(255) NOT NULL,
    processed_data JSON,       -- 处理后的结构化数据
    entities JSON,             -- 提取的实体
    relationships JSON,        -- 提取的关系
    status VARCHAR(20) DEFAULT 'pending',
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 配置说明

### 1. 配置文件（config/config.yaml）
```yaml
database:
  mysql:
    host: "localhost"
    port: 3306
    database: "cosmetic_data"
    username: "root"
    password: "password"
```

### 2. Docker配置（docker-compose.yml）
```yaml
mysql:
  image: mysql:8.0
  container_name: cosmetic_kg_mysql
  ports:
    - "3306:3306"
  environment:
    - MYSQL_ROOT_PASSWORD=password
    - MYSQL_DATABASE=cosmetic_data
    - MYSQL_USER=cosmetic_user
    - MYSQL_PASSWORD=password
  volumes:
    - mysql_data:/var/lib/mysql
  command: --default-authentication-plugin=mysql_native_password
```

## 使用方法

### 1. 启动MySQL服务

#### 使用Docker Compose（推荐）
```bash
# 启动MySQL服务
docker-compose up -d mysql

# 查看服务状态
docker-compose ps mysql

# 查看日志
docker-compose logs mysql
```

#### 使用启动脚本
```bash
# 自动启动所有服务（包括MySQL）
python scripts/start_services.py

# 仅启动数据库服务
python scripts/start_services.py --skip-init
```

### 2. 连接数据库

#### 使用MySQL客户端
```bash
# 连接到容器中的MySQL
docker-compose exec mysql mysql -u root -p

# 或者从主机连接
mysql -h localhost -P 3306 -u root -p
```

#### 使用Python代码
```python
from src.database.mysql_client import MySQLClient

# 创建客户端
client = MySQLClient()

# 保存产品数据
product_data = {
    'id': 'product_001',
    'name': 'SK-II 神仙水',
    'brand': 'SK-II',
    'category': 'skincare',
    'price': 1299.0,
    'ingredients': ['Pitera', '透明质酸'],
    'effects': ['保湿', '提亮'],
    'source': 'sephora'
}

client.save_raw_product(product_data)

# 查询数据
products = client.get_products_by_source('sephora', limit=10)
```

### 3. 数据查询示例

#### 基本查询
```sql
-- 查询所有SK-II产品
SELECT * FROM raw_products WHERE brand = 'SK-II';

-- 查询价格在500-1000元的护肤品
SELECT * FROM raw_products 
WHERE category = 'skincare' 
AND price BETWEEN 500 AND 1000;

-- 查询评分最高的10个产品
SELECT * FROM raw_products 
ORDER BY rating DESC 
LIMIT 10;
```

#### JSON字段查询
```sql
-- 查询包含透明质酸的产品
SELECT * FROM raw_products 
WHERE JSON_CONTAINS(ingredients, '"透明质酸"');

-- 查询具有保湿功效的产品
SELECT * FROM raw_products 
WHERE JSON_CONTAINS(effects, '"保湿"');

-- 提取JSON字段中的特定值
SELECT name, JSON_EXTRACT(ingredients, '$[0]') as first_ingredient 
FROM raw_products;
```

#### 聚合查询
```sql
-- 按品牌统计产品数量
SELECT brand, COUNT(*) as product_count 
FROM raw_products 
GROUP BY brand 
ORDER BY product_count DESC;

-- 按类别统计平均价格
SELECT category, AVG(price) as avg_price 
FROM raw_products 
GROUP BY category;

-- 统计各数据源的爬取情况
SELECT source, COUNT(*) as total_items, 
       MAX(crawled_at) as last_crawl 
FROM raw_products 
GROUP BY source;
```

## 数据迁移

### 从MongoDB迁移到MySQL

如果您之前使用的是MongoDB，可以使用以下脚本进行数据迁移：

```python
# 迁移脚本示例
import json
from pymongo import MongoClient
from src.database.mysql_client import MySQLClient

def migrate_from_mongodb():
    # 连接MongoDB
    mongo_client = MongoClient('mongodb://localhost:27017/')
    mongo_db = mongo_client['cosmetic_data']
    
    # 连接MySQL
    mysql_client = MySQLClient()
    
    # 迁移产品数据
    products = mongo_db.products.find()
    for product in products:
        # 转换数据格式
        product_data = {
            'id': str(product['_id']),
            'name': product.get('name'),
            'brand': product.get('brand'),
            'category': product.get('category'),
            'price': product.get('price'),
            'ingredients': product.get('ingredients', []),
            'effects': product.get('effects', []),
            'source': product.get('source', 'mongodb')
        }
        
        mysql_client.save_raw_product(product_data)
    
    print("数据迁移完成")

if __name__ == "__main__":
    migrate_from_mongodb()
```

## 性能优化

### 1. 索引优化
```sql
-- 为常用查询字段创建索引
CREATE INDEX idx_brand_category ON raw_products(brand, category);
CREATE INDEX idx_price_rating ON raw_products(price, rating);
CREATE INDEX idx_crawled_at ON raw_products(crawled_at);

-- 为JSON字段创建虚拟列和索引
ALTER TABLE raw_products 
ADD COLUMN first_ingredient VARCHAR(255) 
GENERATED ALWAYS AS (JSON_UNQUOTE(JSON_EXTRACT(ingredients, '$[0]'))) STORED;

CREATE INDEX idx_first_ingredient ON raw_products(first_ingredient);
```

### 2. 查询优化
```sql
-- 使用EXPLAIN分析查询性能
EXPLAIN SELECT * FROM raw_products WHERE brand = 'SK-II';

-- 优化JSON查询
SELECT * FROM raw_products 
WHERE first_ingredient = '透明质酸'  -- 使用虚拟列而不是JSON_EXTRACT
```

### 3. 配置优化
```ini
# MySQL配置文件 my.cnf
[mysqld]
innodb_buffer_pool_size = 1G
innodb_log_file_size = 256M
max_connections = 200
query_cache_size = 64M
tmp_table_size = 64M
max_heap_table_size = 64M
```

## 备份和恢复

### 1. 数据备份
```bash
# 备份整个数据库
docker-compose exec mysql mysqldump -u root -p cosmetic_data > backup.sql

# 备份特定表
docker-compose exec mysql mysqldump -u root -p cosmetic_data raw_products > products_backup.sql

# 定时备份脚本
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec mysql mysqldump -u root -ppassword cosmetic_data > backup_$DATE.sql
```

### 2. 数据恢复
```bash
# 恢复数据库
docker-compose exec -T mysql mysql -u root -p cosmetic_data < backup.sql

# 恢复特定表
docker-compose exec -T mysql mysql -u root -p cosmetic_data < products_backup.sql
```

## 监控和维护

### 1. 性能监控
```sql
-- 查看慢查询
SHOW VARIABLES LIKE 'slow_query_log';
SHOW VARIABLES LIKE 'long_query_time';

-- 查看连接状态
SHOW PROCESSLIST;

-- 查看表状态
SHOW TABLE STATUS;
```

### 2. 日常维护
```sql
-- 优化表
OPTIMIZE TABLE raw_products;

-- 分析表
ANALYZE TABLE raw_products;

-- 检查表
CHECK TABLE raw_products;

-- 修复表
REPAIR TABLE raw_products;
```

## 常见问题

### Q: 如何处理中文字符？
A: 确保使用utf8mb4字符集和utf8mb4_unicode_ci排序规则。

### Q: JSON字段查询性能如何优化？
A: 为常用的JSON路径创建虚拟列和索引。

### Q: 如何处理大量数据？
A: 使用分区表、读写分离、定期归档等策略。

### Q: 连接数过多怎么办？
A: 使用连接池、优化查询、增加max_connections配置。

## 总结

MySQL作为项目的主数据库，提供了：
- 可靠的数据存储
- 优秀的查询性能
- 丰富的JSON支持
- 完善的管理工具
- 广泛的社区支持

通过合理的表设计和索引优化，MySQL完全可以满足化妆品知识图谱项目的数据存储需求。
