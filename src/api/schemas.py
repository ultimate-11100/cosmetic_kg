"""
API数据模型定义
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class SkinTypeEnum(str, Enum):
    """肤质类型枚举"""
    DRY = "dry"
    OILY = "oily"
    COMBINATION = "combination"
    SENSITIVE = "sensitive"
    NORMAL = "normal"


class ProductCategoryEnum(str, Enum):
    """产品类别枚举"""
    SKINCARE = "skincare"
    MAKEUP = "makeup"
    FRAGRANCE = "fragrance"
    HAIRCARE = "haircare"
    BODYCARE = "bodycare"


class SafetyLevelEnum(str, Enum):
    """安全等级枚举"""
    SAFE = "safe"
    CAUTION = "caution"
    AVOID = "avoid"
    UNKNOWN = "unknown"


# ==================== 创建请求模型 ====================

class BrandCreate(BaseModel):
    """创建品牌请求模型"""
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


class ProductCreate(BaseModel):
    """创建产品请求模型"""
    id: str = Field(..., description="产品唯一标识")
    name: str = Field(..., description="产品名称")
    brand_id: str = Field(..., description="品牌ID")
    category: ProductCategoryEnum = Field(..., description="产品类别")
    subcategory: Optional[str] = Field(None, description="子类别")
    price: Optional[float] = Field(None, description="价格")
    currency: str = Field("CNY", description="货币单位")
    volume: Optional[str] = Field(None, description="容量/规格")
    description: Optional[str] = Field(None, description="产品描述")
    ingredients: Optional[List[str]] = Field(None, description="成分列表")
    suitable_skin_types: Optional[List[SkinTypeEnum]] = Field(None, description="适合肤质")
    effects: Optional[List[str]] = Field(None, description="功效")
    image_urls: Optional[List[str]] = Field(None, description="产品图片URLs")
    rating: Optional[float] = Field(None, description="评分")
    review_count: Optional[int] = Field(None, description="评论数量")
    launch_date: Optional[str] = Field(None, description="上市日期")


class IngredientCreate(BaseModel):
    """创建成分请求模型"""
    id: str = Field(..., description="成分唯一标识")
    name: str = Field(..., description="成分名称")
    name_en: Optional[str] = Field(None, description="英文名称")
    inci_name: Optional[str] = Field(None, description="INCI名称")
    cas_number: Optional[str] = Field(None, description="CAS号")
    function: Optional[List[str]] = Field(None, description="功能作用")
    safety_level: SafetyLevelEnum = Field(SafetyLevelEnum.UNKNOWN, description="安全等级")
    allergen: bool = Field(False, description="是否为过敏原")
    pregnancy_safe: Optional[bool] = Field(None, description="孕妇是否安全")
    comedogenic_rating: Optional[int] = Field(None, description="致痘等级(0-5)")
    description: Optional[str] = Field(None, description="成分描述")


class EffectCreate(BaseModel):
    """创建功效请求模型"""
    id: str = Field(..., description="功效唯一标识")
    name: str = Field(..., description="功效名称")
    name_en: Optional[str] = Field(None, description="英文名称")
    category: Optional[str] = Field(None, description="功效类别")
    description: Optional[str] = Field(None, description="功效描述")
    mechanism: Optional[str] = Field(None, description="作用机制")


class UserCreate(BaseModel):
    """创建用户请求模型"""
    id: str = Field(..., description="用户唯一标识")
    age_range: Optional[str] = Field(None, description="年龄段")
    skin_type: Optional[SkinTypeEnum] = Field(None, description="肤质类型")
    skin_concerns: Optional[List[str]] = Field(None, description="肌肤问题")
    budget_range: Optional[str] = Field(None, description="预算范围")
    preferred_brands: Optional[List[str]] = Field(None, description="偏好品牌")
    allergic_ingredients: Optional[List[str]] = Field(None, description="过敏成分")
    purchase_history: Optional[List[str]] = Field(None, description="购买历史")


class ReviewCreate(BaseModel):
    """创建评论请求模型"""
    id: str = Field(..., description="评论唯一标识")
    user_id: str = Field(..., description="用户ID")
    product_id: str = Field(..., description="产品ID")
    rating: float = Field(..., description="评分", ge=1, le=5)
    content: str = Field(..., description="评论内容")
    helpful_count: Optional[int] = Field(None, description="有用数")


# ==================== 更新请求模型 ====================

class BrandUpdate(BaseModel):
    """更新品牌请求模型"""
    name: Optional[str] = Field(None, description="品牌名称")
    name_en: Optional[str] = Field(None, description="英文名称")
    country: Optional[str] = Field(None, description="品牌国家")
    founded_year: Optional[int] = Field(None, description="成立年份")
    description: Optional[str] = Field(None, description="品牌描述")
    website: Optional[str] = Field(None, description="官方网站")
    logo_url: Optional[str] = Field(None, description="品牌Logo URL")
    price_range: Optional[str] = Field(None, description="价格区间")
    target_audience: Optional[List[str]] = Field(None, description="目标用户群体")


class ProductUpdate(BaseModel):
    """更新产品请求模型"""
    name: Optional[str] = Field(None, description="产品名称")
    category: Optional[ProductCategoryEnum] = Field(None, description="产品类别")
    subcategory: Optional[str] = Field(None, description="子类别")
    price: Optional[float] = Field(None, description="价格")
    currency: Optional[str] = Field(None, description="货币单位")
    volume: Optional[str] = Field(None, description="容量/规格")
    description: Optional[str] = Field(None, description="产品描述")
    ingredients: Optional[List[str]] = Field(None, description="成分列表")
    suitable_skin_types: Optional[List[SkinTypeEnum]] = Field(None, description="适合肤质")
    effects: Optional[List[str]] = Field(None, description="功效")
    image_urls: Optional[List[str]] = Field(None, description="产品图片URLs")
    rating: Optional[float] = Field(None, description="评分")
    review_count: Optional[int] = Field(None, description="评论数量")
    launch_date: Optional[str] = Field(None, description="上市日期")


# ==================== 查询请求模型 ====================

class ProductSearchQuery(BaseModel):
    """产品搜索查询模型"""
    keyword: Optional[str] = Field(None, description="关键词")
    category: Optional[ProductCategoryEnum] = Field(None, description="产品类别")
    brand_id: Optional[str] = Field(None, description="品牌ID")
    min_price: Optional[float] = Field(None, description="最低价格")
    max_price: Optional[float] = Field(None, description="最高价格")
    skin_type: Optional[SkinTypeEnum] = Field(None, description="适合肤质")
    effects: Optional[List[str]] = Field(None, description="功效")
    ingredients: Optional[List[str]] = Field(None, description="成分")
    sort_by: Optional[str] = Field("rating", description="排序字段")
    sort_order: Optional[str] = Field("desc", description="排序方向")
    limit: int = Field(20, description="返回数量限制", ge=1, le=100)
    offset: int = Field(0, description="偏移量", ge=0)


class RecommendationQuery(BaseModel):
    """推荐查询模型"""
    user_id: str = Field(..., description="用户ID")
    algorithm: str = Field("hybrid", description="推荐算法")
    limit: int = Field(10, description="推荐数量", ge=1, le=50)
    include_purchased: bool = Field(False, description="是否包含已购买产品")
    category_filter: Optional[List[ProductCategoryEnum]] = Field(None, description="类别过滤")
    price_range: Optional[Dict[str, float]] = Field(None, description="价格范围")


# ==================== 响应模型 ====================

class BrandResponse(BaseModel):
    """品牌响应模型"""
    id: str
    name: str
    name_en: Optional[str] = None
    country: Optional[str] = None
    founded_year: Optional[int] = None
    description: Optional[str] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None
    price_range: Optional[str] = None
    target_audience: Optional[List[str]] = None
    product_count: Optional[int] = None


class ProductResponse(BaseModel):
    """产品响应模型"""
    id: str
    name: str
    brand_id: str
    brand_name: Optional[str] = None
    category: ProductCategoryEnum
    subcategory: Optional[str] = None
    price: Optional[float] = None
    currency: str = "CNY"
    volume: Optional[str] = None
    description: Optional[str] = None
    ingredients: Optional[List[str]] = None
    suitable_skin_types: Optional[List[SkinTypeEnum]] = None
    effects: Optional[List[str]] = None
    image_urls: Optional[List[str]] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    launch_date: Optional[str] = None


class IngredientResponse(BaseModel):
    """成分响应模型"""
    id: str
    name: str
    name_en: Optional[str] = None
    inci_name: Optional[str] = None
    cas_number: Optional[str] = None
    function: Optional[List[str]] = None
    safety_level: SafetyLevelEnum
    allergen: bool
    pregnancy_safe: Optional[bool] = None
    comedogenic_rating: Optional[int] = None
    description: Optional[str] = None


class RecommendationResponse(BaseModel):
    """推荐响应模型"""
    product_id: str
    product_name: Optional[str] = None
    brand_name: Optional[str] = None
    score: float
    reason: str
    confidence: float
    product_info: Optional[Dict[str, Any]] = None


class SearchResponse(BaseModel):
    """搜索响应模型"""
    query: str
    total_count: int
    results: List[ProductResponse]
    facets: Optional[Dict[str, Any]] = None
    suggestions: Optional[List[str]] = None


class AnalysisResponse(BaseModel):
    """分析响应模型"""
    analysis_type: str
    target_id: str
    result: Dict[str, Any]
    confidence: float
    timestamp: str


class SafetyAnalysisResponse(BaseModel):
    """安全性分析响应模型"""
    product_id: str
    safety_score: float
    total_ingredients: int
    safe_ingredients: int
    caution_ingredients: int
    avoid_ingredients: int
    allergen_ingredients: List[str]
    pregnancy_unsafe_ingredients: List[str]
    detailed_analysis: List[Dict[str, Any]]


class CompetitionAnalysisResponse(BaseModel):
    """竞争分析响应模型"""
    brand_id: str
    brand_name: str
    competitors: List[Dict[str, Any]]
    market_position: Dict[str, Any]
    competitive_advantages: List[str]
    improvement_suggestions: List[str]


# ==================== 通用响应模型 ====================

class SuccessResponse(BaseModel):
    """成功响应模型"""
    success: bool = True
    message: str
    data: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    """错误响应模型"""
    success: bool = False
    error: str
    details: Optional[Dict[str, Any]] = None


class PaginatedResponse(BaseModel):
    """分页响应模型"""
    items: List[Dict[str, Any]]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool
