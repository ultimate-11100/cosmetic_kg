# 化妆品知识图谱项目 (Cosmetic Knowledge Graph)

## 项目概述

这是一个基于知识图谱技术的化妆品智能分析平台，通过构建化妆品领域的知识图谱，提供个性化推荐、成分分析、品牌洞察等商业价值服务。

## 核心功能

### 1. 知识图谱构建
- 化妆品实体识别（品牌、产品、成分、功效等）
- 实体关系抽取（包含、适用、竞争等关系）
- 多源数据融合（电商平台、官网、评论等）

### 2. 智能推荐系统
- 基于用户画像的个性化推荐
- 成分相似性推荐
- 功效导向推荐
- 价格敏感推荐

### 3. 成分安全分析
- 成分安全性评估
- 过敏原检测
- 孕妇适用性分析
- 敏感肌适用性分析

### 4. 商业智能分析
- 品牌竞争力分析
- 市场趋势预测
- 用户偏好洞察
- 价格策略分析

## 技术架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   数据采集层     │    │   知识抽取层     │    │   图数据库层     │
│                │    │                │    │                │
│ • 爬虫系统      │───▶│ • NLP处理      │───▶│ • Neo4j        │
│ • API接口      │    │ • 实体识别      │    │ • 图查询        │
│ • 数据清洗      │    │ • 关系抽取      │    │ • 图算法        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   关系数据库     │    │   推荐系统      │    │   可视化层      │
│                │    │                │    │                │
│ • MySQL存储    │    │ • 协同过滤      │    │ • Web界面      │
│ • 原始数据      │    │ • 内容推荐      │    │ • 图可视化      │
│ • 处理日志      │    │ • 混合推荐      │    │ • 数据大屏      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API服务层     │    │   缓存层        │    │   监控层        │
│                │    │                │    │                │
│ • RESTful API  │    │ • Redis缓存    │    │ • 日志监控      │
│ • GraphQL      │    │ • 会话存储      │    │ • 性能监控      │
│ • 认证授权      │    │ • 查询缓存      │    │ • 健康检查      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 商业价值

### 1. B2C应用场景
- **个性化购物助手**: 根据肤质、年龄、预算推荐合适产品
- **成分安全顾问**: 帮助用户避免过敏成分，选择安全产品
- **美妆知识问答**: 提供专业的美妆知识咨询服务

### 2. B2B应用场景
- **品牌竞争分析**: 为化妆品公司提供市场竞争洞察
- **产品研发支持**: 基于市场需求和成分分析指导新品开发
- **营销策略优化**: 基于用户画像和偏好数据优化营销策略

### 3. 数据变现模式
- **API服务收费**: 向第三方开发者提供付费API服务
- **企业定制服务**: 为化妆品公司提供定制化分析报告
- **广告推荐服务**: 基于精准用户画像的广告投放服务

## 项目结构

```
cosmetic_kg/
├── data/                   # 数据文件
│   ├── raw/               # 原始数据
│   ├── processed/         # 处理后数据
│   └── knowledge_base/    # 知识库
├── src/                   # 源代码
│   ├── data_collection/   # 数据采集
│   ├── knowledge_extraction/ # 知识抽取
│   ├── graph_database/    # 图数据库
│   ├── recommendation/    # 推荐系统
│   ├── api/              # API服务
│   └── visualization/    # 可视化
├── models/               # 机器学习模型
├── config/              # 配置文件
├── tests/               # 测试文件
├── docs/                # 文档
├── scripts/             # 脚本文件
└── requirements.txt     # 依赖包
```

## 快速开始

### 方式一：使用Docker Compose（推荐）

1. 克隆项目
```bash
git clone https://github.com/your-repo/cosmetic_kg.git
cd cosmetic_kg
```

2. 启动所有服务
```bash
# 启动核心服务
docker-compose up -d

# 等待服务启动完成（约2-3分钟）
docker-compose logs -f api
```

3. 初始化数据库
```bash
# 等待Neo4j完全启动后执行
docker-compose exec api python scripts/init_database.py
```

4. 访问服务
- 前端界面: http://localhost:3000
- API文档: http://localhost:8000/docs
- Neo4j浏览器: http://localhost:7474 (用户名: neo4j, 密码: password)

### 方式二：手动安装

#### 环境要求
- Python 3.8+
- Neo4j 4.0+
- Redis 6.0+
- Node.js 14+ (前端)

#### 安装步骤

1. 克隆项目
```bash
git clone https://github.com/your-repo/cosmetic_kg.git
cd cosmetic_kg
```

2. 安装Python依赖
```bash
pip install -r requirements.txt
```

3. 启动数据库服务
```bash
# 使用Docker启动数据库
docker-compose up -d neo4j redis mongodb
```

4. 使用启动脚本
```bash
# 启动所有服务（包括数据库初始化）
python scripts/start_services.py

# 或者分别启动
python scripts/start_services.py --api-only    # 仅启动API
python scripts/start_services.py --frontend-only  # 仅启动前端
```

## 使用示例

### 1. 获取产品推荐
```python
import requests

# 获取用户个性化推荐
response = requests.get('http://localhost:8000/api/recommendations/user/user_001?algorithm=hybrid&limit=10')
recommendations = response.json()

for rec in recommendations:
    print(f"推荐产品: {rec['product_id']}, 分数: {rec['score']}, 理由: {rec['reason']}")
```

### 2. 成分安全性分析
```python
# 分析产品成分安全性
response = requests.get('http://localhost:8000/api/analysis/ingredient-safety/product_001')
safety_analysis = response.json()

print(f"安全评分: {safety_analysis['safety_score']}")
print(f"安全成分: {safety_analysis['safe_ingredients']}")
print(f"需注意成分: {safety_analysis['caution_ingredients']}")
```

### 3. 智能搜索
```python
# 搜索护肤产品
response = requests.get('http://localhost:8000/api/search?q=保湿精华&limit=20')
search_results = response.json()

print(f"搜索到 {search_results['total_count']} 个产品")
for product in search_results['results']:
    print(f"- {product['name']} ({product['brand_name']}) - ¥{product['price']}")
```

## 数据采集

### 启动数据采集
```bash
# 采集所有数据源的产品数据
python scripts/collect_data.py --source all --type products --limit 1000

# 采集特定数据源的品牌数据
python scripts/collect_data.py --source sephora --type brands --limit 100

# 采集天猫护肤品数据
python scripts/collect_data.py --source tmall --keyword "护肤品" --limit 500
```

## 测试

### 运行测试
```bash
# 运行所有测试
pytest tests/ -v

# 运行API测试
pytest tests/test_api.py -v

# 运行特定测试
pytest tests/test_api.py::TestAPI::test_get_brands -v
```

### 性能测试
```bash
# 使用locust进行压力测试
pip install locust
locust -f tests/performance_test.py --host=http://localhost:8000
```

## 部署指南

### 生产环境部署

1. 修改配置文件
```bash
cp config/config.yaml config/config.prod.yaml
# 编辑生产环境配置
```

2. 使用Docker Compose部署
```bash
# 生产环境部署
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f api
```

3. 配置反向代理（Nginx）
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
        proxy_pass http://localhost:3000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 监控和维护

1. 健康检查
```bash
# 检查API服务状态
curl http://localhost:8000/api/health

# 检查数据库连接
docker-compose exec neo4j cypher-shell -u neo4j -p password "RETURN 1"
```

2. 日志监控
```bash
# 查看API日志
docker-compose logs -f api

# 查看数据库日志
docker-compose logs -f neo4j
```

3. 数据备份
```bash
# 备份Neo4j数据
docker-compose exec neo4j neo4j-admin dump --database=neo4j --to=/backups/neo4j-backup.dump

# 备份MongoDB数据
docker-compose exec mongodb mongodump --out /backups/mongodb-backup
```

## 开发指南

### 项目结构说明
- `src/api/`: FastAPI后端服务
- `src/graph_database/`: Neo4j图数据库操作
- `src/database/`: MySQL关系数据库操作
- `src/recommendation/`: 推荐系统算法
- `src/knowledge_extraction/`: NLP和知识抽取
- `src/data_collection/`: 数据采集爬虫
- `src/visualization/`: 前端可视化界面
- `config/`: 配置文件
- `scripts/`: 工具脚本
- `tests/`: 测试文件
- `docs/`: 文档

### 数据库架构
项目采用多数据库架构：
- **Neo4j**: 存储实体关系，支持复杂图查询和推荐算法
- **MySQL**: 存储原始数据、处理日志和结构化数据
- **Redis**: 缓存热点数据，提升查询性能

详细的MySQL配置和使用说明请参考 [docs/MYSQL_SETUP.md](docs/MYSQL_SETUP.md)

### 添加新功能

1. 添加新的API接口
```python
# 在 src/api/app.py 中添加新路由
@app.get("/api/new-feature")
async def new_feature():
    return {"message": "新功能"}
```

2. 扩展数据模型
```python
# 在 src/graph_database/models.py 中添加新模型
class NewEntity(BaseModel):
    id: str
    name: str
    # 其他字段...
```

3. 添加新的推荐算法
```python
# 在 src/recommendation/recommender.py 中添加新方法
def new_recommendation_algorithm(self, user_id: str) -> List[RecommendationResult]:
    # 实现新的推荐算法
    pass
```

详细的开发文档请参考 [docs/](docs/) 目录。

## 常见问题

### Q: Neo4j连接失败怎么办？
A: 检查Neo4j服务是否启动，确认端口7687可访问，验证用户名密码是否正确。

### Q: 前端页面无法加载数据？
A: 检查API服务是否正常运行，确认CORS配置是否正确。

### Q: 推荐结果为空？
A: 确认数据库中有足够的数据，检查用户是否存在购买历史。

### Q: 数据采集失败？
A: 检查网络连接，确认目标网站是否可访问，可能需要配置代理。

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request来改进项目！

### 贡献指南
1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 联系方式

- 项目维护者: [Your Name]
- 邮箱: [your.email@example.com]
- 项目主页: [https://github.com/your-repo/cosmetic_kg]
- 问题反馈: [https://github.com/your-repo/cosmetic_kg/issues]

## 致谢

感谢以下开源项目的支持：
- [Neo4j](https://neo4j.com/) - 图数据库
- [FastAPI](https://fastapi.tiangolo.com/) - Web框架
- [React](https://reactjs.org/) - 前端框架
- [spaCy](https://spacy.io/) - NLP库
- [scikit-learn](https://scikit-learn.org/) - 机器学习库
