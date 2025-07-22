"""
MySQL数据库客户端
"""

import mysql.connector
from mysql.connector import Error
from typing import List, Dict, Any, Optional
import yaml
from pathlib import Path
from loguru import logger
import json
from datetime import datetime


class MySQLClient:
    """MySQL数据库客户端"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """初始化MySQL客户端"""
        self.config = self._load_config(config_path)
        self.connection = None
        self.connect()
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_path}")
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        return config['database']['mysql']
    
    def connect(self) -> None:
        """连接到MySQL数据库"""
        try:
            self.connection = mysql.connector.connect(
                host=self.config['host'],
                port=self.config['port'],
                database=self.config['database'],
                user=self.config['username'],
                password=self.config['password'],
                charset='utf8mb4',
                collation='utf8mb4_unicode_ci'
            )
            
            if self.connection.is_connected():
                logger.info("成功连接到MySQL数据库")
                self._create_tables()
            
        except Error as e:
            logger.error(f"连接MySQL数据库失败: {e}")
            raise
    
    def close(self) -> None:
        """关闭数据库连接"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("MySQL数据库连接已关闭")
    
    def _create_tables(self) -> None:
        """创建数据表"""
        tables = {
            'raw_products': """
                CREATE TABLE IF NOT EXISTS raw_products (
                    id VARCHAR(255) PRIMARY KEY,
                    name VARCHAR(500) NOT NULL,
                    brand VARCHAR(255),
                    category VARCHAR(100),
                    price DECIMAL(10,2),
                    currency VARCHAR(10) DEFAULT 'CNY',
                    description TEXT,
                    ingredients JSON,
                    effects JSON,
                    image_urls JSON,
                    rating DECIMAL(3,2),
                    review_count INT,
                    source VARCHAR(100),
                    crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    raw_data JSON,
                    INDEX idx_brand (brand),
                    INDEX idx_category (category),
                    INDEX idx_price (price),
                    INDEX idx_rating (rating)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """,
            
            'raw_brands': """
                CREATE TABLE IF NOT EXISTS raw_brands (
                    id VARCHAR(255) PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    name_en VARCHAR(255),
                    country VARCHAR(100),
                    founded_year INT,
                    description TEXT,
                    website VARCHAR(500),
                    logo_url VARCHAR(500),
                    price_range VARCHAR(50),
                    target_audience JSON,
                    source VARCHAR(100),
                    crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    raw_data JSON,
                    INDEX idx_name (name),
                    INDEX idx_country (country)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """,
            
            'raw_reviews': """
                CREATE TABLE IF NOT EXISTS raw_reviews (
                    id VARCHAR(255) PRIMARY KEY,
                    product_id VARCHAR(255),
                    user_id VARCHAR(255),
                    rating DECIMAL(3,2),
                    content TEXT,
                    sentiment_score DECIMAL(3,2),
                    helpful_count INT DEFAULT 0,
                    source VARCHAR(100),
                    created_at TIMESTAMP,
                    crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    raw_data JSON,
                    INDEX idx_product_id (product_id),
                    INDEX idx_rating (rating),
                    INDEX idx_created_at (created_at)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """,
            
            'crawl_logs': """
                CREATE TABLE IF NOT EXISTS crawl_logs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    source VARCHAR(100) NOT NULL,
                    data_type VARCHAR(50) NOT NULL,
                    status VARCHAR(20) NOT NULL,
                    items_count INT DEFAULT 0,
                    error_message TEXT,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_source (source),
                    INDEX idx_status (status),
                    INDEX idx_completed_at (completed_at)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """,
            
            'processed_data': """
                CREATE TABLE IF NOT EXISTS processed_data (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    data_type VARCHAR(50) NOT NULL,
                    source_id VARCHAR(255) NOT NULL,
                    processed_data JSON,
                    entities JSON,
                    relationships JSON,
                    status VARCHAR(20) DEFAULT 'pending',
                    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_data_type (data_type),
                    INDEX idx_source_id (source_id),
                    INDEX idx_status (status)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """
        }
        
        cursor = self.connection.cursor()
        
        for table_name, create_sql in tables.items():
            try:
                cursor.execute(create_sql)
                logger.info(f"创建表: {table_name}")
            except Error as e:
                logger.error(f"创建表 {table_name} 失败: {e}")
        
        cursor.close()
        self.connection.commit()
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """执行查询"""
        if not self.connection or not self.connection.is_connected():
            self.connect()
        
        cursor = self.connection.cursor(dictionary=True)
        
        try:
            cursor.execute(query, params or ())
            results = cursor.fetchall()
            return results
        except Error as e:
            logger.error(f"执行查询失败: {query}, 错误: {e}")
            raise
        finally:
            cursor.close()
    
    def execute_insert(self, query: str, params: tuple = None) -> int:
        """执行插入操作"""
        if not self.connection or not self.connection.is_connected():
            self.connect()
        
        cursor = self.connection.cursor()
        
        try:
            cursor.execute(query, params or ())
            self.connection.commit()
            return cursor.lastrowid
        except Error as e:
            logger.error(f"执行插入失败: {query}, 错误: {e}")
            self.connection.rollback()
            raise
        finally:
            cursor.close()
    
    def execute_batch_insert(self, query: str, data: List[tuple]) -> int:
        """批量插入数据"""
        if not self.connection or not self.connection.is_connected():
            self.connect()
        
        cursor = self.connection.cursor()
        
        try:
            cursor.executemany(query, data)
            self.connection.commit()
            return cursor.rowcount
        except Error as e:
            logger.error(f"批量插入失败: {query}, 错误: {e}")
            self.connection.rollback()
            raise
        finally:
            cursor.close()
    
    def save_raw_product(self, product_data: Dict[str, Any]) -> bool:
        """保存原始产品数据"""
        query = """
        INSERT INTO raw_products 
        (id, name, brand, category, price, currency, description, 
         ingredients, effects, image_urls, rating, review_count, source, raw_data)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        name = VALUES(name),
        brand = VALUES(brand),
        category = VALUES(category),
        price = VALUES(price),
        description = VALUES(description),
        ingredients = VALUES(ingredients),
        effects = VALUES(effects),
        image_urls = VALUES(image_urls),
        rating = VALUES(rating),
        review_count = VALUES(review_count),
        raw_data = VALUES(raw_data)
        """
        
        try:
            params = (
                product_data.get('id'),
                product_data.get('name'),
                product_data.get('brand'),
                product_data.get('category'),
                product_data.get('price'),
                product_data.get('currency', 'CNY'),
                product_data.get('description'),
                json.dumps(product_data.get('ingredients', []), ensure_ascii=False),
                json.dumps(product_data.get('effects', []), ensure_ascii=False),
                json.dumps(product_data.get('image_urls', []), ensure_ascii=False),
                product_data.get('rating'),
                product_data.get('review_count'),
                product_data.get('source'),
                json.dumps(product_data, ensure_ascii=False)
            )
            
            self.execute_insert(query, params)
            return True
            
        except Exception as e:
            logger.error(f"保存产品数据失败: {e}")
            return False
    
    def save_raw_brand(self, brand_data: Dict[str, Any]) -> bool:
        """保存原始品牌数据"""
        query = """
        INSERT INTO raw_brands 
        (id, name, name_en, country, founded_year, description, 
         website, logo_url, price_range, target_audience, source, raw_data)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        name = VALUES(name),
        name_en = VALUES(name_en),
        country = VALUES(country),
        founded_year = VALUES(founded_year),
        description = VALUES(description),
        website = VALUES(website),
        logo_url = VALUES(logo_url),
        price_range = VALUES(price_range),
        target_audience = VALUES(target_audience),
        raw_data = VALUES(raw_data)
        """
        
        try:
            params = (
                brand_data.get('id'),
                brand_data.get('name'),
                brand_data.get('name_en'),
                brand_data.get('country'),
                brand_data.get('founded_year'),
                brand_data.get('description'),
                brand_data.get('website'),
                brand_data.get('logo_url'),
                brand_data.get('price_range'),
                json.dumps(brand_data.get('target_audience', []), ensure_ascii=False),
                brand_data.get('source'),
                json.dumps(brand_data, ensure_ascii=False)
            )
            
            self.execute_insert(query, params)
            return True
            
        except Exception as e:
            logger.error(f"保存品牌数据失败: {e}")
            return False
    
    def save_raw_review(self, review_data: Dict[str, Any]) -> bool:
        """保存原始评论数据"""
        query = """
        INSERT INTO raw_reviews 
        (id, product_id, user_id, rating, content, sentiment_score, 
         helpful_count, source, created_at, raw_data)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
        rating = VALUES(rating),
        content = VALUES(content),
        sentiment_score = VALUES(sentiment_score),
        helpful_count = VALUES(helpful_count),
        raw_data = VALUES(raw_data)
        """
        
        try:
            params = (
                review_data.get('id'),
                review_data.get('product_id'),
                review_data.get('user_id'),
                review_data.get('rating'),
                review_data.get('content'),
                review_data.get('sentiment_score'),
                review_data.get('helpful_count', 0),
                review_data.get('source'),
                review_data.get('created_at'),
                json.dumps(review_data, ensure_ascii=False)
            )
            
            self.execute_insert(query, params)
            return True
            
        except Exception as e:
            logger.error(f"保存评论数据失败: {e}")
            return False
    
    def get_products_by_source(self, source: str, limit: int = 100) -> List[Dict[str, Any]]:
        """根据数据源获取产品"""
        query = """
        SELECT * FROM raw_products 
        WHERE source = %s 
        ORDER BY crawled_at DESC 
        LIMIT %s
        """
        
        return self.execute_query(query, (source, limit))
    
    def get_brands_by_source(self, source: str, limit: int = 100) -> List[Dict[str, Any]]:
        """根据数据源获取品牌"""
        query = """
        SELECT * FROM raw_brands 
        WHERE source = %s 
        ORDER BY crawled_at DESC 
        LIMIT %s
        """
        
        return self.execute_query(query, (source, limit))
    
    def log_crawl_activity(self, source: str, data_type: str, status: str, 
                          items_count: int = 0, error_message: str = None) -> bool:
        """记录爬取活动日志"""
        query = """
        INSERT INTO crawl_logs 
        (source, data_type, status, items_count, error_message, started_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        
        try:
            params = (
                source,
                data_type,
                status,
                items_count,
                error_message,
                datetime.now()
            )
            
            self.execute_insert(query, params)
            return True
            
        except Exception as e:
            logger.error(f"记录爬取日志失败: {e}")
            return False
