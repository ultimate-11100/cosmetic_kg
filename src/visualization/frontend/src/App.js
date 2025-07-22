import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Layout, Menu, theme } from 'antd';
import {
  HomeOutlined,
  SearchOutlined,
  StarOutlined,
  BarChartOutlined,
  SafetyOutlined,
  ShopOutlined
} from '@ant-design/icons';

import HomePage from './pages/HomePage';
import SearchPage from './pages/SearchPage';
import RecommendationPage from './pages/RecommendationPage';
import AnalysisPage from './pages/AnalysisPage';
import SafetyPage from './pages/SafetyPage';
import ProductPage from './pages/ProductPage';
import KnowledgeGraphPage from './pages/KnowledgeGraphPage';

import './App.css';

const { Header, Content, Sider } = Layout;

const menuItems = [
  {
    key: '/',
    icon: <HomeOutlined />,
    label: '首页',
  },
  {
    key: '/search',
    icon: <SearchOutlined />,
    label: '产品搜索',
  },
  {
    key: '/recommendation',
    icon: <StarOutlined />,
    label: '个性化推荐',
  },
  {
    key: '/analysis',
    icon: <BarChartOutlined />,
    label: '数据分析',
  },
  {
    key: '/safety',
    icon: <SafetyOutlined />,
    label: '成分安全',
  },
  {
    key: '/knowledge-graph',
    icon: <ShopOutlined />,
    label: '知识图谱',
  },
];

function App() {
  const {
    token: { colorBgContainer },
  } = theme.useToken();

  const [selectedKey, setSelectedKey] = React.useState('/');

  return (
    <Router>
      <Layout style={{ minHeight: '100vh' }}>
        <Sider
          breakpoint="lg"
          collapsedWidth="0"
          onBreakpoint={(broken) => {
            console.log(broken);
          }}
          onCollapse={(collapsed, type) => {
            console.log(collapsed, type);
          }}
        >
          <div className="demo-logo-vertical" />
          <Menu
            theme="dark"
            mode="inline"
            selectedKeys={[selectedKey]}
            items={menuItems}
            onClick={({ key }) => {
              setSelectedKey(key);
              window.location.href = key;
            }}
          />
        </Sider>
        <Layout>
          <Header
            style={{
              padding: 0,
              background: colorBgContainer,
            }}
          >
            <div style={{ 
              padding: '0 24px', 
              fontSize: '20px', 
              fontWeight: 'bold',
              color: '#1890ff'
            }}>
              化妆品知识图谱系统
            </div>
          </Header>
          <Content
            style={{
              margin: '24px 16px',
              padding: 24,
              minHeight: 280,
              background: colorBgContainer,
            }}
          >
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/search" element={<SearchPage />} />
              <Route path="/recommendation" element={<RecommendationPage />} />
              <Route path="/analysis" element={<AnalysisPage />} />
              <Route path="/safety" element={<SafetyPage />} />
              <Route path="/product/:id" element={<ProductPage />} />
              <Route path="/knowledge-graph" element={<KnowledgeGraphPage />} />
            </Routes>
          </Content>
        </Layout>
      </Layout>
    </Router>
  );
}

export default App;
