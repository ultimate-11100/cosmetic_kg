"""
化妆品知识图谱数据模型定义
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class SkinType(str, Enum):
    """肤质类型"""
    DRY = "dry"
    OILY = "oily"
    COMBINATION = "combination"
    SENSITIVE = "sensitive"
    NORMAL = "normal"


class ProductCategory(str, Enum):
    """产品类别"""
    SKINCARE = "skincare"
    MAKEUP = "makeup"
    FRAGRANCE = "fragrance"
    HAIRCARE = "haircare"
    BODYCARE = "bodycare"


class SafetyLevel(str, Enum):
    """安全等级"""
    SAFE = "safe"
    CAUTION = "caution"
    AVOID = "avoid"
    UNKNOWN = "unknown"


class Brand(BaseModel):
    """品牌实体"""
    id: str = Field(..., description="品牌唯一标识")
    name: str = Field(..., description="品牌名称")
    name_en: Optional[str] = Field(None, description="英文名称")
    country: Optional[str] = Field(None, description="品牌国家")
    founded_year: Optional[int] = Field(None, description="成立年份")
    description: Optional[str] = Field(None, description="品牌描述")
    website: Optional[str] = Field(None, description="官方网站")
    logo_url: Optional[str] = Field(None, description="品牌Logo URL")
    price_range: Optional[str] = Field(None, description="价格区间")
    target_audience: Optional[List[str]] = Field(None, description="目标用户群体")


class Ingredient(BaseModel):
    """成分实体"""
    id: str = Field(..., description="成分唯一标识")
    name: str = Field(..., description="成分名称")
    name_en: Optional[str] = Field(None, description="英文名称")
    inci_name: Optional[str] = Field(None, description="INCI名称")
    cas_number: Optional[str] = Field(None, description="CAS号")
    function: Optional[List[str]] = Field(None, description="功能作用")
    safety_level: SafetyLevel = Field(SafetyLevel.UNKNOWN, description="安全等级")
    allergen: bool = Field(False, description="是否为过敏原")
    pregnancy_safe: Optional[bool] = Field(None, description="孕妇是否安全")
    comedogenic_rating: Optional[int] = Field(None, description="致痘等级(0-5)")
    description: Optional[str] = Field(None, description="成分描述")


class Product(BaseModel):
    """产品实体"""
    id: str = Field(..., description="产品唯一标识")
    name: str = Field(..., description="产品名称")
    brand_id: str = Field(..., description="品牌ID")
    category: ProductCategory = Field(..., description="产品类别")
    subcategory: Optional[str] = Field(None, description="子类别")
    price: Optional[float] = Field(None, description="价格")
    currency: str = Field("CNY", description="货币单位")
    volume: Optional[str] = Field(None, description="容量/规格")
    description: Optional[str] = Field(None, description="产品描述")
    ingredients: Optional[List[str]] = Field(None, description="成分列表")
    suitable_skin_types: Optional[List[SkinType]] = Field(None, description="适合肤质")
    effects: Optional[List[str]] = Field(None, description="功效")
    image_urls: Optional[List[str]] = Field(None, description="产品图片URLs")
    rating: Optional[float] = Field(None, description="评分")
    review_count: Optional[int] = Field(None, description="评论数量")
    launch_date: Optional[str] = Field(None, description="上市日期")


class Effect(BaseModel):
    """功效实体"""
    id: str = Field(..., description="功效唯一标识")
    name: str = Field(..., description="功效名称")
    name_en: Optional[str] = Field(None, description="英文名称")
    category: Optional[str] = Field(None, description="功效类别")
    description: Optional[str] = Field(None, description="功效描述")
    mechanism: Optional[str] = Field(None, description="作用机制")


class User(BaseModel):
    """用户实体"""
    id: str = Field(..., description="用户唯一标识")
    age_range: Optional[str] = Field(None, description="年龄段")
    skin_type: Optional[SkinType] = Field(None, description="肤质类型")
    skin_concerns: Optional[List[str]] = Field(None, description="肌肤问题")
    budget_range: Optional[str] = Field(None, description="预算范围")
    preferred_brands: Optional[List[str]] = Field(None, description="偏好品牌")
    allergic_ingredients: Optional[List[str]] = Field(None, description="过敏成分")
    purchase_history: Optional[List[str]] = Field(None, description="购买历史")


class Review(BaseModel):
    """评论实体"""
    id: str = Field(..., description="评论唯一标识")
    user_id: str = Field(..., description="用户ID")
    product_id: str = Field(..., description="产品ID")
    rating: float = Field(..., description="评分")
    content: str = Field(..., description="评论内容")
    sentiment: Optional[float] = Field(None, description="情感分数")
    helpful_count: Optional[int] = Field(None, description="有用数")
    created_at: str = Field(..., description="创建时间")


# 关系定义
class Relationship(BaseModel):
    """关系基类"""
    source_id: str = Field(..., description="源节点ID")
    target_id: str = Field(..., description="目标节点ID")
    relationship_type: str = Field(..., description="关系类型")
    properties: Optional[Dict[str, Any]] = Field(None, description="关系属性")


class BrandProductRelation(Relationship):
    """品牌-产品关系"""
    relationship_type: str = Field("PRODUCES", description="关系类型")


class ProductIngredientRelation(Relationship):
    """产品-成分关系"""
    relationship_type: str = Field("CONTAINS", description="关系类型")
    concentration: Optional[float] = Field(None, description="浓度")
    position: Optional[int] = Field(None, description="成分表位置")


class ProductEffectRelation(Relationship):
    """产品-功效关系"""
    relationship_type: str = Field("HAS_EFFECT", description="关系类型")
    effectiveness: Optional[float] = Field(None, description="有效性评分")


class UserProductRelation(Relationship):
    """用户-产品关系"""
    relationship_type: str = Field("PURCHASED", description="关系类型")
    purchase_date: Optional[str] = Field(None, description="购买日期")
    satisfaction: Optional[float] = Field(None, description="满意度")


class ProductSimilarityRelation(Relationship):
    """产品相似性关系"""
    relationship_type: str = Field("SIMILAR_TO", description="关系类型")
    similarity_score: float = Field(..., description="相似度分数")
    similarity_type: str = Field(..., description="相似性类型")  # ingredient, effect, price, etc.


class CompetitorRelation(Relationship):
    """竞争关系"""
    relationship_type: str = Field("COMPETES_WITH", description="关系类型")
    competition_level: Optional[str] = Field(None, description="竞争程度")
    market_segment: Optional[str] = Field(None, description="市场细分")


# 图谱查询结果模型
class GraphQueryResult(BaseModel):
    """图谱查询结果"""
    nodes: List[Dict[str, Any]] = Field(..., description="节点列表")
    relationships: List[Dict[str, Any]] = Field(..., description="关系列表")
    total_count: int = Field(..., description="总数量")


class RecommendationResult(BaseModel):
    """推荐结果"""
    product_id: str = Field(..., description="产品ID")
    score: float = Field(..., description="推荐分数")
    reason: str = Field(..., description="推荐理由")
    confidence: float = Field(..., description="置信度")


class AnalysisResult(BaseModel):
    """分析结果"""
    analysis_type: str = Field(..., description="分析类型")
    result: Dict[str, Any] = Field(..., description="分析结果")
    confidence: float = Field(..., description="置信度")
    timestamp: str = Field(..., description="分析时间")
