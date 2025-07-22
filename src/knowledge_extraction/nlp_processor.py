"""
自然语言处理模块 - 用于实体识别和关系抽取
"""

import spacy
import jieba
import re
from typing import List, Dict, Any, Tuple, Optional
from loguru import logger
import json
from pathlib import Path
import yaml
from transformers import AutoTokenizer, AutoModel
import torch
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


class NLPProcessor:
    """NLP处理器"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """初始化NLP处理器"""
        self.config = self._load_config(config_path)
        self.nlp = None
        self.bert_tokenizer = None
        self.bert_model = None
        self._load_models()
        self._load_dictionaries()
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        config_file = Path(config_path)
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            return config.get('nlp', {})
        return {}
    
    def _load_models(self) -> None:
        """加载NLP模型"""
        try:
            # 加载spaCy模型
            model_name = self.config.get('models', {}).get('spacy_model', 'zh_core_web_sm')
            try:
                self.nlp = spacy.load(model_name)
            except OSError:
                logger.warning(f"spaCy模型 {model_name} 未找到，使用基础模型")
                self.nlp = spacy.blank('zh')
            
            # 加载BERT模型
            bert_model_name = self.config.get('models', {}).get('bert_model', 'bert-base-chinese')
            try:
                self.bert_tokenizer = AutoTokenizer.from_pretrained(bert_model_name)
                self.bert_model = AutoModel.from_pretrained(bert_model_name)
                logger.info("BERT模型加载成功")
            except Exception as e:
                logger.warning(f"BERT模型加载失败: {e}")
            
        except Exception as e:
            logger.error(f"模型加载失败: {e}")
    
    def _load_dictionaries(self) -> None:
        """加载领域词典"""
        self.brand_dict = self._load_dictionary("data/knowledge_base/brands.json")
        self.ingredient_dict = self._load_dictionary("data/knowledge_base/ingredients.json")
        self.effect_dict = self._load_dictionary("data/knowledge_base/effects.json")
        self.category_dict = self._load_dictionary("data/knowledge_base/categories.json")
        
        # 添加自定义词汇到jieba
        for brand in self.brand_dict.keys():
            jieba.add_word(brand)
        for ingredient in self.ingredient_dict.keys():
            jieba.add_word(ingredient)
    
    def _load_dictionary(self, file_path: str) -> Dict[str, Any]:
        """加载词典文件"""
        dict_file = Path(file_path)
        if dict_file.exists():
            with open(dict_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            logger.warning(f"词典文件不存在: {file_path}")
            return {}
    
    def extract_entities(self, text: str) -> Dict[str, List[Dict[str, Any]]]:
        """提取实体"""
        entities = {
            'brands': [],
            'ingredients': [],
            'effects': [],
            'categories': [],
            'prices': [],
            'skin_types': []
        }
        
        # 使用jieba分词
        words = list(jieba.cut(text))
        
        # 品牌识别
        entities['brands'] = self._extract_brands(text, words)
        
        # 成分识别
        entities['ingredients'] = self._extract_ingredients(text, words)
        
        # 功效识别
        entities['effects'] = self._extract_effects(text, words)
        
        # 类别识别
        entities['categories'] = self._extract_categories(text, words)
        
        # 价格识别
        entities['prices'] = self._extract_prices(text)
        
        # 肤质识别
        entities['skin_types'] = self._extract_skin_types(text, words)
        
        return entities
    
    def _extract_brands(self, text: str, words: List[str]) -> List[Dict[str, Any]]:
        """提取品牌实体"""
        brands = []
        
        # 基于词典匹配
        for word in words:
            if word in self.brand_dict:
                brands.append({
                    'text': word,
                    'label': 'BRAND',
                    'confidence': 0.9,
                    'info': self.brand_dict[word]
                })
        
        # 基于规则的品牌识别
        brand_patterns = [
            r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*',  # 英文品牌名
            r'[A-Z]{2,}',  # 全大写缩写
        ]
        
        for pattern in brand_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                brand_text = match.group()
                if len(brand_text) > 1 and brand_text not in [b['text'] for b in brands]:
                    brands.append({
                        'text': brand_text,
                        'label': 'BRAND',
                        'confidence': 0.7,
                        'start': match.start(),
                        'end': match.end()
                    })
        
        return brands
    
    def _extract_ingredients(self, text: str, words: List[str]) -> List[Dict[str, Any]]:
        """提取成分实体"""
        ingredients = []
        
        # 基于词典匹配
        for word in words:
            if word in self.ingredient_dict:
                ingredients.append({
                    'text': word,
                    'label': 'INGREDIENT',
                    'confidence': 0.9,
                    'info': self.ingredient_dict[word]
                })
        
        # 基于规则的成分识别
        ingredient_patterns = [
            r'[A-Za-z\-]+酸',  # 各种酸类
            r'维生素[A-Z]',    # 维生素
            r'透明质酸|玻尿酸',  # 常见成分
            r'胶原蛋白',
            r'神经酰胺',
            r'烟酰胺',
        ]
        
        for pattern in ingredient_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                ingredient_text = match.group()
                if ingredient_text not in [i['text'] for i in ingredients]:
                    ingredients.append({
                        'text': ingredient_text,
                        'label': 'INGREDIENT',
                        'confidence': 0.8,
                        'start': match.start(),
                        'end': match.end()
                    })
        
        return ingredients
    
    def _extract_effects(self, text: str, words: List[str]) -> List[Dict[str, Any]]:
        """提取功效实体"""
        effects = []
        
        # 功效关键词
        effect_keywords = [
            '保湿', '补水', '美白', '祛斑', '抗衰老', '紧致',
            '控油', '祛痘', '舒缓', '修复', '防晒', '去角质',
            '淡化细纹', '提亮肤色', '收缩毛孔', '抗氧化'
        ]
        
        for keyword in effect_keywords:
            if keyword in text:
                effects.append({
                    'text': keyword,
                    'label': 'EFFECT',
                    'confidence': 0.8
                })
        
        return effects
    
    def _extract_categories(self, text: str, words: List[str]) -> List[Dict[str, Any]]:
        """提取类别实体"""
        categories = []
        
        category_keywords = [
            '洁面', '爽肤水', '精华', '面霜', '面膜', '防晒霜',
            '粉底', '口红', '眼影', '睫毛膏', '腮红', '香水'
        ]
        
        for keyword in category_keywords:
            if keyword in text:
                categories.append({
                    'text': keyword,
                    'label': 'CATEGORY',
                    'confidence': 0.8
                })
        
        return categories
    
    def _extract_prices(self, text: str) -> List[Dict[str, Any]]:
        """提取价格实体"""
        prices = []
        
        # 价格模式
        price_patterns = [
            r'¥\s*(\d+(?:\.\d{2})?)',  # ¥199.00
            r'(\d+(?:\.\d{2})?)\s*元',  # 199元
            r'\$\s*(\d+(?:\.\d{2})?)',  # $29.99
        ]
        
        for pattern in price_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                price_value = float(match.group(1))
                prices.append({
                    'text': match.group(),
                    'label': 'PRICE',
                    'value': price_value,
                    'confidence': 0.9,
                    'start': match.start(),
                    'end': match.end()
                })
        
        return prices
    
    def _extract_skin_types(self, text: str, words: List[str]) -> List[Dict[str, Any]]:
        """提取肤质实体"""
        skin_types = []
        
        skin_type_keywords = [
            '干性肌肤', '油性肌肤', '混合性肌肤', '敏感肌肤', '中性肌肤',
            '干皮', '油皮', '混合皮', '敏感皮', '痘痘肌'
        ]
        
        for keyword in skin_type_keywords:
            if keyword in text:
                skin_types.append({
                    'text': keyword,
                    'label': 'SKIN_TYPE',
                    'confidence': 0.8
                })
        
        return skin_types
    
    def extract_relationships(self, text: str, entities: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """提取实体关系"""
        relationships = []
        
        # 产品-品牌关系
        relationships.extend(self._extract_product_brand_relations(text, entities))
        
        # 产品-成分关系
        relationships.extend(self._extract_product_ingredient_relations(text, entities))
        
        # 产品-功效关系
        relationships.extend(self._extract_product_effect_relations(text, entities))
        
        # 产品-适用肤质关系
        relationships.extend(self._extract_product_skintype_relations(text, entities))
        
        return relationships
    
    def _extract_product_brand_relations(self, text: str, entities: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """提取产品-品牌关系"""
        relations = []
        
        brands = entities.get('brands', [])
        categories = entities.get('categories', [])
        
        for brand in brands:
            for category in categories:
                # 简单的距离判断
                if abs(brand.get('start', 0) - category.get('start', 0)) < 50:
                    relations.append({
                        'source': brand['text'],
                        'target': category['text'],
                        'relation': 'PRODUCES',
                        'confidence': 0.7
                    })
        
        return relations
    
    def _extract_product_ingredient_relations(self, text: str, entities: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """提取产品-成分关系"""
        relations = []
        
        ingredients = entities.get('ingredients', [])
        categories = entities.get('categories', [])
        
        # 寻找"含有"、"添加"等关系词
        contain_patterns = [r'含有', r'添加', r'富含', r'包含']
        
        for ingredient in ingredients:
            for category in categories:
                for pattern in contain_patterns:
                    if re.search(f'{category["text"]}.*{pattern}.*{ingredient["text"]}', text) or \
                       re.search(f'{ingredient["text"]}.*{pattern}.*{category["text"]}', text):
                        relations.append({
                            'source': category['text'],
                            'target': ingredient['text'],
                            'relation': 'CONTAINS',
                            'confidence': 0.8
                        })
        
        return relations
    
    def _extract_product_effect_relations(self, text: str, entities: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """提取产品-功效关系"""
        relations = []
        
        effects = entities.get('effects', [])
        categories = entities.get('categories', [])
        
        # 寻找功效关系词
        effect_patterns = [r'具有', r'能够', r'有效', r'帮助']
        
        for effect in effects:
            for category in categories:
                for pattern in effect_patterns:
                    if re.search(f'{category["text"]}.*{pattern}.*{effect["text"]}', text):
                        relations.append({
                            'source': category['text'],
                            'target': effect['text'],
                            'relation': 'HAS_EFFECT',
                            'confidence': 0.7
                        })
        
        return relations
    
    def _extract_product_skintype_relations(self, text: str, entities: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """提取产品-肤质关系"""
        relations = []
        
        skin_types = entities.get('skin_types', [])
        categories = entities.get('categories', [])
        
        # 寻找适用关系词
        suitable_patterns = [r'适合', r'适用于', r'专为.*设计']
        
        for skin_type in skin_types:
            for category in categories:
                for pattern in suitable_patterns:
                    if re.search(f'{category["text"]}.*{pattern}.*{skin_type["text"]}', text) or \
                       re.search(f'{pattern}.*{skin_type["text"]}.*{category["text"]}', text):
                        relations.append({
                            'source': category['text'],
                            'target': skin_type['text'],
                            'relation': 'SUITABLE_FOR',
                            'confidence': 0.7
                        })
        
        return relations
    
    def get_text_embedding(self, text: str) -> Optional[np.ndarray]:
        """获取文本的BERT嵌入向量"""
        if not self.bert_model or not self.bert_tokenizer:
            return None
        
        try:
            # 编码文本
            inputs = self.bert_tokenizer(text, return_tensors='pt', 
                                       truncation=True, max_length=512, 
                                       padding=True)
            
            # 获取嵌入
            with torch.no_grad():
                outputs = self.bert_model(**inputs)
                # 使用[CLS]标记的嵌入作为句子嵌入
                embeddings = outputs.last_hidden_state[:, 0, :].numpy()
            
            return embeddings[0]
            
        except Exception as e:
            logger.error(f"获取文本嵌入失败: {e}")
            return None
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """计算两个文本的相似度"""
        emb1 = self.get_text_embedding(text1)
        emb2 = self.get_text_embedding(text2)
        
        if emb1 is None or emb2 is None:
            return 0.0
        
        # 计算余弦相似度
        similarity = cosine_similarity([emb1], [emb2])[0][0]
        return float(similarity)
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """分析文本情感"""
        # 简单的情感分析实现
        positive_words = ['好', '棒', '喜欢', '推荐', '满意', '效果好', '值得']
        negative_words = ['差', '不好', '失望', '后悔', '过敏', '没效果', '不推荐']
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        if positive_count > negative_count:
            sentiment = 'positive'
            score = min(0.5 + positive_count * 0.1, 1.0)
        elif negative_count > positive_count:
            sentiment = 'negative'
            score = max(-0.5 - negative_count * 0.1, -1.0)
        else:
            sentiment = 'neutral'
            score = 0.0
        
        return {
            'sentiment': sentiment,
            'score': score,
            'positive_count': positive_count,
            'negative_count': negative_count
        }
    
    def process_review(self, review_text: str) -> Dict[str, Any]:
        """处理用户评论"""
        # 提取实体
        entities = self.extract_entities(review_text)
        
        # 提取关系
        relationships = self.extract_relationships(review_text, entities)
        
        # 情感分析
        sentiment = self.analyze_sentiment(review_text)
        
        return {
            'entities': entities,
            'relationships': relationships,
            'sentiment': sentiment,
            'processed_text': review_text
        }
