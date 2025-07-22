"""
Neo4j图数据库客户端
"""

from typing import List, Dict, Any, Optional, Union
from neo4j import GraphDatabase, Driver, Session
from loguru import logger
import yaml
from pathlib import Path

from .models import (
    Brand, Product, Ingredient, Effect, User, Review,
    Relationship, GraphQueryResult, RecommendationResult
)


class Neo4jClient:
    """Neo4j数据库客户端"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """初始化Neo4j客户端"""
        self.config = self._load_config(config_path)
        self.driver: Optional[Driver] = None
        self.connect()
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_path}")
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        return config['database']['neo4j']
    
    def connect(self) -> None:
        """连接到Neo4j数据库"""
        try:
            self.driver = GraphDatabase.driver(
                self.config['uri'],
                auth=(self.config['username'], self.config['password'])
            )
            # 测试连接
            with self.driver.session() as session:
                session.run("RETURN 1")
            logger.info("成功连接到Neo4j数据库")
        except Exception as e:
            logger.error(f"连接Neo4j数据库失败: {e}")
            raise
    
    def close(self) -> None:
        """关闭数据库连接"""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j数据库连接已关闭")
    
    def execute_query(self, query: str, parameters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """执行Cypher查询"""
        if not self.driver:
            raise RuntimeError("数据库未连接")
        
        try:
            with self.driver.session() as session:
                result = session.run(query, parameters or {})
                return [record.data() for record in result]
        except Exception as e:
            logger.error(f"执行查询失败: {query}, 错误: {e}")
            raise
    
    def create_indexes(self) -> None:
        """创建索引以提高查询性能"""
        indexes = [
            "CREATE INDEX brand_id_index IF NOT EXISTS FOR (b:Brand) ON (b.id)",
            "CREATE INDEX product_id_index IF NOT EXISTS FOR (p:Product) ON (p.id)",
            "CREATE INDEX ingredient_id_index IF NOT EXISTS FOR (i:Ingredient) ON (i.id)",
            "CREATE INDEX effect_id_index IF NOT EXISTS FOR (e:Effect) ON (e.id)",
            "CREATE INDEX user_id_index IF NOT EXISTS FOR (u:User) ON (u.id)",
            "CREATE INDEX product_name_index IF NOT EXISTS FOR (p:Product) ON (p.name)",
            "CREATE INDEX brand_name_index IF NOT EXISTS FOR (b:Brand) ON (b.name)",
            "CREATE INDEX ingredient_name_index IF NOT EXISTS FOR (i:Ingredient) ON (i.name)"
        ]
        
        for index_query in indexes:
            try:
                self.execute_query(index_query)
                logger.info(f"创建索引: {index_query}")
            except Exception as e:
                logger.warning(f"创建索引失败: {index_query}, 错误: {e}")
    
    def create_brand(self, brand: Brand) -> bool:
        """创建品牌节点"""
        query = """
        MERGE (b:Brand {id: $id})
        SET b.name = $name,
            b.name_en = $name_en,
            b.country = $country,
            b.founded_year = $founded_year,
            b.description = $description,
            b.website = $website,
            b.logo_url = $logo_url,
            b.price_range = $price_range,
            b.target_audience = $target_audience
        RETURN b
        """
        
        try:
            result = self.execute_query(query, brand.dict())
            return len(result) > 0
        except Exception as e:
            logger.error(f"创建品牌失败: {e}")
            return False
    
    def create_product(self, product: Product) -> bool:
        """创建产品节点"""
        query = """
        MERGE (p:Product {id: $id})
        SET p.name = $name,
            p.brand_id = $brand_id,
            p.category = $category,
            p.subcategory = $subcategory,
            p.price = $price,
            p.currency = $currency,
            p.volume = $volume,
            p.description = $description,
            p.ingredients = $ingredients,
            p.suitable_skin_types = $suitable_skin_types,
            p.effects = $effects,
            p.image_urls = $image_urls,
            p.rating = $rating,
            p.review_count = $review_count,
            p.launch_date = $launch_date
        RETURN p
        """
        
        try:
            result = self.execute_query(query, product.dict())
            return len(result) > 0
        except Exception as e:
            logger.error(f"创建产品失败: {e}")
            return False
    
    def create_ingredient(self, ingredient: Ingredient) -> bool:
        """创建成分节点"""
        query = """
        MERGE (i:Ingredient {id: $id})
        SET i.name = $name,
            i.name_en = $name_en,
            i.inci_name = $inci_name,
            i.cas_number = $cas_number,
            i.function = $function,
            i.safety_level = $safety_level,
            i.allergen = $allergen,
            i.pregnancy_safe = $pregnancy_safe,
            i.comedogenic_rating = $comedogenic_rating,
            i.description = $description
        RETURN i
        """
        
        try:
            result = self.execute_query(query, ingredient.dict())
            return len(result) > 0
        except Exception as e:
            logger.error(f"创建成分失败: {e}")
            return False
    
    def create_relationship(self, relationship: Relationship) -> bool:
        """创建关系"""
        query = f"""
        MATCH (a {{id: $source_id}}), (b {{id: $target_id}})
        MERGE (a)-[r:{relationship.relationship_type}]->(b)
        SET r += $properties
        RETURN r
        """
        
        try:
            params = {
                'source_id': relationship.source_id,
                'target_id': relationship.target_id,
                'properties': relationship.properties or {}
            }
            result = self.execute_query(query, params)
            return len(result) > 0
        except Exception as e:
            logger.error(f"创建关系失败: {e}")
            return False
    
    def find_products_by_brand(self, brand_id: str) -> List[Dict[str, Any]]:
        """根据品牌查找产品"""
        query = """
        MATCH (b:Brand {id: $brand_id})-[:PRODUCES]->(p:Product)
        RETURN p
        """
        
        return self.execute_query(query, {'brand_id': brand_id})
    
    def find_products_by_ingredient(self, ingredient_id: str) -> List[Dict[str, Any]]:
        """根据成分查找产品"""
        query = """
        MATCH (i:Ingredient {id: $ingredient_id})<-[:CONTAINS]-(p:Product)
        RETURN p, i
        """
        
        return self.execute_query(query, {'ingredient_id': ingredient_id})
    
    def find_similar_products(self, product_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """查找相似产品"""
        query = """
        MATCH (p1:Product {id: $product_id})-[r:SIMILAR_TO]-(p2:Product)
        RETURN p2, r.similarity_score as score, r.similarity_type as type
        ORDER BY r.similarity_score DESC
        LIMIT $limit
        """
        
        return self.execute_query(query, {'product_id': product_id, 'limit': limit})
    
    def get_product_ingredients(self, product_id: str) -> List[Dict[str, Any]]:
        """获取产品成分"""
        query = """
        MATCH (p:Product {id: $product_id})-[r:CONTAINS]->(i:Ingredient)
        RETURN i, r.concentration as concentration, r.position as position
        ORDER BY r.position
        """
        
        return self.execute_query(query, {'product_id': product_id})
    
    def recommend_products_for_user(self, user_id: str, limit: int = 10) -> List[RecommendationResult]:
        """为用户推荐产品"""
        # 基于用户购买历史和偏好的推荐算法
        query = """
        MATCH (u:User {id: $user_id})
        OPTIONAL MATCH (u)-[:PURCHASED]->(purchased:Product)
        OPTIONAL MATCH (purchased)-[:SIMILAR_TO]-(similar:Product)
        WHERE NOT (u)-[:PURCHASED]->(similar)
        WITH u, similar, COUNT(purchased) as purchase_count,
             AVG(similar.rating) as avg_rating
        WHERE similar IS NOT NULL
        RETURN similar.id as product_id,
               (purchase_count * 0.3 + avg_rating * 0.7) as score,
               'Based on purchase history and ratings' as reason,
               0.8 as confidence
        ORDER BY score DESC
        LIMIT $limit
        """
        
        results = self.execute_query(query, {'user_id': user_id, 'limit': limit})
        
        return [
            RecommendationResult(
                product_id=result['product_id'],
                score=result['score'],
                reason=result['reason'],
                confidence=result['confidence']
            )
            for result in results
        ]
    
    def analyze_brand_competition(self, brand_id: str) -> Dict[str, Any]:
        """分析品牌竞争情况"""
        query = """
        MATCH (b1:Brand {id: $brand_id})-[:PRODUCES]->(p1:Product)
        MATCH (b2:Brand)-[:PRODUCES]->(p2:Product)
        WHERE b1 <> b2 AND p1.category = p2.category
        WITH b1, b2, COUNT(p2) as competing_products,
             AVG(p2.price) as avg_competitor_price,
             AVG(p1.price) as avg_own_price
        RETURN b2.name as competitor_name,
               competing_products,
               avg_competitor_price,
               avg_own_price,
               (avg_own_price - avg_competitor_price) as price_difference
        ORDER BY competing_products DESC
        LIMIT 10
        """
        
        return self.execute_query(query, {'brand_id': brand_id})
    
    def get_ingredient_safety_analysis(self, product_id: str) -> Dict[str, Any]:
        """获取产品成分安全性分析"""
        query = """
        MATCH (p:Product {id: $product_id})-[:CONTAINS]->(i:Ingredient)
        RETURN i.name as ingredient_name,
               i.safety_level as safety_level,
               i.allergen as is_allergen,
               i.pregnancy_safe as pregnancy_safe,
               i.comedogenic_rating as comedogenic_rating
        ORDER BY i.safety_level DESC
        """
        
        return self.execute_query(query, {'product_id': product_id})
