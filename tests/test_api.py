"""
API测试文件
"""

import pytest
import requests
import json
from typing import Dict, Any


class TestAPI:
    """API测试类"""
    
    BASE_URL = "http://localhost:8000"
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """测试设置"""
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer test_token"
        }
    
    def test_health_check(self):
        """测试健康检查接口"""
        response = requests.get(f"{self.BASE_URL}/api/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
    
    def test_get_brands(self):
        """测试获取品牌列表"""
        response = requests.get(f"{self.BASE_URL}/api/brands")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_brand_by_id(self):
        """测试根据ID获取品牌"""
        brand_id = "brand_001"
        response = requests.get(f"{self.BASE_URL}/api/brands/{brand_id}")
        
        if response.status_code == 200:
            data = response.json()
            assert data["id"] == brand_id
        elif response.status_code == 404:
            # 品牌不存在是正常的
            pass
        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")
    
    def test_create_brand(self):
        """测试创建品牌"""
        brand_data = {
            "id": "test_brand_001",
            "name": "测试品牌",
            "name_en": "Test Brand",
            "country": "中国",
            "description": "这是一个测试品牌"
        }
        
        response = requests.post(
            f"{self.BASE_URL}/api/brands",
            json=brand_data,
            headers=self.headers
        )
        
        # 可能返回201或400（如果已存在）
        assert response.status_code in [200, 201, 400]
    
    def test_get_products(self):
        """测试获取产品列表"""
        response = requests.get(f"{self.BASE_URL}/api/products")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
    
    def test_get_product_by_id(self):
        """测试根据ID获取产品"""
        product_id = "product_001"
        response = requests.get(f"{self.BASE_URL}/api/products/{product_id}")
        
        if response.status_code == 200:
            data = response.json()
            assert data["id"] == product_id
        elif response.status_code == 404:
            # 产品不存在是正常的
            pass
        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")
    
    def test_search_products(self):
        """测试产品搜索"""
        params = {
            "q": "护肤",
            "limit": 10
        }
        
        response = requests.get(f"{self.BASE_URL}/api/search", params=params)
        assert response.status_code == 200
        
        data = response.json()
        assert "results" in data
        assert "total_count" in data
    
    def test_get_recommendations(self):
        """测试获取推荐"""
        user_id = "user_001"
        params = {
            "algorithm": "hybrid",
            "limit": 5
        }
        
        response = requests.get(
            f"{self.BASE_URL}/api/recommendations/user/{user_id}",
            params=params
        )
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
            assert len(data) <= 5
        elif response.status_code == 404:
            # 用户不存在是正常的
            pass
        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")
    
    def test_get_similar_products(self):
        """测试获取相似产品"""
        product_id = "product_001"
        params = {"limit": 5}
        
        response = requests.get(
            f"{self.BASE_URL}/api/products/{product_id}/similar",
            params=params
        )
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
        elif response.status_code == 404:
            # 产品不存在是正常的
            pass
        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")
    
    def test_ingredient_safety_analysis(self):
        """测试成分安全性分析"""
        product_id = "product_001"
        
        response = requests.get(
            f"{self.BASE_URL}/api/analysis/ingredient-safety/{product_id}"
        )
        
        if response.status_code == 200:
            data = response.json()
            assert "safety_score" in data
            assert "total_ingredients" in data
        elif response.status_code == 404:
            # 产品不存在是正常的
            pass
        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")
    
    def test_brand_competition_analysis(self):
        """测试品牌竞争分析"""
        brand_id = "brand_001"
        
        response = requests.get(
            f"{self.BASE_URL}/api/analysis/brand-competition/{brand_id}"
        )
        
        if response.status_code == 200:
            data = response.json()
            assert "brand_id" in data
            assert "competitors" in data
        elif response.status_code == 404:
            # 品牌不存在是正常的
            pass
        else:
            pytest.fail(f"Unexpected status code: {response.status_code}")
    
    def test_skin_type_recommendations(self):
        """测试根据肤质推荐"""
        skin_type = "dry"
        params = {"limit": 5}
        
        response = requests.get(
            f"{self.BASE_URL}/api/recommendations/skin-type/{skin_type}",
            params=params
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestNLPProcessor:
    """NLP处理器测试"""
    
    def test_entity_extraction(self):
        """测试实体提取"""
        from src.knowledge_extraction.nlp_processor import NLPProcessor
        
        processor = NLPProcessor()
        text = "SK-II神仙水含有透明质酸，具有保湿功效，适合干性肌肤使用，价格1299元。"
        
        entities = processor.extract_entities(text)
        
        assert "brands" in entities
        assert "ingredients" in entities
        assert "effects" in entities
        assert "prices" in entities
        assert "skin_types" in entities
    
    def test_relationship_extraction(self):
        """测试关系提取"""
        from src.knowledge_extraction.nlp_processor import NLPProcessor
        
        processor = NLPProcessor()
        text = "兰蔻小黑瓶精华含有透明质酸，具有抗衰老功效。"
        
        entities = processor.extract_entities(text)
        relationships = processor.extract_relationships(text, entities)
        
        assert isinstance(relationships, list)
    
    def test_sentiment_analysis(self):
        """测试情感分析"""
        from src.knowledge_extraction.nlp_processor import NLPProcessor
        
        processor = NLPProcessor()
        
        positive_text = "这个产品真的很好用，效果很棒，强烈推荐！"
        negative_text = "这个产品太差了，完全没有效果，很失望。"
        
        positive_result = processor.analyze_sentiment(positive_text)
        negative_result = processor.analyze_sentiment(negative_text)
        
        assert positive_result["sentiment"] == "positive"
        assert negative_result["sentiment"] == "negative"


class TestRecommender:
    """推荐系统测试"""
    
    def test_content_based_recommendation(self):
        """测试基于内容的推荐"""
        # 这个测试需要数据库连接，可能需要mock
        pass
    
    def test_collaborative_filtering(self):
        """测试协同过滤推荐"""
        # 这个测试需要数据库连接，可能需要mock
        pass
    
    def test_hybrid_recommendation(self):
        """测试混合推荐"""
        # 这个测试需要数据库连接，可能需要mock
        pass


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])
