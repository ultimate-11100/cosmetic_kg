#!/usr/bin/env python3
"""
数据库初始化脚本
"""

import sys
import os
from pathlib import Path
import json
import uuid
from loguru import logger

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.graph_database.neo4j_client import Neo4jClient
from src.graph_database.models import Brand, Product, Ingredient, Effect, User


def create_sample_brands():
    """创建示例品牌数据"""
    brands = [
        {
            "id": "brand_001",
            "name": "SK-II",
            "name_en": "SK-II",
            "country": "日本",
            "founded_year": 1980,
            "description": "SK-II是宝洁公司旗下的高端护肤品牌，以其独特的Pitera™成分而闻名。",
            "website": "https://www.sk-ii.com",
            "price_range": "高端",
            "target_audience": ["25-45岁女性", "高收入群体"]
        },
        {
            "id": "brand_002",
            "name": "兰蔻",
            "name_en": "Lancôme",
            "country": "法国",
            "founded_year": 1935,
            "description": "兰蔻是欧莱雅集团旗下的高端化妆品品牌，以其奢华的护肤和彩妆产品著称。",
            "website": "https://www.lancome.com",
            "price_range": "高端",
            "target_audience": ["20-50岁女性", "追求品质的消费者"]
        },
        {
            "id": "brand_003",
            "name": "雅诗兰黛",
            "name_en": "Estée Lauder",
            "country": "美国",
            "founded_year": 1946,
            "description": "雅诗兰黛是全球知名的化妆品集团，以其抗衰老护肤产品而闻名。",
            "website": "https://www.esteelauder.com",
            "price_range": "高端",
            "target_audience": ["25-55岁女性", "成熟消费者"]
        },
        {
            "id": "brand_004",
            "name": "欧莱雅",
            "name_en": "L'Oréal",
            "country": "法国",
            "founded_year": 1909,
            "description": "欧莱雅是全球最大的化妆品公司，提供从大众到高端的全系列产品。",
            "website": "https://www.loreal.com",
            "price_range": "中端",
            "target_audience": ["18-60岁", "广泛消费群体"]
        },
        {
            "id": "brand_005",
            "name": "薇姿",
            "name_en": "Vichy",
            "country": "法国",
            "founded_year": 1931,
            "description": "薇姿是欧莱雅集团旗下的药妆品牌，专注于敏感肌肤护理。",
            "website": "https://www.vichy.com",
            "price_range": "中端",
            "target_audience": ["敏感肌肤人群", "注重成分安全的消费者"]
        }
    ]
    
    return [Brand(**brand) for brand in brands]


def create_sample_ingredients():
    """创建示例成分数据"""
    ingredients = [
        {
            "id": "ingredient_001",
            "name": "透明质酸",
            "name_en": "Hyaluronic Acid",
            "inci_name": "Sodium Hyaluronate",
            "function": ["保湿", "锁水", "抗衰老"],
            "safety_level": "safe",
            "allergen": False,
            "pregnancy_safe": True,
            "comedogenic_rating": 0,
            "description": "透明质酸是一种天然的保湿成分，能够结合自身重量1000倍的水分。"
        },
        {
            "id": "ingredient_002",
            "name": "烟酰胺",
            "name_en": "Niacinamide",
            "inci_name": "Niacinamide",
            "function": ["美白", "控油", "收缩毛孔", "抗炎"],
            "safety_level": "safe",
            "allergen": False,
            "pregnancy_safe": True,
            "comedogenic_rating": 0,
            "description": "烟酰胺是维生素B3的一种形式，具有多重护肤功效。"
        },
        {
            "id": "ingredient_003",
            "name": "视黄醇",
            "name_en": "Retinol",
            "inci_name": "Retinol",
            "function": ["抗衰老", "去角质", "淡化细纹"],
            "safety_level": "caution",
            "allergen": False,
            "pregnancy_safe": False,
            "comedogenic_rating": 2,
            "description": "视黄醇是维生素A的一种形式，是强效的抗衰老成分。"
        },
        {
            "id": "ingredient_004",
            "name": "水杨酸",
            "name_en": "Salicylic Acid",
            "inci_name": "Salicylic Acid",
            "function": ["去角质", "控油", "祛痘", "收缩毛孔"],
            "safety_level": "caution",
            "allergen": False,
            "pregnancy_safe": False,
            "comedogenic_rating": 0,
            "description": "水杨酸是一种β-羟基酸，能够深入毛孔清洁。"
        },
        {
            "id": "ingredient_005",
            "name": "神经酰胺",
            "name_en": "Ceramide",
            "inci_name": "Ceramide NP",
            "function": ["修复屏障", "保湿", "抗敏"],
            "safety_level": "safe",
            "allergen": False,
            "pregnancy_safe": True,
            "comedogenic_rating": 0,
            "description": "神经酰胺是皮肤屏障的重要组成部分，能够修复和强化肌肤屏障。"
        }
    ]
    
    return [Ingredient(**ingredient) for ingredient in ingredients]


def create_sample_effects():
    """创建示例功效数据"""
    effects = [
        {
            "id": "effect_001",
            "name": "保湿",
            "name_en": "Moisturizing",
            "category": "基础护理",
            "description": "为肌肤补充和锁住水分，保持肌肤水润状态。",
            "mechanism": "通过吸湿剂、封闭剂和润肤剂的作用来维持肌肤水分平衡。"
        },
        {
            "id": "effect_002",
            "name": "美白",
            "name_en": "Whitening",
            "category": "美白淡斑",
            "description": "抑制黑色素生成，淡化色斑，提亮肤色。",
            "mechanism": "通过抑制酪氨酸酶活性或阻断黑色素传递来实现美白效果。"
        },
        {
            "id": "effect_003",
            "name": "抗衰老",
            "name_en": "Anti-aging",
            "category": "抗衰修护",
            "description": "延缓肌肤衰老，减少细纹和皱纹。",
            "mechanism": "通过促进胶原蛋白合成、抗氧化等方式来对抗肌肤老化。"
        },
        {
            "id": "effect_004",
            "name": "控油",
            "name_en": "Oil Control",
            "category": "控油祛痘",
            "description": "调节皮脂分泌，减少肌肤出油。",
            "mechanism": "通过调节皮脂腺活性或吸收多余油脂来控制出油。"
        },
        {
            "id": "effect_005",
            "name": "舒缓",
            "name_en": "Soothing",
            "category": "舒缓修护",
            "description": "缓解肌肤敏感和炎症，舒缓不适感。",
            "mechanism": "通过抗炎成分来减轻肌肤炎症反应。"
        }
    ]
    
    return [Effect(**effect) for effect in effects]


def create_sample_products():
    """创建示例产品数据"""
    products = [
        {
            "id": "product_001",
            "name": "SK-II 神仙水",
            "brand_id": "brand_001",
            "category": "skincare",
            "subcategory": "精华水",
            "price": 1299.0,
            "currency": "CNY",
            "volume": "230ml",
            "description": "含有独特Pitera™成分的护肤精华，能够改善肌肤质地，提升肌肤光泽。",
            "ingredients": ["Pitera", "透明质酸", "烟酰胺"],
            "suitable_skin_types": ["normal", "dry", "combination"],
            "effects": ["保湿", "提亮", "抗衰老"],
            "rating": 4.8,
            "review_count": 15420,
            "launch_date": "1980-01-01"
        },
        {
            "id": "product_002",
            "name": "兰蔻小黑瓶精华",
            "brand_id": "brand_002",
            "category": "skincare",
            "subcategory": "精华液",
            "price": 899.0,
            "currency": "CNY",
            "volume": "30ml",
            "description": "兰蔻经典抗衰老精华，含有多种活性成分，能够紧致肌肤，减少细纹。",
            "ingredients": ["腺苷", "透明质酸", "维生素E"],
            "suitable_skin_types": ["normal", "dry", "combination"],
            "effects": ["抗衰老", "紧致", "保湿"],
            "rating": 4.7,
            "review_count": 12890,
            "launch_date": "2009-01-01"
        },
        {
            "id": "product_003",
            "name": "雅诗兰黛小棕瓶精华",
            "brand_id": "brand_003",
            "category": "skincare",
            "subcategory": "精华液",
            "price": 799.0,
            "currency": "CNY",
            "volume": "30ml",
            "description": "雅诗兰黛明星产品，专注于肌肤修护和抗衰老。",
            "ingredients": ["透明质酸", "维生素C", "胜肽"],
            "suitable_skin_types": ["normal", "dry", "combination"],
            "effects": ["抗衰老", "修护", "提亮"],
            "rating": 4.6,
            "review_count": 9876,
            "launch_date": "1982-01-01"
        },
        {
            "id": "product_004",
            "name": "欧莱雅复颜抗皱紧致滋润日霜",
            "brand_id": "brand_004",
            "category": "skincare",
            "subcategory": "面霜",
            "price": 199.0,
            "currency": "CNY",
            "volume": "50ml",
            "description": "适合成熟肌肤的抗衰老日霜，质地滋润，易于吸收。",
            "ingredients": ["视黄醇", "透明质酸", "维生素E"],
            "suitable_skin_types": ["dry", "normal"],
            "effects": ["抗衰老", "保湿", "紧致"],
            "rating": 4.3,
            "review_count": 5432,
            "launch_date": "2015-01-01"
        },
        {
            "id": "product_005",
            "name": "薇姿温泉矿物保湿霜",
            "brand_id": "brand_005",
            "category": "skincare",
            "subcategory": "面霜",
            "price": 158.0,
            "currency": "CNY",
            "volume": "50ml",
            "description": "专为敏感肌肤设计的温和保湿霜，含有薇姿温泉水。",
            "ingredients": ["薇姿温泉水", "神经酰胺", "透明质酸"],
            "suitable_skin_types": ["sensitive", "dry"],
            "effects": ["保湿", "舒缓", "修护"],
            "rating": 4.4,
            "review_count": 3210,
            "launch_date": "2018-01-01"
        }
    ]
    
    return [Product(**product) for product in products]


def create_sample_users():
    """创建示例用户数据"""
    users = [
        {
            "id": "user_001",
            "age_range": "25-30",
            "skin_type": "combination",
            "skin_concerns": ["毛孔粗大", "偶尔长痘"],
            "budget_range": "500-1000",
            "preferred_brands": ["SK-II", "兰蔻"],
            "allergic_ingredients": [],
            "purchase_history": ["product_001", "product_002"]
        },
        {
            "id": "user_002",
            "age_range": "30-35",
            "skin_type": "dry",
            "skin_concerns": ["干燥", "细纹"],
            "budget_range": "300-800",
            "preferred_brands": ["雅诗兰黛", "欧莱雅"],
            "allergic_ingredients": ["香精"],
            "purchase_history": ["product_003", "product_004"]
        },
        {
            "id": "user_003",
            "age_range": "20-25",
            "skin_type": "sensitive",
            "skin_concerns": ["敏感", "泛红"],
            "budget_range": "100-300",
            "preferred_brands": ["薇姿"],
            "allergic_ingredients": ["酒精", "香精"],
            "purchase_history": ["product_005"]
        }
    ]
    
    return [User(**user) for user in users]


def create_relationships(neo4j_client):
    """创建实体关系"""
    relationships = [
        # 品牌-产品关系
        ("brand_001", "product_001", "PRODUCES"),
        ("brand_002", "product_002", "PRODUCES"),
        ("brand_003", "product_003", "PRODUCES"),
        ("brand_004", "product_004", "PRODUCES"),
        ("brand_005", "product_005", "PRODUCES"),
        
        # 产品-成分关系
        ("product_001", "ingredient_001", "CONTAINS"),
        ("product_001", "ingredient_002", "CONTAINS"),
        ("product_002", "ingredient_001", "CONTAINS"),
        ("product_003", "ingredient_001", "CONTAINS"),
        ("product_004", "ingredient_003", "CONTAINS"),
        ("product_004", "ingredient_001", "CONTAINS"),
        ("product_005", "ingredient_005", "CONTAINS"),
        ("product_005", "ingredient_001", "CONTAINS"),
        
        # 产品-功效关系
        ("product_001", "effect_001", "HAS_EFFECT"),
        ("product_001", "effect_002", "HAS_EFFECT"),
        ("product_001", "effect_003", "HAS_EFFECT"),
        ("product_002", "effect_003", "HAS_EFFECT"),
        ("product_002", "effect_001", "HAS_EFFECT"),
        ("product_003", "effect_003", "HAS_EFFECT"),
        ("product_003", "effect_001", "HAS_EFFECT"),
        ("product_004", "effect_003", "HAS_EFFECT"),
        ("product_004", "effect_001", "HAS_EFFECT"),
        ("product_005", "effect_001", "HAS_EFFECT"),
        ("product_005", "effect_005", "HAS_EFFECT"),
        
        # 用户-产品关系
        ("user_001", "product_001", "PURCHASED"),
        ("user_001", "product_002", "PURCHASED"),
        ("user_002", "product_003", "PURCHASED"),
        ("user_002", "product_004", "PURCHASED"),
        ("user_003", "product_005", "PURCHASED"),
    ]
    
    for source_id, target_id, relation_type in relationships:
        query = f"""
        MATCH (a {{id: $source_id}}), (b {{id: $target_id}})
        MERGE (a)-[r:{relation_type}]->(b)
        RETURN r
        """
        
        try:
            neo4j_client.execute_query(query, {
                'source_id': source_id,
                'target_id': target_id
            })
            logger.info(f"创建关系: {source_id} -{relation_type}-> {target_id}")
        except Exception as e:
            logger.error(f"创建关系失败: {e}")


def save_knowledge_base():
    """保存知识库文件"""
    knowledge_base_dir = Path("data/knowledge_base")
    knowledge_base_dir.mkdir(parents=True, exist_ok=True)
    
    # 品牌词典
    brands_dict = {
        "SK-II": {"type": "brand", "country": "日本", "category": "高端"},
        "兰蔻": {"type": "brand", "country": "法国", "category": "高端"},
        "雅诗兰黛": {"type": "brand", "country": "美国", "category": "高端"},
        "欧莱雅": {"type": "brand", "country": "法国", "category": "中端"},
        "薇姿": {"type": "brand", "country": "法国", "category": "药妆"}
    }
    
    with open(knowledge_base_dir / "brands.json", 'w', encoding='utf-8') as f:
        json.dump(brands_dict, f, ensure_ascii=False, indent=2)
    
    # 成分词典
    ingredients_dict = {
        "透明质酸": {"type": "ingredient", "safety": "safe", "function": ["保湿"]},
        "烟酰胺": {"type": "ingredient", "safety": "safe", "function": ["美白", "控油"]},
        "视黄醇": {"type": "ingredient", "safety": "caution", "function": ["抗衰老"]},
        "水杨酸": {"type": "ingredient", "safety": "caution", "function": ["去角质", "祛痘"]},
        "神经酰胺": {"type": "ingredient", "safety": "safe", "function": ["修复屏障"]}
    }
    
    with open(knowledge_base_dir / "ingredients.json", 'w', encoding='utf-8') as f:
        json.dump(ingredients_dict, f, ensure_ascii=False, indent=2)
    
    # 功效词典
    effects_dict = {
        "保湿": {"type": "effect", "category": "基础护理"},
        "美白": {"type": "effect", "category": "美白淡斑"},
        "抗衰老": {"type": "effect", "category": "抗衰修护"},
        "控油": {"type": "effect", "category": "控油祛痘"},
        "舒缓": {"type": "effect", "category": "舒缓修护"}
    }
    
    with open(knowledge_base_dir / "effects.json", 'w', encoding='utf-8') as f:
        json.dump(effects_dict, f, ensure_ascii=False, indent=2)
    
    # 类别词典
    categories_dict = {
        "精华水": {"type": "category", "parent": "护肤品"},
        "精华液": {"type": "category", "parent": "护肤品"},
        "面霜": {"type": "category", "parent": "护肤品"},
        "洁面": {"type": "category", "parent": "护肤品"},
        "面膜": {"type": "category", "parent": "护肤品"}
    }
    
    with open(knowledge_base_dir / "categories.json", 'w', encoding='utf-8') as f:
        json.dump(categories_dict, f, ensure_ascii=False, indent=2)
    
    logger.info("知识库文件保存完成")


def main():
    """主函数"""
    logger.info("开始初始化数据库...")
    
    try:
        # 连接Neo4j数据库
        neo4j_client = Neo4jClient()
        
        # 创建索引
        logger.info("创建数据库索引...")
        neo4j_client.create_indexes()
        
        # 创建示例数据
        logger.info("创建品牌数据...")
        brands = create_sample_brands()
        for brand in brands:
            neo4j_client.create_brand(brand)
        
        logger.info("创建成分数据...")
        ingredients = create_sample_ingredients()
        for ingredient in ingredients:
            neo4j_client.create_ingredient(ingredient)
        
        logger.info("创建功效数据...")
        effects = create_sample_effects()
        for effect in effects:
            query = """
            MERGE (e:Effect {id: $id})
            SET e.name = $name,
                e.name_en = $name_en,
                e.category = $category,
                e.description = $description,
                e.mechanism = $mechanism
            RETURN e
            """
            neo4j_client.execute_query(query, effect.dict())
        
        logger.info("创建产品数据...")
        products = create_sample_products()
        for product in products:
            neo4j_client.create_product(product)
        
        logger.info("创建用户数据...")
        users = create_sample_users()
        for user in users:
            query = """
            MERGE (u:User {id: $id})
            SET u.age_range = $age_range,
                u.skin_type = $skin_type,
                u.skin_concerns = $skin_concerns,
                u.budget_range = $budget_range,
                u.preferred_brands = $preferred_brands,
                u.allergic_ingredients = $allergic_ingredients,
                u.purchase_history = $purchase_history
            RETURN u
            """
            neo4j_client.execute_query(query, user.dict())
        
        # 创建关系
        logger.info("创建实体关系...")
        create_relationships(neo4j_client)
        
        # 保存知识库
        logger.info("保存知识库文件...")
        save_knowledge_base()
        
        # 关闭连接
        neo4j_client.close()
        
        logger.info("数据库初始化完成！")
        
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
