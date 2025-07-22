#!/usr/bin/env python3
"""
服务启动脚本
"""

import sys
import os
import subprocess
import time
from pathlib import Path
import argparse
from loguru import logger
import yaml


def load_config():
    """加载配置文件"""
    config_file = Path("config/config.yaml")
    if config_file.exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    return {}


def check_neo4j():
    """检查Neo4j服务状态"""
    try:
        import neo4j
        from neo4j import GraphDatabase
        
        config = load_config()
        neo4j_config = config.get('database', {}).get('neo4j', {})
        
        driver = GraphDatabase.driver(
            neo4j_config.get('uri', 'bolt://localhost:7687'),
            auth=(
                neo4j_config.get('username', 'neo4j'),
                neo4j_config.get('password', 'password')
            )
        )
        
        with driver.session() as session:
            session.run("RETURN 1")
        
        driver.close()
        logger.info("Neo4j服务运行正常")
        return True
        
    except Exception as e:
        logger.error(f"Neo4j服务连接失败: {e}")
        return False


def start_neo4j_docker():
    """使用Docker启动Neo4j"""
    logger.info("正在启动Neo4j Docker容器...")
    
    try:
        # 检查是否已有运行的容器
        result = subprocess.run(
            ["docker", "ps", "-q", "-f", "name=neo4j"],
            capture_output=True,
            text=True
        )
        
        if result.stdout.strip():
            logger.info("Neo4j容器已在运行")
            return True
        
        # 启动新容器
        cmd = [
            "docker", "run", "-d",
            "--name", "neo4j",
            "-p", "7474:7474",
            "-p", "7687:7687",
            "-e", "NEO4J_AUTH=neo4j/password",
            "-v", "neo4j_data:/data",
            "-v", "neo4j_logs:/logs",
            "neo4j:latest"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("Neo4j容器启动成功")
            # 等待服务启动
            logger.info("等待Neo4j服务启动...")
            time.sleep(30)
            return True
        else:
            logger.error(f"Neo4j容器启动失败: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"启动Neo4j Docker容器失败: {e}")
        return False


def start_mysql_docker():
    """使用Docker启动MySQL"""
    logger.info("正在启动MySQL Docker容器...")

    try:
        # 检查是否已有运行的容器
        result = subprocess.run(
            ["docker", "ps", "-q", "-f", "name=mysql"],
            capture_output=True,
            text=True
        )

        if result.stdout.strip():
            logger.info("MySQL容器已在运行")
            return True

        # 启动新容器
        cmd = [
            "docker", "run", "-d",
            "--name", "mysql",
            "-p", "3306:3306",
            "-e", "MYSQL_ROOT_PASSWORD=password",
            "-e", "MYSQL_DATABASE=cosmetic_data",
            "-v", "mysql_data:/var/lib/mysql",
            "mysql:8.0",
            "--default-authentication-plugin=mysql_native_password"
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            logger.info("MySQL容器启动成功")
            # MySQL需要更长时间启动
            logger.info("等待MySQL服务启动...")
            time.sleep(45)
            return True
        else:
            logger.error(f"MySQL容器启动失败: {result.stderr}")
            return False

    except Exception as e:
        logger.error(f"启动MySQL Docker容器失败: {e}")
        return False


def start_redis_docker():
    """使用Docker启动Redis"""
    logger.info("正在启动Redis Docker容器...")

    try:
        # 检查是否已有运行的容器
        result = subprocess.run(
            ["docker", "ps", "-q", "-f", "name=redis"],
            capture_output=True,
            text=True
        )

        if result.stdout.strip():
            logger.info("Redis容器已在运行")
            return True

        # 启动新容器
        cmd = [
            "docker", "run", "-d",
            "--name", "redis",
            "-p", "6379:6379",
            "redis:latest"
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            logger.info("Redis容器启动成功")
            time.sleep(5)
            return True
        else:
            logger.error(f"Redis容器启动失败: {result.stderr}")
            return False

    except Exception as e:
        logger.error(f"启动Redis Docker容器失败: {e}")
        return False


def start_api_server():
    """启动API服务器"""
    logger.info("正在启动API服务器...")
    
    try:
        # 切换到项目根目录
        os.chdir(Path(__file__).parent.parent)
        
        # 启动FastAPI服务器
        cmd = [
            sys.executable, "-m", "uvicorn",
            "src.api.app:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ]
        
        process = subprocess.Popen(cmd)
        logger.info(f"API服务器启动成功，PID: {process.pid}")
        
        # 等待服务启动
        time.sleep(5)
        
        return process
        
    except Exception as e:
        logger.error(f"启动API服务器失败: {e}")
        return None


def start_frontend():
    """启动前端服务"""
    logger.info("正在启动前端服务...")
    
    try:
        frontend_dir = Path(__file__).parent.parent / "src" / "visualization" / "frontend"
        
        if not frontend_dir.exists():
            logger.error("前端目录不存在")
            return None
        
        os.chdir(frontend_dir)
        
        # 检查是否已安装依赖
        if not (frontend_dir / "node_modules").exists():
            logger.info("正在安装前端依赖...")
            result = subprocess.run(["npm", "install"], capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"安装前端依赖失败: {result.stderr}")
                return None
        
        # 启动前端开发服务器
        cmd = ["npm", "start"]
        process = subprocess.Popen(cmd)
        logger.info(f"前端服务启动成功，PID: {process.pid}")
        
        return process
        
    except Exception as e:
        logger.error(f"启动前端服务失败: {e}")
        return None


def initialize_database():
    """初始化数据库"""
    logger.info("正在初始化数据库...")
    
    try:
        # 切换到项目根目录
        os.chdir(Path(__file__).parent.parent)
        
        # 运行数据库初始化脚本
        cmd = [sys.executable, "scripts/init_database.py"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("数据库初始化成功")
            return True
        else:
            logger.error(f"数据库初始化失败: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='化妆品知识图谱服务启动脚本')
    parser.add_argument('--skip-docker', action='store_true', help='跳过Docker服务启动')
    parser.add_argument('--skip-init', action='store_true', help='跳过数据库初始化')
    parser.add_argument('--api-only', action='store_true', help='仅启动API服务')
    parser.add_argument('--frontend-only', action='store_true', help='仅启动前端服务')
    
    args = parser.parse_args()
    
    logger.info("开始启动化妆品知识图谱系统...")
    
    processes = []
    
    try:
        # 启动Docker服务
        if not args.skip_docker and not args.frontend_only:
            if not check_neo4j():
                if not start_neo4j_docker():
                    logger.error("Neo4j启动失败，退出")
                    return
            
            if not start_mysql_docker():
                logger.error("MySQL启动失败，退出")
                return

            if not start_redis_docker():
                logger.warning("Redis启动失败，但系统可以继续运行")
        
        # 初始化数据库
        if not args.skip_init and not args.frontend_only:
            if check_neo4j():
                if not initialize_database():
                    logger.warning("数据库初始化失败，但系统可以继续运行")
            else:
                logger.warning("Neo4j未运行，跳过数据库初始化")
        
        # 启动API服务器
        if not args.frontend_only:
            api_process = start_api_server()
            if api_process:
                processes.append(api_process)
            else:
                logger.error("API服务器启动失败")
                return
        
        # 启动前端服务
        if not args.api_only:
            frontend_process = start_frontend()
            if frontend_process:
                processes.append(frontend_process)
            else:
                logger.warning("前端服务启动失败，但API服务仍可使用")
        
        logger.info("系统启动完成！")
        logger.info("API服务地址: http://localhost:8000")
        logger.info("API文档地址: http://localhost:8000/docs")
        if not args.api_only:
            logger.info("前端服务地址: http://localhost:3000")
        logger.info("Neo4j浏览器: http://localhost:7474")
        
        # 等待用户中断
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("收到中断信号，正在关闭服务...")
            
            # 终止所有进程
            for process in processes:
                try:
                    process.terminate()
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
            
            logger.info("所有服务已关闭")
    
    except Exception as e:
        logger.error(f"系统启动失败: {e}")
        
        # 清理进程
        for process in processes:
            try:
                process.terminate()
            except:
                pass


if __name__ == "__main__":
    main()
