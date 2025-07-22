#!/usr/bin/env python3
"""
数据采集脚本
"""

import sys
import os
from pathlib import Path
import argparse
from loguru import logger

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.data_collection.base_crawler import CrawlerManager


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='化妆品数据采集脚本')
    parser.add_argument('--source', type=str, choices=['sephora', 'tmall', 'all'], 
                       default='all', help='数据源选择')
    parser.add_argument('--type', type=str, choices=['products', 'brands', 'all'], 
                       default='products', help='数据类型')
    parser.add_argument('--limit', type=int, default=100, help='采集数量限制')
    parser.add_argument('--category', type=str, default='skincare', help='产品类别')
    parser.add_argument('--keyword', type=str, default='护肤品', help='搜索关键词')
    
    args = parser.parse_args()
    
    logger.info(f"开始数据采集 - 源: {args.source}, 类型: {args.type}, 限制: {args.limit}")
    
    try:
        crawler_manager = CrawlerManager()
        
        if args.source == 'all':
            # 从所有数据源采集
            if args.type == 'products':
                results = crawler_manager.crawl_all_sources(
                    data_type='products',
                    category=args.category,
                    keyword=args.keyword,
                    limit=args.limit
                )
            elif args.type == 'brands':
                results = crawler_manager.crawl_all_sources(
                    data_type='brands',
                    limit=args.limit
                )
            else:  # all
                product_results = crawler_manager.crawl_all_sources(
                    data_type='products',
                    category=args.category,
                    keyword=args.keyword,
                    limit=args.limit
                )
                brand_results = crawler_manager.crawl_all_sources(
                    data_type='brands',
                    limit=args.limit
                )
                results = {
                    'products': product_results,
                    'brands': brand_results
                }
        else:
            # 从指定数据源采集
            crawler = crawler_manager.crawlers.get(args.source)
            if not crawler:
                logger.error(f"不支持的数据源: {args.source}")
                return
            
            if args.type == 'products':
                if args.source == 'sephora':
                    data = crawler.crawl_products(category=args.category, limit=args.limit)
                elif args.source == 'tmall':
                    data = crawler.crawl_products(keyword=args.keyword, limit=args.limit)
                else:
                    data = crawler.crawl_products(limit=args.limit)
                
                results = {args.source: data}
            elif args.type == 'brands':
                data = crawler.crawl_brands(limit=args.limit)
                results = {args.source: data}
            else:  # all
                if args.source == 'sephora':
                    products = crawler.crawl_products(category=args.category, limit=args.limit)
                elif args.source == 'tmall':
                    products = crawler.crawl_products(keyword=args.keyword, limit=args.limit)
                else:
                    products = crawler.crawl_products(limit=args.limit)
                
                brands = crawler.crawl_brands(limit=args.limit)
                results = {
                    'products': {args.source: products},
                    'brands': {args.source: brands}
                }
        
        # 统计结果
        total_items = 0
        if isinstance(results, dict):
            for source, data in results.items():
                if isinstance(data, list):
                    total_items += len(data)
                elif isinstance(data, dict):
                    for sub_source, sub_data in data.items():
                        if isinstance(sub_data, list):
                            total_items += len(sub_data)
        
        logger.info(f"数据采集完成，共采集 {total_items} 条数据")
        
    except Exception as e:
        logger.error(f"数据采集失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
