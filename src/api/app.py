"""
化妆品知识图谱API服务
"""

from fastapi import FastAPI, HTTPException, Depends, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Dict, Any, Optional
import uvicorn
from loguru import logger
import yaml
from pathlib import Path as FilePath

from ..graph_database.neo4j_client import Neo4jClient
from ..graph_database.models import (
    Brand, Product, Ingredient, Effect, User, Review,
    GraphQueryResult, RecommendationResult, AnalysisResult
)
from ..recommendation.recommender import CosmeticRecommender
from ..knowledge_extraction.nlp_processor import NLPProcessor
from .schemas import *


# 初始化FastAPI应用
app = FastAPI(
    title="化妆品知识图谱API",
    description="基于知识图谱的化妆品智能分析和推荐系统",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 安全认证
security = HTTPBearer()

# 全局变量
neo4j_client: Optional[Neo4jClient] = None
recommender: Optional[CosmeticRecommender] = None
nlp_processor: Optional[NLPProcessor] = None


def load_config() -> Dict[str, Any]:
    """加载配置文件"""
    config_file = FilePath("config/config.yaml")
    if config_file.exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    return {}


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    global neo4j_client, recommender, nlp_processor
    
    try:
        # 初始化Neo4j客户端
        neo4j_client = Neo4jClient()
        logger.info("Neo4j客户端初始化成功")
        
        # 初始化推荐系统
        recommender = CosmeticRecommender(neo4j_client)
        logger.info("推荐系统初始化成功")
        
        # 初始化NLP处理器
        nlp_processor = NLPProcessor()
        logger.info("NLP处理器初始化成功")
        
        logger.info("API服务启动成功")
        
    except Exception as e:
        logger.error(f"API服务启动失败: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    global neo4j_client
    
    if neo4j_client:
        neo4j_client.close()
        logger.info("Neo4j连接已关闭")


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """获取当前用户（简化版认证）"""
    # 这里应该实现真正的JWT token验证
    # 现在只是简单返回一个用户ID
    return "user_123"


# ==================== 品牌相关API ====================

@app.post("/api/brands", response_model=Dict[str, Any])
async def create_brand(brand: BrandCreate):
    """创建品牌"""
    try:
        brand_obj = Brand(**brand.dict())
        success = neo4j_client.create_brand(brand_obj)
        
        if success:
            return {"message": "品牌创建成功", "brand_id": brand.id}
        else:
            raise HTTPException(status_code=400, detail="品牌创建失败")
            
    except Exception as e:
        logger.error(f"创建品牌失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/brands/{brand_id}", response_model=Dict[str, Any])
async def get_brand(brand_id: str = Path(..., description="品牌ID")):
    """获取品牌信息"""
    try:
        query = "MATCH (b:Brand {id: $brand_id}) RETURN b"
        results = neo4j_client.execute_query(query, {"brand_id": brand_id})
        
        if not results:
            raise HTTPException(status_code=404, detail="品牌不存在")
        
        return results[0]['b']
        
    except Exception as e:
        logger.error(f"获取品牌信息失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/brands", response_model=List[Dict[str, Any]])
async def list_brands(
    limit: int = Query(20, ge=1, le=100, description="返回数量限制"),
    offset: int = Query(0, ge=0, description="偏移量")
):
    """获取品牌列表"""
    try:
        query = """
        MATCH (b:Brand)
        RETURN b
        ORDER BY b.name
        SKIP $offset LIMIT $limit
        """
        
        results = neo4j_client.execute_query(query, {
            "limit": limit,
            "offset": offset
        })
        
        return [result['b'] for result in results]
        
    except Exception as e:
        logger.error(f"获取品牌列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 产品相关API ====================

@app.post("/api/products", response_model=Dict[str, Any])
async def create_product(product: ProductCreate):
    """创建产品"""
    try:
        product_obj = Product(**product.dict())
        success = neo4j_client.create_product(product_obj)
        
        if success:
            return {"message": "产品创建成功", "product_id": product.id}
        else:
            raise HTTPException(status_code=400, detail="产品创建失败")
            
    except Exception as e:
        logger.error(f"创建产品失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/products/{product_id}", response_model=Dict[str, Any])
async def get_product(product_id: str = Path(..., description="产品ID")):
    """获取产品详细信息"""
    try:
        query = """
        MATCH (p:Product {id: $product_id})
        OPTIONAL MATCH (b:Brand)-[:PRODUCES]->(p)
        OPTIONAL MATCH (p)-[:CONTAINS]->(i:Ingredient)
        OPTIONAL MATCH (p)-[:HAS_EFFECT]->(e:Effect)
        RETURN p, b.name as brand_name, 
               collect(DISTINCT i.name) as ingredients,
               collect(DISTINCT e.name) as effects
        """
        
        results = neo4j_client.execute_query(query, {"product_id": product_id})
        
        if not results:
            raise HTTPException(status_code=404, detail="产品不存在")
        
        result = results[0]
        product_info = result['p']
        product_info['brand_name'] = result['brand_name']
        product_info['ingredients'] = result['ingredients']
        product_info['effects'] = result['effects']
        
        return product_info
        
    except Exception as e:
        logger.error(f"获取产品信息失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/products", response_model=List[Dict[str, Any]])
async def list_products(
    category: Optional[str] = Query(None, description="产品类别"),
    brand_id: Optional[str] = Query(None, description="品牌ID"),
    min_price: Optional[float] = Query(None, description="最低价格"),
    max_price: Optional[float] = Query(None, description="最高价格"),
    limit: int = Query(20, ge=1, le=100, description="返回数量限制"),
    offset: int = Query(0, ge=0, description="偏移量")
):
    """获取产品列表"""
    try:
        conditions = []
        params = {"limit": limit, "offset": offset}
        
        if category:
            conditions.append("p.category = $category")
            params["category"] = category
        
        if brand_id:
            conditions.append("p.brand_id = $brand_id")
            params["brand_id"] = brand_id
        
        if min_price is not None:
            conditions.append("p.price >= $min_price")
            params["min_price"] = min_price
        
        if max_price is not None:
            conditions.append("p.price <= $max_price")
            params["max_price"] = max_price
        
        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
        
        query = f"""
        MATCH (p:Product)
        {where_clause}
        RETURN p
        ORDER BY p.rating DESC, p.name
        SKIP $offset LIMIT $limit
        """
        
        results = neo4j_client.execute_query(query, params)
        return [result['p'] for result in results]
        
    except Exception as e:
        logger.error(f"获取产品列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 推荐相关API ====================

@app.get("/api/recommendations/user/{user_id}", response_model=List[RecommendationResult])
async def get_user_recommendations(
    user_id: str = Path(..., description="用户ID"),
    algorithm: str = Query("hybrid", description="推荐算法: collaborative, content, knowledge_graph, hybrid"),
    limit: int = Query(10, ge=1, le=50, description="推荐数量")
):
    """获取用户个性化推荐"""
    try:
        if algorithm == "collaborative":
            recommendations = recommender.collaborative_filtering_recommend(user_id, limit)
        elif algorithm == "content":
            recommendations = recommender.content_based_recommend(user_id, limit)
        elif algorithm == "knowledge_graph":
            recommendations = recommender.knowledge_graph_recommend(user_id, limit)
        elif algorithm == "hybrid":
            recommendations = recommender.hybrid_recommend(user_id, limit)
        else:
            raise HTTPException(status_code=400, detail="不支持的推荐算法")
        
        return recommendations
        
    except Exception as e:
        logger.error(f"获取用户推荐失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/recommendations/skin-type/{skin_type}", response_model=List[RecommendationResult])
async def get_skin_type_recommendations(
    skin_type: str = Path(..., description="肤质类型"),
    limit: int = Query(10, ge=1, le=50, description="推荐数量")
):
    """根据肤质推荐产品"""
    try:
        recommendations = recommender.get_product_recommendations_by_skin_type(skin_type, limit)
        return recommendations
        
    except Exception as e:
        logger.error(f"获取肤质推荐失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/products/{product_id}/similar", response_model=List[Dict[str, Any]])
async def get_similar_products(
    product_id: str = Path(..., description="产品ID"),
    limit: int = Query(10, ge=1, le=50, description="相似产品数量")
):
    """获取相似产品"""
    try:
        similar_products = neo4j_client.find_similar_products(product_id, limit)
        return similar_products
        
    except Exception as e:
        logger.error(f"获取相似产品失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 分析相关API ====================

@app.get("/api/analysis/ingredient-safety/{product_id}", response_model=Dict[str, Any])
async def analyze_ingredient_safety(product_id: str = Path(..., description="产品ID")):
    """分析产品成分安全性"""
    try:
        safety_analysis = neo4j_client.get_ingredient_safety_analysis(product_id)
        
        # 计算安全性评分
        total_ingredients = len(safety_analysis)
        if total_ingredients == 0:
            return {"message": "未找到产品成分信息"}
        
        safe_count = sum(1 for item in safety_analysis if item['safety_level'] == 'safe')
        caution_count = sum(1 for item in safety_analysis if item['safety_level'] == 'caution')
        avoid_count = sum(1 for item in safety_analysis if item['safety_level'] == 'avoid')
        
        safety_score = (safe_count * 1.0 + caution_count * 0.5 + avoid_count * 0.0) / total_ingredients
        
        return {
            "product_id": product_id,
            "safety_score": safety_score,
            "total_ingredients": total_ingredients,
            "safe_ingredients": safe_count,
            "caution_ingredients": caution_count,
            "avoid_ingredients": avoid_count,
            "detailed_analysis": safety_analysis
        }
        
    except Exception as e:
        logger.error(f"成分安全性分析失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analysis/brand-competition/{brand_id}", response_model=Dict[str, Any])
async def analyze_brand_competition(brand_id: str = Path(..., description="品牌ID")):
    """分析品牌竞争情况"""
    try:
        competition_analysis = neo4j_client.analyze_brand_competition(brand_id)
        return {
            "brand_id": brand_id,
            "competitors": competition_analysis
        }
        
    except Exception as e:
        logger.error(f"品牌竞争分析失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 搜索相关API ====================

@app.get("/api/search", response_model=Dict[str, Any])
async def search_products(
    q: str = Query(..., description="搜索关键词"),
    limit: int = Query(20, ge=1, le=100, description="返回数量限制")
):
    """搜索产品"""
    try:
        # 使用NLP处理搜索查询
        entities = nlp_processor.extract_entities(q)
        
        # 构建搜索查询
        search_conditions = []
        params = {"limit": limit}
        
        # 根据提取的实体构建查询条件
        if entities['brands']:
            brand_names = [brand['text'] for brand in entities['brands']]
            search_conditions.append("b.name IN $brand_names")
            params["brand_names"] = brand_names
        
        if entities['categories']:
            categories = [cat['text'] for cat in entities['categories']]
            search_conditions.append("p.category IN $categories")
            params["categories"] = categories
        
        # 文本搜索
        search_conditions.append("(p.name CONTAINS $query OR p.description CONTAINS $query)")
        params["query"] = q
        
        where_clause = "WHERE " + " OR ".join(search_conditions) if search_conditions else ""
        
        query = f"""
        MATCH (p:Product)
        OPTIONAL MATCH (b:Brand)-[:PRODUCES]->(p)
        {where_clause}
        RETURN p, b.name as brand_name
        ORDER BY p.rating DESC
        LIMIT $limit
        """
        
        results = neo4j_client.execute_query(query, params)
        
        products = []
        for result in results:
            product = result['p']
            product['brand_name'] = result['brand_name']
            products.append(product)
        
        return {
            "query": q,
            "extracted_entities": entities,
            "results": products,
            "total_count": len(products)
        }
        
    except Exception as e:
        logger.error(f"搜索失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 健康检查API ====================

@app.get("/api/health")
async def health_check():
    """健康检查"""
    try:
        # 测试数据库连接
        neo4j_client.execute_query("RETURN 1")
        
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": "2024-01-01T00:00:00Z"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": "2024-01-01T00:00:00Z"
        }


if __name__ == "__main__":
    config = load_config()
    api_config = config.get('api', {})
    
    uvicorn.run(
        "src.api.app:app",
        host=api_config.get('host', '0.0.0.0'),
        port=api_config.get('port', 8000),
        reload=api_config.get('debug', True)
    )
