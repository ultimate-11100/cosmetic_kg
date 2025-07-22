"""
基础爬虫类
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional
import time
import random
from abc import ABC, abstractmethod
from loguru import logger
import json
from urllib.parse import urljoin, urlparse
import yaml
from pathlib import Path


class BaseCrawler(ABC):
    """基础爬虫抽象类"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """初始化爬虫"""
        self.config = self._load_config(config_path)
        self.session = requests.Session()
        self._setup_session()
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        config_file = Path(config_path)
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            return config.get('data_collection', {})
        return {}
    
    def _setup_session(self) -> None:
        """设置请求会话"""
        user_agents = self.config.get('scrapy', {}).get('user_agents', [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        ])
        
        self.session.headers.update({
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def get_page(self, url: str, **kwargs) -> Optional[requests.Response]:
        """获取页面内容"""
        try:
            # 添加随机延迟
            delay = self.config.get('scrapy', {}).get('download_delay', 1)
            randomize = self.config.get('scrapy', {}).get('randomize_download_delay', 0.5)
            sleep_time = delay + random.uniform(0, randomize)
            time.sleep(sleep_time)
            
            response = self.session.get(url, timeout=30, **kwargs)
            response.raise_for_status()
            
            logger.info(f"成功获取页面: {url}")
            return response
            
        except requests.RequestException as e:
            logger.error(f"获取页面失败: {url}, 错误: {e}")
            return None
    
    def parse_html(self, html_content: str) -> BeautifulSoup:
        """解析HTML内容"""
        return BeautifulSoup(html_content, 'html.parser')
    
    def save_data(self, data: List[Dict[str, Any]], filename: str) -> None:
        """保存数据到文件"""
        output_dir = Path("data/raw")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / filename
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"数据已保存到: {output_file}")
    
    @abstractmethod
    def crawl_products(self, **kwargs) -> List[Dict[str, Any]]:
        """爬取产品数据 - 子类必须实现"""
        pass
    
    @abstractmethod
    def crawl_brands(self, **kwargs) -> List[Dict[str, Any]]:
        """爬取品牌数据 - 子类必须实现"""
        pass


class SephoraCrawler(BaseCrawler):
    """Sephora爬虫"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        super().__init__(config_path)
        self.base_url = self.config.get('sources', {}).get('sephora', {}).get('base_url', 'https://www.sephora.com')
    
    def crawl_products(self, category: str = "skincare", limit: int = 100) -> List[Dict[str, Any]]:
        """爬取Sephora产品数据"""
        products = []
        
        # 构建搜索URL
        search_url = f"{self.base_url}/shop/{category}"
        
        try:
            response = self.get_page(search_url)
            if not response:
                return products
            
            soup = self.parse_html(response.text)
            
            # 解析产品列表
            product_items = soup.find_all('div', class_='ProductTile')
            
            for item in product_items[:limit]:
                product_data = self._parse_product_item(item)
                if product_data:
                    products.append(product_data)
            
            logger.info(f"成功爬取 {len(products)} 个Sephora产品")
            
        except Exception as e:
            logger.error(f"爬取Sephora产品失败: {e}")
        
        return products
    
    def _parse_product_item(self, item) -> Optional[Dict[str, Any]]:
        """解析单个产品项"""
        try:
            # 提取产品信息
            name_elem = item.find('span', class_='ProductTile-name')
            brand_elem = item.find('span', class_='ProductTile-brand')
            price_elem = item.find('span', class_='ProductTile-price')
            rating_elem = item.find('div', class_='Rating')
            image_elem = item.find('img')
            
            product_data = {
                'name': name_elem.get_text(strip=True) if name_elem else '',
                'brand': brand_elem.get_text(strip=True) if brand_elem else '',
                'price': self._extract_price(price_elem.get_text(strip=True)) if price_elem else None,
                'rating': self._extract_rating(rating_elem) if rating_elem else None,
                'image_url': image_elem.get('src') if image_elem else '',
                'source': 'sephora'
            }
            
            return product_data
            
        except Exception as e:
            logger.error(f"解析产品项失败: {e}")
            return None
    
    def _extract_price(self, price_text: str) -> Optional[float]:
        """提取价格"""
        try:
            # 移除货币符号和其他字符，提取数字
            import re
            price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
            if price_match:
                return float(price_match.group())
        except:
            pass
        return None
    
    def _extract_rating(self, rating_elem) -> Optional[float]:
        """提取评分"""
        try:
            # 从星级评分中提取数值
            stars = rating_elem.find_all('span', class_='Rating-star--filled')
            return len(stars) if stars else None
        except:
            return None
    
    def crawl_brands(self, **kwargs) -> List[Dict[str, Any]]:
        """爬取品牌数据"""
        brands = []
        
        brands_url = f"{self.base_url}/brands"
        
        try:
            response = self.get_page(brands_url)
            if not response:
                return brands
            
            soup = self.parse_html(response.text)
            
            # 解析品牌列表
            brand_items = soup.find_all('a', class_='BrandTile')
            
            for item in brand_items:
                brand_data = self._parse_brand_item(item)
                if brand_data:
                    brands.append(brand_data)
            
            logger.info(f"成功爬取 {len(brands)} 个Sephora品牌")
            
        except Exception as e:
            logger.error(f"爬取Sephora品牌失败: {e}")
        
        return brands
    
    def _parse_brand_item(self, item) -> Optional[Dict[str, Any]]:
        """解析单个品牌项"""
        try:
            name_elem = item.find('span', class_='BrandTile-name')
            logo_elem = item.find('img')
            
            brand_data = {
                'name': name_elem.get_text(strip=True) if name_elem else '',
                'logo_url': logo_elem.get('src') if logo_elem else '',
                'url': item.get('href', ''),
                'source': 'sephora'
            }
            
            return brand_data
            
        except Exception as e:
            logger.error(f"解析品牌项失败: {e}")
            return None


class TmallCrawler(BaseCrawler):
    """天猫爬虫"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        super().__init__(config_path)
        self.base_url = self.config.get('sources', {}).get('tmall', {}).get('base_url', 'https://www.tmall.com')
    
    def crawl_products(self, keyword: str = "护肤品", limit: int = 100) -> List[Dict[str, Any]]:
        """爬取天猫产品数据"""
        products = []
        
        # 构建搜索URL
        search_url = f"{self.base_url}/search.htm"
        params = {
            'q': keyword,
            'sort': 's',  # 按销量排序
        }
        
        try:
            response = self.get_page(search_url, params=params)
            if not response:
                return products
            
            soup = self.parse_html(response.text)
            
            # 解析产品列表
            product_items = soup.find_all('div', class_='product-item')
            
            for item in product_items[:limit]:
                product_data = self._parse_tmall_product(item)
                if product_data:
                    products.append(product_data)
            
            logger.info(f"成功爬取 {len(products)} 个天猫产品")
            
        except Exception as e:
            logger.error(f"爬取天猫产品失败: {e}")
        
        return products
    
    def _parse_tmall_product(self, item) -> Optional[Dict[str, Any]]:
        """解析天猫产品项"""
        try:
            # 天猫页面结构可能需要根据实际情况调整
            title_elem = item.find('a', class_='product-title')
            price_elem = item.find('span', class_='price')
            shop_elem = item.find('a', class_='shop-name')
            
            product_data = {
                'name': title_elem.get_text(strip=True) if title_elem else '',
                'price': self._extract_price(price_elem.get_text(strip=True)) if price_elem else None,
                'shop': shop_elem.get_text(strip=True) if shop_elem else '',
                'source': 'tmall'
            }
            
            return product_data
            
        except Exception as e:
            logger.error(f"解析天猫产品项失败: {e}")
            return None
    
    def crawl_brands(self, **kwargs) -> List[Dict[str, Any]]:
        """爬取天猫品牌数据"""
        # 天猫品牌爬取逻辑
        return []


class CrawlerManager:
    """爬虫管理器"""
    
    def __init__(self):
        self.crawlers = {
            'sephora': SephoraCrawler(),
            'tmall': TmallCrawler(),
        }
    
    def crawl_all_sources(self, data_type: str = 'products', **kwargs) -> Dict[str, List[Dict[str, Any]]]:
        """从所有数据源爬取数据"""
        results = {}
        
        for source_name, crawler in self.crawlers.items():
            try:
                if data_type == 'products':
                    data = crawler.crawl_products(**kwargs)
                elif data_type == 'brands':
                    data = crawler.crawl_brands(**kwargs)
                else:
                    continue
                
                results[source_name] = data
                
                # 保存数据
                filename = f"{source_name}_{data_type}_{int(time.time())}.json"
                crawler.save_data(data, filename)
                
            except Exception as e:
                logger.error(f"从 {source_name} 爬取数据失败: {e}")
                results[source_name] = []
        
        return results
