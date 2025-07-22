# 化妆品知识图谱 API 文档

## 概述

化妆品知识图谱API提供了全面的化妆品数据查询、分析和推荐服务。基于Neo4j图数据库构建，支持复杂的关系查询和智能推荐。

## 基础信息

- **Base URL**: `http://localhost:8000`
- **API版本**: v1
- **认证方式**: Bearer Token
- **数据格式**: JSON

## 认证

所有API请求都需要在Header中包含认证信息：

```
Authorization: Bearer <your_token>
```

## 通用响应格式

### 成功响应
```json
{
  "success": true,
  "data": {...},
  "message": "操作成功"
}
```

### 错误响应
```json
{
  "success": false,
  "error": "错误信息",
  "details": {...}
}
```

## API 接口

### 1. 健康检查

检查API服务状态。

**请求**
```
GET /api/health
```

**响应**
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### 2. 品牌管理

#### 2.1 获取品牌列表

**请求**
```
GET /api/brands?limit=20&offset=0
```

**参数**
- `limit` (int): 返回数量限制，默认20，最大100
- `offset` (int): 偏移量，默认0

**响应**
```json
[
  {
    "id": "brand_001",
    "name": "SK-II",
    "name_en": "SK-II",
    "country": "日本",
    "founded_year": 1980,
    "description": "SK-II是宝洁公司旗下的高端护肤品牌...",
    "website": "https://www.sk-ii.com",
    "price_range": "高端",
    "target_audience": ["25-45岁女性", "高收入群体"]
  }
]
```

#### 2.2 获取品牌详情

**请求**
```
GET /api/brands/{brand_id}
```

**响应**
```json
{
  "id": "brand_001",
  "name": "SK-II",
  "name_en": "SK-II",
  "country": "日本",
  "founded_year": 1980,
  "description": "SK-II是宝洁公司旗下的高端护肤品牌...",
  "website": "https://www.sk-ii.com",
  "price_range": "高端",
  "target_audience": ["25-45岁女性", "高收入群体"],
  "product_count": 156
}
```

#### 2.3 创建品牌

**请求**
```
POST /api/brands
Content-Type: application/json

{
  "id": "brand_new",
  "name": "新品牌",
  "name_en": "New Brand",
  "country": "中国",
  "description": "品牌描述"
}
```

**响应**
```json
{
  "message": "品牌创建成功",
  "brand_id": "brand_new"
}
```

### 3. 产品管理

#### 3.1 获取产品列表

**请求**
```
GET /api/products?category=skincare&brand_id=brand_001&min_price=100&max_price=1000&limit=20&offset=0
```

**参数**
- `category` (string): 产品类别 (skincare, makeup, fragrance, haircare, bodycare)
- `brand_id` (string): 品牌ID
- `min_price` (float): 最低价格
- `max_price` (float): 最高价格
- `limit` (int): 返回数量限制
- `offset` (int): 偏移量

**响应**
```json
[
  {
    "id": "product_001",
    "name": "SK-II 神仙水",
    "brand_id": "brand_001",
    "brand_name": "SK-II",
    "category": "skincare",
    "subcategory": "精华水",
    "price": 1299.0,
    "currency": "CNY",
    "volume": "230ml",
    "description": "含有独特Pitera™成分的护肤精华...",
    "rating": 4.8,
    "review_count": 15420
  }
]
```

#### 3.2 获取产品详情

**请求**
```
GET /api/products/{product_id}
```

**响应**
```json
{
  "id": "product_001",
  "name": "SK-II 神仙水",
  "brand_id": "brand_001",
  "brand_name": "SK-II",
  "category": "skincare",
  "subcategory": "精华水",
  "price": 1299.0,
  "currency": "CNY",
  "volume": "230ml",
  "description": "含有独特Pitera™成分的护肤精华...",
  "ingredients": ["Pitera", "透明质酸", "烟酰胺"],
  "suitable_skin_types": ["normal", "dry", "combination"],
  "effects": ["保湿", "提亮", "抗衰老"],
  "rating": 4.8,
  "review_count": 15420,
  "launch_date": "1980-01-01"
}
```

#### 3.3 获取相似产品

**请求**
```
GET /api/products/{product_id}/similar?limit=10
```

**响应**
```json
[
  {
    "p2": {
      "id": "product_002",
      "name": "兰蔻小黑瓶精华",
      "price": 899.0
    },
    "score": 0.85,
    "type": "ingredient"
  }
]
```

### 4. 推荐系统

#### 4.1 用户个性化推荐

**请求**
```
GET /api/recommendations/user/{user_id}?algorithm=hybrid&limit=10
```

**参数**
- `algorithm` (string): 推荐算法 (collaborative, content, knowledge_graph, hybrid)
- `limit` (int): 推荐数量

**响应**
```json
[
  {
    "product_id": "product_003",
    "score": 0.92,
    "reason": "基于用户偏好和产品特征匹配",
    "confidence": 0.85
  }
]
```

#### 4.2 根据肤质推荐

**请求**
```
GET /api/recommendations/skin-type/{skin_type}?limit=10
```

**参数**
- `skin_type` (string): 肤质类型 (dry, oily, combination, sensitive, normal)

**响应**
```json
[
  {
    "product_id": "product_005",
    "score": 0.88,
    "reason": "适合干性肌肤",
    "confidence": 0.8
  }
]
```

### 5. 搜索功能

#### 5.1 产品搜索

**请求**
```
GET /api/search?q=保湿精华&limit=20
```

**参数**
- `q` (string): 搜索关键词
- `limit` (int): 返回数量限制

**响应**
```json
{
  "query": "保湿精华",
  "extracted_entities": {
    "brands": [],
    "ingredients": [],
    "effects": [{"text": "保湿", "label": "EFFECT"}],
    "categories": [{"text": "精华", "label": "CATEGORY"}]
  },
  "results": [
    {
      "id": "product_001",
      "name": "SK-II 神仙水",
      "brand_name": "SK-II",
      "price": 1299.0,
      "rating": 4.8
    }
  ],
  "total_count": 1
}
```

### 6. 分析功能

#### 6.1 成分安全性分析

**请求**
```
GET /api/analysis/ingredient-safety/{product_id}
```

**响应**
```json
{
  "product_id": "product_001",
  "safety_score": 0.85,
  "total_ingredients": 10,
  "safe_ingredients": 8,
  "caution_ingredients": 2,
  "avoid_ingredients": 0,
  "detailed_analysis": [
    {
      "ingredient_name": "透明质酸",
      "safety_level": "safe",
      "is_allergen": false,
      "pregnancy_safe": true,
      "comedogenic_rating": 0
    }
  ]
}
```

#### 6.2 品牌竞争分析

**请求**
```
GET /api/analysis/brand-competition/{brand_id}
```

**响应**
```json
{
  "brand_id": "brand_001",
  "competitors": [
    {
      "competitor_name": "兰蔻",
      "competing_products": 25,
      "avg_competitor_price": 850.0,
      "avg_own_price": 1200.0,
      "price_difference": 350.0
    }
  ]
}
```

## 错误代码

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 403 | 禁止访问 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

## 限制说明

- API调用频率限制：100次/分钟
- 单次查询最大返回数量：100条
- 搜索关键词最大长度：100字符

## SDK 示例

### Python
```python
import requests

class CosmeticKGClient:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {token}"}
    
    def get_brands(self, limit=20, offset=0):
        response = requests.get(
            f"{self.base_url}/api/brands",
            params={"limit": limit, "offset": offset},
            headers=self.headers
        )
        return response.json()
    
    def get_recommendations(self, user_id, algorithm="hybrid", limit=10):
        response = requests.get(
            f"{self.base_url}/api/recommendations/user/{user_id}",
            params={"algorithm": algorithm, "limit": limit},
            headers=self.headers
        )
        return response.json()

# 使用示例
client = CosmeticKGClient("http://localhost:8000", "your_token")
brands = client.get_brands(limit=10)
recommendations = client.get_recommendations("user_001")
```

### JavaScript
```javascript
class CosmeticKGClient {
    constructor(baseUrl, token) {
        this.baseUrl = baseUrl;
        this.headers = {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        };
    }
    
    async getBrands(limit = 20, offset = 0) {
        const response = await fetch(
            `${this.baseUrl}/api/brands?limit=${limit}&offset=${offset}`,
            { headers: this.headers }
        );
        return response.json();
    }
    
    async getRecommendations(userId, algorithm = 'hybrid', limit = 10) {
        const response = await fetch(
            `${this.baseUrl}/api/recommendations/user/${userId}?algorithm=${algorithm}&limit=${limit}`,
            { headers: this.headers }
        );
        return response.json();
    }
}

// 使用示例
const client = new CosmeticKGClient('http://localhost:8000', 'your_token');
const brands = await client.getBrands(10);
const recommendations = await client.getRecommendations('user_001');
```

## 更新日志

### v1.0.0 (2024-01-01)
- 初始版本发布
- 支持品牌、产品、成分、功效的CRUD操作
- 实现基于知识图谱的推荐系统
- 提供成分安全性分析功能
- 支持智能搜索和实体识别
