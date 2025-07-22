"""
基于知识图谱的推荐系统
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from loguru import logger
import json
from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import networkx as nx
from collections import defaultdict
import random

from ..graph_database.neo4j_client import Neo4jClient
from ..graph_database.models import RecommendationResult, User, Product


class CosmeticRecommender:
    """化妆品推荐系统"""
    
    def __init__(self, neo4j_client: Neo4jClient):
        """初始化推荐系统"""
        self.neo4j_client = neo4j_client
        self.user_profiles = {}
        self.product_features = {}
        self.similarity_matrix = None
        self.graph = None
        self._initialize()
    
    def _initialize(self) -> None:
        """初始化推荐系统"""
        try:
            self._load_user_profiles()
            self._load_product_features()
            self._build_similarity_matrix()
            self._build_knowledge_graph()
            logger.info("推荐系统初始化完成")
        except Exception as e:
            logger.error(f"推荐系统初始化失败: {e}")
    
    def _load_user_profiles(self) -> None:
        """加载用户画像"""
        query = """
        MATCH (u:User)
        OPTIONAL MATCH (u)-[:PURCHASED]->(p:Product)
        RETURN u, collect(p) as purchased_products
        """
        
        results = self.neo4j_client.execute_query(query)
        
        for result in results:
            user_data = result['u']
            purchased_products = result['purchased_products']
            
            self.user_profiles[user_data['id']] = {
                'user_info': user_data,
                'purchased_products': [p['id'] for p in purchased_products],
                'preferences': self._extract_user_preferences(user_data, purchased_products)
            }
    
    def _extract_user_preferences(self, user_data: Dict, purchased_products: List[Dict]) -> Dict[str, Any]:
        """提取用户偏好"""
        preferences = {
            'preferred_categories': [],
            'preferred_brands': [],
            'preferred_price_range': None,
            'preferred_effects': [],
            'skin_concerns': user_data.get('skin_concerns', [])
        }
        
        if purchased_products:
            # 分析购买历史
            categories = [p.get('category') for p in purchased_products if p.get('category')]
            brands = [p.get('brand_id') for p in purchased_products if p.get('brand_id')]
            prices = [p.get('price') for p in purchased_products if p.get('price')]
            
            # 统计偏好类别
            category_counts = defaultdict(int)
            for cat in categories:
                category_counts[cat] += 1
            preferences['preferred_categories'] = sorted(category_counts.keys(), 
                                                       key=category_counts.get, reverse=True)[:3]
            
            # 统计偏好品牌
            brand_counts = defaultdict(int)
            for brand in brands:
                brand_counts[brand] += 1
            preferences['preferred_brands'] = sorted(brand_counts.keys(), 
                                                   key=brand_counts.get, reverse=True)[:3]
            
            # 计算价格偏好
            if prices:
                avg_price = np.mean(prices)
                preferences['preferred_price_range'] = {
                    'min': avg_price * 0.7,
                    'max': avg_price * 1.3
                }
        
        return preferences
    
    def _load_product_features(self) -> None:
        """加载产品特征"""
        query = """
        MATCH (p:Product)
        OPTIONAL MATCH (p)-[:CONTAINS]->(i:Ingredient)
        OPTIONAL MATCH (p)-[:HAS_EFFECT]->(e:Effect)
        OPTIONAL MATCH (b:Brand)-[:PRODUCES]->(p)
        RETURN p, collect(DISTINCT i.name) as ingredients, 
               collect(DISTINCT e.name) as effects,
               b.name as brand_name
        """
        
        results = self.neo4j_client.execute_query(query)
        
        for result in results:
            product = result['p']
            ingredients = result['ingredients']
            effects = result['effects']
            brand_name = result['brand_name']
            
            # 构建产品特征向量
            feature_text = ' '.join([
                product.get('name', ''),
                product.get('description', ''),
                ' '.join(ingredients),
                ' '.join(effects),
                brand_name or ''
            ])
            
            self.product_features[product['id']] = {
                'product_info': product,
                'ingredients': ingredients,
                'effects': effects,
                'brand_name': brand_name,
                'feature_text': feature_text,
                'category': product.get('category'),
                'price': product.get('price'),
                'rating': product.get('rating')
            }
    
    def _build_similarity_matrix(self) -> None:
        """构建产品相似度矩阵"""
        if not self.product_features:
            return
        
        # 使用TF-IDF计算文本相似度
        product_ids = list(self.product_features.keys())
        feature_texts = [self.product_features[pid]['feature_text'] for pid in product_ids]
        
        vectorizer = TfidfVectorizer(max_features=1000, stop_words=None)
        tfidf_matrix = vectorizer.fit_transform(feature_texts)
        
        # 计算余弦相似度
        similarity_matrix = cosine_similarity(tfidf_matrix)
        
        self.similarity_matrix = pd.DataFrame(
            similarity_matrix,
            index=product_ids,
            columns=product_ids
        )
    
    def _build_knowledge_graph(self) -> None:
        """构建知识图谱网络"""
        self.graph = nx.Graph()
        
        # 添加产品节点
        for product_id, features in self.product_features.items():
            self.graph.add_node(product_id, 
                              node_type='product',
                              **features['product_info'])
        
        # 添加相似度边
        if self.similarity_matrix is not None:
            for i, product_id1 in enumerate(self.similarity_matrix.index):
                for j, product_id2 in enumerate(self.similarity_matrix.columns):
                    if i < j:  # 避免重复边
                        similarity = self.similarity_matrix.iloc[i, j]
                        if similarity > 0.3:  # 相似度阈值
                            self.graph.add_edge(product_id1, product_id2, 
                                               weight=similarity, 
                                               edge_type='similar')
    
    def collaborative_filtering_recommend(self, user_id: str, n_recommendations: int = 10) -> List[RecommendationResult]:
        """协同过滤推荐"""
        if user_id not in self.user_profiles:
            return []
        
        user_profile = self.user_profiles[user_id]
        purchased_products = set(user_profile['purchased_products'])
        
        # 找到相似用户
        similar_users = self._find_similar_users(user_id)
        
        # 收集相似用户购买的产品
        candidate_products = defaultdict(float)
        
        for similar_user_id, similarity_score in similar_users[:10]:  # 取前10个相似用户
            similar_user_purchases = set(self.user_profiles[similar_user_id]['purchased_products'])
            
            # 找到该用户购买但目标用户未购买的产品
            new_products = similar_user_purchases - purchased_products
            
            for product_id in new_products:
                candidate_products[product_id] += similarity_score
        
        # 排序并返回推荐结果
        recommendations = []
        for product_id, score in sorted(candidate_products.items(), 
                                      key=lambda x: x[1], reverse=True)[:n_recommendations]:
            recommendations.append(RecommendationResult(
                product_id=product_id,
                score=score,
                reason="基于相似用户的购买行为",
                confidence=min(score, 1.0)
            ))
        
        return recommendations
    
    def content_based_recommend(self, user_id: str, n_recommendations: int = 10) -> List[RecommendationResult]:
        """基于内容的推荐"""
        if user_id not in self.user_profiles:
            return []
        
        user_profile = self.user_profiles[user_id]
        purchased_products = set(user_profile['purchased_products'])
        preferences = user_profile['preferences']
        
        candidate_products = []
        
        for product_id, features in self.product_features.items():
            if product_id in purchased_products:
                continue
            
            score = self._calculate_content_score(features, preferences)
            
            if score > 0.3:  # 分数阈值
                candidate_products.append((product_id, score))
        
        # 排序并返回推荐结果
        recommendations = []
        for product_id, score in sorted(candidate_products, 
                                      key=lambda x: x[1], reverse=True)[:n_recommendations]:
            recommendations.append(RecommendationResult(
                product_id=product_id,
                score=score,
                reason="基于用户偏好和产品特征匹配",
                confidence=score
            ))
        
        return recommendations
    
    def knowledge_graph_recommend(self, user_id: str, n_recommendations: int = 10) -> List[RecommendationResult]:
        """基于知识图谱的推荐"""
        if user_id not in self.user_profiles or not self.graph:
            return []
        
        user_profile = self.user_profiles[user_id]
        purchased_products = user_profile['purchased_products']
        
        # 使用随机游走算法
        candidate_scores = defaultdict(float)
        
        for seed_product in purchased_products:
            if seed_product in self.graph:
                # 从用户购买的产品开始随机游走
                walk_scores = self._random_walk(seed_product, walk_length=10, num_walks=50)
                
                for product_id, score in walk_scores.items():
                    if product_id not in purchased_products:
                        candidate_scores[product_id] += score
        
        # 排序并返回推荐结果
        recommendations = []
        for product_id, score in sorted(candidate_scores.items(), 
                                      key=lambda x: x[1], reverse=True)[:n_recommendations]:
            recommendations.append(RecommendationResult(
                product_id=product_id,
                score=score / len(purchased_products),  # 归一化
                reason="基于知识图谱的产品关联分析",
                confidence=min(score / len(purchased_products), 1.0)
            ))
        
        return recommendations
    
    def hybrid_recommend(self, user_id: str, n_recommendations: int = 10) -> List[RecommendationResult]:
        """混合推荐算法"""
        # 获取不同算法的推荐结果
        cf_recommendations = self.collaborative_filtering_recommend(user_id, n_recommendations)
        cb_recommendations = self.content_based_recommend(user_id, n_recommendations)
        kg_recommendations = self.knowledge_graph_recommend(user_id, n_recommendations)
        
        # 合并和加权
        combined_scores = defaultdict(float)
        combined_reasons = {}
        combined_confidence = {}
        
        # 协同过滤权重: 0.4
        for rec in cf_recommendations:
            combined_scores[rec.product_id] += rec.score * 0.4
            combined_reasons[rec.product_id] = rec.reason
            combined_confidence[rec.product_id] = rec.confidence * 0.4
        
        # 基于内容权重: 0.3
        for rec in cb_recommendations:
            combined_scores[rec.product_id] += rec.score * 0.3
            if rec.product_id in combined_reasons:
                combined_reasons[rec.product_id] += f"; {rec.reason}"
            else:
                combined_reasons[rec.product_id] = rec.reason
            combined_confidence[rec.product_id] += rec.confidence * 0.3
        
        # 知识图谱权重: 0.3
        for rec in kg_recommendations:
            combined_scores[rec.product_id] += rec.score * 0.3
            if rec.product_id in combined_reasons:
                combined_reasons[rec.product_id] += f"; {rec.reason}"
            else:
                combined_reasons[rec.product_id] = rec.reason
            combined_confidence[rec.product_id] += rec.confidence * 0.3
        
        # 排序并返回最终推荐结果
        final_recommendations = []
        for product_id, score in sorted(combined_scores.items(), 
                                      key=lambda x: x[1], reverse=True)[:n_recommendations]:
            final_recommendations.append(RecommendationResult(
                product_id=product_id,
                score=score,
                reason=combined_reasons.get(product_id, "混合推荐算法"),
                confidence=combined_confidence.get(product_id, 0.5)
            ))
        
        return final_recommendations
    
    def _find_similar_users(self, user_id: str) -> List[Tuple[str, float]]:
        """找到相似用户"""
        target_user = self.user_profiles[user_id]
        target_purchases = set(target_user['purchased_products'])
        
        similar_users = []
        
        for other_user_id, other_profile in self.user_profiles.items():
            if other_user_id == user_id:
                continue
            
            other_purchases = set(other_profile['purchased_products'])
            
            # 计算Jaccard相似度
            intersection = len(target_purchases & other_purchases)
            union = len(target_purchases | other_purchases)
            
            if union > 0:
                similarity = intersection / union
                if similarity > 0.1:  # 相似度阈值
                    similar_users.append((other_user_id, similarity))
        
        return sorted(similar_users, key=lambda x: x[1], reverse=True)
    
    def _calculate_content_score(self, product_features: Dict, user_preferences: Dict) -> float:
        """计算基于内容的推荐分数"""
        score = 0.0
        
        # 类别匹配
        if product_features['category'] in user_preferences['preferred_categories']:
            score += 0.3
        
        # 品牌匹配
        if product_features['brand_name'] in user_preferences['preferred_brands']:
            score += 0.2
        
        # 价格匹配
        price_range = user_preferences.get('preferred_price_range')
        if price_range and product_features['price']:
            if price_range['min'] <= product_features['price'] <= price_range['max']:
                score += 0.2
        
        # 功效匹配
        product_effects = set(product_features['effects'])
        user_concerns = set(user_preferences['skin_concerns'])
        
        # 简单的功效-问题匹配逻辑
        effect_concern_mapping = {
            '保湿': ['干燥', '缺水'],
            '控油': ['出油', '油腻'],
            '美白': ['暗沉', '色斑'],
            '抗衰老': ['细纹', '松弛'],
            '祛痘': ['痘痘', '粉刺']
        }
        
        for effect in product_effects:
            if effect in effect_concern_mapping:
                mapped_concerns = set(effect_concern_mapping[effect])
                if mapped_concerns & user_concerns:
                    score += 0.3
                    break
        
        return min(score, 1.0)
    
    def _random_walk(self, start_node: str, walk_length: int = 10, num_walks: int = 50) -> Dict[str, float]:
        """随机游走算法"""
        node_scores = defaultdict(float)
        
        for _ in range(num_walks):
            current_node = start_node
            
            for step in range(walk_length):
                neighbors = list(self.graph.neighbors(current_node))
                if not neighbors:
                    break
                
                # 根据边权重选择下一个节点
                weights = [self.graph[current_node][neighbor].get('weight', 1.0) 
                          for neighbor in neighbors]
                
                # 加权随机选择
                total_weight = sum(weights)
                if total_weight == 0:
                    next_node = random.choice(neighbors)
                else:
                    rand_val = random.uniform(0, total_weight)
                    cumsum = 0
                    next_node = neighbors[-1]  # 默认值
                    for i, weight in enumerate(weights):
                        cumsum += weight
                        if rand_val <= cumsum:
                            next_node = neighbors[i]
                            break
                
                # 记录访问分数（距离越远分数越低）
                node_scores[next_node] += 1.0 / (step + 1)
                current_node = next_node
        
        return dict(node_scores)
    
    def get_product_recommendations_by_skin_type(self, skin_type: str, n_recommendations: int = 10) -> List[RecommendationResult]:
        """根据肤质推荐产品"""
        query = """
        MATCH (p:Product)-[:SUITABLE_FOR]->(s:SkinType {name: $skin_type})
        RETURN p
        ORDER BY p.rating DESC, p.review_count DESC
        LIMIT $limit
        """
        
        results = self.neo4j_client.execute_query(query, {
            'skin_type': skin_type,
            'limit': n_recommendations
        })
        
        recommendations = []
        for result in results:
            product = result['p']
            recommendations.append(RecommendationResult(
                product_id=product['id'],
                score=product.get('rating', 0) / 5.0,  # 归一化评分
                reason=f"适合{skin_type}肌肤",
                confidence=0.8
            ))
        
        return recommendations
