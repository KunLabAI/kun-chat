# Vue 3 + Vite

This template should help get you started developing with Vue 3 in Vite. The template uses Vue 3 `<script setup>` SFCs, check out the [script setup docs](https://v3.vuejs.org/api/sfc-script-setup.html#sfc-script-setup) to learn more.

Learn more about IDE Support for Vue in the [Vue Docs Scaling up Guide](https://vuejs.org/guide/scaling-up/tooling.html#ide-support).

## 项目特性

- 多模型支持
- 实时对话（WebSocket）
- 对话历史记录
- 流式响应
- 模型管理功能
- 提示词库管理
- 用户认证系统

## 环境要求

- Node.js 16.14.0+
- Electron 28.1.0 

## 安装步骤

1. 克隆项目到本地
2. 安装依赖
```bash
npm install
```
3. 启动开发服务器
```bash
npm run dev
```
4. 启动Electron
```bash
npm run electron:dev
```

## API文档

启动后端服务后访问 http://localhost:8000/docs 查看完整的API文档

## 目录结构

```
frontend/
├── src/
│   ├── assets/
│   ├── components/
│   ├── pages/
│   ├── router/
│   ├── store/
│   ├── utils/
│   └── views/
├── public/
├── package.json
├── vite.config.js
└── README.md
```

## 使用说明

1. 确保后端服务已经启动并可访问
2. 启动前端开发服务器
3. 启动Electron
4. 访问 http://localhost:5173 查看应用

## 开发说明

- 使用Vue 3 + Vite开发
- 采用WebSocket实现实时通信
- 数据存储使用JSON文件
- 支持JWT认证

## 注意事项

- 生产环境部署前请修改.env中的密钥
- 确保数据目录具有正确的读写权限
- 建议在虚拟环境中运行项目