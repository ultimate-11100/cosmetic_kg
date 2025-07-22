import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Statistic, Typography, List, Avatar, Tag, Spin } from 'antd';
import { 
  ShopOutlined, 
  StarOutlined, 
  SafetyOutlined, 
  BarChartOutlined,
  TrophyOutlined,
  HeartOutlined
} from '@ant-design/icons';
import ReactECharts from 'echarts-for-react';
import { getSystemStats, getPopularProducts, getRecentAnalysis } from '../services/api';

const { Title, Paragraph } = Typography;

const HomePage = () => {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({});
  const [popularProducts, setPopularProducts] = useState([]);
  const [recentAnalysis, setRecentAnalysis] = useState([]);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      
      // 模拟数据加载
      setTimeout(() => {
        setStats({
          totalProducts: 15420,
          totalBrands: 856,
          totalIngredients: 2341,
          totalUsers: 8967
        });
        
        setPopularProducts([
          {
            id: '1',
            name: 'SK-II 神仙水',
            brand: 'SK-II',
            rating: 4.8,
            price: 1299,
            image: '/api/placeholder/80/80'
          },
          {
            id: '2',
            name: '兰蔻小黑瓶精华',
            brand: '兰蔻',
            rating: 4.7,
            price: 899,
            image: '/api/placeholder/80/80'
          },
          {
            id: '3',
            name: '雅诗兰黛小棕瓶',
            brand: '雅诗兰黛',
            rating: 4.6,
            price: 799,
            image: '/api/placeholder/80/80'
          }
        ]);
        
        setRecentAnalysis([
          {
            type: '成分安全分析',
            product: 'SK-II 神仙水',
            result: '安全等级: 高',
            time: '2小时前'
          },
          {
            type: '品牌竞争分析',
            product: '兰蔻品牌',
            result: '市场地位: 领先',
            time: '4小时前'
          },
          {
            type: '用户偏好分析',
            product: '护肤类产品',
            result: '保湿功效最受欢迎',
            time: '6小时前'
          }
        ]);
        
        setLoading(false);
      }, 1000);
      
    } catch (error) {
      console.error('加载数据失败:', error);
      setLoading(false);
    }
  };

  // 品牌分布图表配置
  const brandChartOption = {
    title: {
      text: '热门品牌分布',
      left: 'center'
    },
    tooltip: {
      trigger: 'item'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [
      {
        name: '产品数量',
        type: 'pie',
        radius: '50%',
        data: [
          { value: 1048, name: '兰蔻' },
          { value: 735, name: '雅诗兰黛' },
          { value: 580, name: 'SK-II' },
          { value: 484, name: '迪奥' },
          { value: 300, name: '香奈儿' }
        ],
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  };

  // 价格分布图表配置
  const priceChartOption = {
    title: {
      text: '产品价格分布',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      data: ['0-100', '100-300', '300-500', '500-1000', '1000+']
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        data: [2340, 4560, 3210, 2890, 1420],
        type: 'bar',
        itemStyle: {
          color: '#1890ff'
        }
      }
    ]
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div>
      <Title level={2}>系统概览</Title>
      <Paragraph>
        欢迎使用化妆品知识图谱系统！这里为您提供全面的化妆品数据分析、个性化推荐和成分安全评估服务。
      </Paragraph>

      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card>
            <Statistic
              title="产品总数"
              value={stats.totalProducts}
              prefix={<ShopOutlined />}
              valueStyle={{ color: '#3f8600' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="品牌总数"
              value={stats.totalBrands}
              prefix={<TrophyOutlined />}
              valueStyle={{ color: '#cf1322' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="成分总数"
              value={stats.totalIngredients}
              prefix={<SafetyOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic
              title="用户总数"
              value={stats.totalUsers}
              prefix={<HeartOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={16}>
        {/* 热门产品 */}
        <Col span={8}>
          <Card title="热门产品" extra={<StarOutlined />}>
            <List
              itemLayout="horizontal"
              dataSource={popularProducts}
              renderItem={(item) => (
                <List.Item>
                  <List.Item.Meta
                    avatar={<Avatar src={item.image} />}
                    title={
                      <div>
                        {item.name}
                        <Tag color="gold" style={{ marginLeft: 8 }}>
                          {item.rating}★
                        </Tag>
                      </div>
                    }
                    description={
                      <div>
                        <div>{item.brand}</div>
                        <div style={{ color: '#f50' }}>¥{item.price}</div>
                      </div>
                    }
                  />
                </List.Item>
              )}
            />
          </Card>
        </Col>

        {/* 品牌分布图 */}
        <Col span={8}>
          <Card title="品牌分布" extra={<BarChartOutlined />}>
            <ReactECharts 
              option={brandChartOption} 
              style={{ height: '300px' }}
            />
          </Card>
        </Col>

        {/* 价格分布图 */}
        <Col span={8}>
          <Card title="价格分布" extra={<BarChartOutlined />}>
            <ReactECharts 
              option={priceChartOption} 
              style={{ height: '300px' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 最近分析 */}
      <Row style={{ marginTop: 16 }}>
        <Col span={24}>
          <Card title="最近分析" extra={<BarChartOutlined />}>
            <List
              itemLayout="horizontal"
              dataSource={recentAnalysis}
              renderItem={(item) => (
                <List.Item>
                  <List.Item.Meta
                    title={item.type}
                    description={
                      <div>
                        <div><strong>分析对象:</strong> {item.product}</div>
                        <div><strong>分析结果:</strong> {item.result}</div>
                        <div style={{ color: '#999' }}>{item.time}</div>
                      </div>
                    }
                  />
                </List.Item>
              )}
            />
          </Card>
        </Col>
      </Row>

      {/* 功能介绍 */}
      <Row gutter={16} style={{ marginTop: 24 }}>
        <Col span={8}>
          <Card
            title="智能推荐"
            extra={<StarOutlined />}
            hoverable
            onClick={() => window.location.href = '/recommendation'}
          >
            <p>基于用户画像和产品特征的个性化推荐系统，帮助用户找到最适合的化妆品。</p>
          </Card>
        </Col>
        <Col span={8}>
          <Card
            title="成分安全"
            extra={<SafetyOutlined />}
            hoverable
            onClick={() => window.location.href = '/safety'}
          >
            <p>全面的成分安全性分析，包括过敏原检测、孕妇适用性评估等。</p>
          </Card>
        </Col>
        <Col span={8}>
          <Card
            title="数据分析"
            extra={<BarChartOutlined />}
            hoverable
            onClick={() => window.location.href = '/analysis'}
          >
            <p>深度的市场分析和品牌竞争分析，为商业决策提供数据支持。</p>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default HomePage;
