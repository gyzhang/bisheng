# BISHENG 本地开发环境搭建指南

本指南将帮助你快速在本地搭建 BISHENG 开发环境。

## 📋 目录

- [环境要求](#环境要求)
- [架构概述](#架构概述)
- [快速开始](#快速开始)
- [开发工具脚本](#开发工具脚本)
- [服务管理](#服务管理)
- [日志查看](#日志查看)
- [常见问题](#常见问题)

---

## 🛠 环境要求

### 必需软件

1. **Python 3.10+**
   - 推荐使用 conda 管理虚拟环境
   - 虚拟环境名称：`bisheng`

2. **Node.js 16+**
   - 用于运行前端项目
   - npm 8+

3. **Docker & Docker Compose**
   - 用于运行依赖服务（MySQL、Redis、Milvus 等）

4. **ffmpeg**
   - 音频处理工具（ASR 功能必需）
   - macOS: `brew install ffmpeg`

### 依赖服务端口

| 服务 | 端口 | 说明 |
|------|------|------|
| MySQL | 3306 | 数据库 |
| Redis | 6379 | 缓存 |
| Elasticsearch | 9200 | 搜索引擎 |
| Milvus | 19530 | 向量数据库 |
| MinIO | 9100 | 对象存储 |
| Backend API | 7860 | 后端服务 |
| Platform 前端 | 3001 | 管理后台 |
| Client 前端 | 4001 | 用户界面 |

---

## 🏗 架构概述

### 项目结构

```
bisheng/
├── docker/              # Docker 配置和数据
│   ├── docker-compose.yml    # 依赖服务编排
│   ├── mysql/                # MySQL 配置
│   ├── redis/                # Redis 配置
│   └── ...
├── scripts/             # 开发工具脚本
│   ├── dev_start.sh          # 启动开发服务
│   ├── dev_stop.sh           # 停止开发服务
│   └── dev_restart.sh        # 重启开发服务
├── src/
│   ├── backend/         # Python 后端
│   │   ├── bisheng/          # 主应用
│   │   └── pyproject.toml    # Python 依赖
│   └── frontend/        # React 前端
│       ├── platform/         # 管理后台
│       └── client/           # 用户界面
└── logs/                # 日志文件（自动创建）
```

### 技术栈

**后端**
- Python 3.10+
- FastAPI + Uvicorn
- Celery（异步任务）
- SQLAlchemy（ORM）
- MySQL + Redis + Milvus

**前端**
- React + TypeScript
- Vite
- 双前端架构（Platform + Client）

---

## 🚀 快速开始

### 步骤 1：启动 Docker 依赖服务

```bash
# 进入项目根目录
cd /path/to/bisheng

# 启动所有依赖服务（MySQL, Redis, Milvus 等）
docker-compose -p bisheng up -d

# 查看 Docker 服务状态
docker-compose -p bisheng ps
```

### 步骤 2：配置 Python 环境

```bash
# 创建并激活 conda 虚拟环境
conda create -n bisheng python=3.10
conda activate bisheng

# 安装后端依赖
cd src/backend
uv pip install -e . --system

# 验证安装
python -c "import bisheng"
```

### 步骤 3：启动开发服务

```bash
# 方式 1：启动所有服务（后端 + 双前端）
./scripts/dev_start.sh

# 方式 2：只启动后端
./scripts/dev_start.sh -s backend

# 方式 3：只启动前端
./scripts/dev_start.sh -s frontend
```

### 步骤 4：访问应用

启动成功后，你可以访问：

- **管理后台（Platform）**：http://localhost:3001/
  - 登录：http://localhost:3001/admin/login
  
- **用户界面（Client）**：http://localhost:4001/workspace/
  - 登录：http://localhost:4001/workspace/admin/login

- **后端 API**：http://localhost:7860
  - Swagger UI：http://localhost:7860/docs

- **默认账号**：
  - 邮箱：xprogrammer@163.com
  - 密码：good@Man2026

---

## 🛠 开发工具脚本

### dev_start.sh - 启动服务

```bash
# 启动所有服务
./scripts/dev_start.sh

# 只启动后端（Backend API + Celery Worker + Celery Beat）
./scripts/dev_start.sh -s backend

# 只启动前端（Platform + Client）
./scripts/dev_start.sh -s frontend

# 查看帮助
./scripts/dev_start.sh -h
```

**后端包含三个进程：**
1. Backend API - FastAPI 应用
2. Celery Worker - 异步任务处理器
3. Celery Beat - 定时任务调度器

### dev_stop.sh - 停止服务

```bash
# 停止所有服务
./scripts/dev_stop.sh

# 只停止后端
./scripts/dev_stop.sh -s backend

# 只停止前端
./scripts/dev_stop.sh -s frontend

# 查看帮助
./scripts/dev_stop.sh -h
```

### dev_restart.sh - 重启服务

```bash
# 重启所有服务
./scripts/dev_restart.sh

# 只重启后端
./scripts/dev_restart.sh -s backend

# 只重启前端
./scripts/dev_restart.sh -s frontend
```

---

## 📊 服务管理

### 查看服务状态

```bash
# 检查端口占用
lsof -i :7860  # 后端
lsof -i :3001  # Platform 前端
lsof -i :4001  # Client 前端

# 查看 Docker 服务
docker-compose -p bisheng ps
```

### 手动清理进程

如果脚本未能正常停止服务，可以手动清理：

```bash
# 清理端口占用
lsof -ti:7860 | xargs kill -9
lsof -ti:3001 | xargs kill -9
lsof -ti:4001 | xargs kill -9
```

### 停止 Docker 服务

```bash
# 停止所有 Docker 服务
docker-compose -p bisheng down

# 停止并删除数据卷（谨慎使用！）
docker-compose -p bisheng down -v
```

---

## 🔧 重要脚本：patch_code.sh

### 作用说明

`src/backend/patch_code.sh` 用于在**本地开发环境**中应用 langchain_openai 库的补丁，使其支持 `reasoning_content` 字段（AI 模型的推理思考过程内容）。

### 为什么需要这个补丁？

- **Docker 生产环境**：Dockerfile 构建时会自动应用补丁（`RUN patch -p1 < ...`）
- **本地开发环境**：使用 conda 虚拟环境，不会自动应用补丁，需要手动执行

### 何时需要执行？

#### ✅ 必须执行的情况：

1. **初次设置开发环境**
   ```bash
   # 安装依赖后
   uv pip install -e . --system
   bash src/backend/patch_code.sh bisheng
   ```

2. **重新安装依赖后**
   ```bash
   # 每次重装都要重新打补丁
   uv pip install -e . --system
   bash src/backend/patch_code.sh bisheng
   ```

3. **使用 reasoning 相关功能时**
   - 测试 Qwen、DeepSeek 等支持推理的模型
   - 需要查看模型的思考过程

#### ❌ 不需要执行的情况：

1. **不使用 reasoning 功能**
   - 只开发普通聊天、知识库等功能

2. **Docker 容器内开发**
   - Docker 镜像已包含补丁

### 使用方法

```bash
# 方式 1：指定 conda环境名称
bash src/backend/patch_code.sh bisheng

# 方式 2：使用当前激活的 Python 环境
conda activate bisheng
bash src/backend/patch_code.sh
```

### 验证补丁是否生效

```bash
# 检查补丁是否已应用
python -c "import langchain_openai; print('✓ 环境就绪')"

# 或者查看库文件
grep -n "reasoning_content" $(python -c 'from distutils.sysconfig import get_python_lib(); print(get_python_lib())')/langchain_openai/chat_models/base.py
```

### 自动化建议

建议在 `dev_start.sh` 中添加自动检查逻辑：

```bash
# 启动服务前检查补丁
if ! grep -q "reasoning_content" $(python -c 'from distutils.sysconfig import get_python_lib(); print(get_python_lib())')/langchain_openai/chat_models/base.py 2>/dev/null; then
    echo "⚠️ 检测到 langchain_openai 补丁未应用，正在应用..."
    bash src/backend/patch_code.sh
fi
```

---

## 📝 日志查看

### 日志文件位置

所有日志统一存放在项目根目录的 `logs/` 目录：

```
logs/
├── backend/
│   ├── backend_api.log      # 后端 API 日志
│   ├── backend_worker.log   # Celery Worker 日志
│   ├── backend_beat.log     # Celery Beat 日志
│   ├── backend_api.pid      # API 进程 ID
│   ├── backend_worker.pid   # Worker 进程 ID
│   └── backend_beat.pid     # Beat 进程 ID
├── platform/
│   ├── platform.log         # Platform 前端日志
│   └── platform.pid         # 进程 ID
└── client/
    ├── client.log           # Client 前端日志
    └── client.pid           # 进程 ID
```

### 实时查看日志

```bash
# 查看所有日志
tail -f logs/backend/backend_api.log
tail -f logs/backend/backend_worker.log
tail -f logs/platform/platform.log
tail -f logs/client/client.log

# 只看后端 API 日志
tail -f logs/backend/backend_api.log

# 同时看多个日志
tail -f logs/backend/backend_api.log logs/backend/backend_worker.log
```

### 根据服务类型查看

```bash
# 后端完整日志
tail -f logs/backend/backend_api.log logs/backend/backend_worker.log logs/backend/backend_beat.log

# 前端完整日志
tail -f logs/platform/platform.log logs/client/client.log
```

---

## 🔧 环境变量配置

开发脚本会自动设置以下环境变量：

```bash
# 数据库连接
export BISHENG_DATABASE_URL="mysql+pymysql://root:1234@localhost:3306/bisheng"

# Redis 连接
export BISHENG_REDIS_URL="redis://localhost:6379/0"

# Milvus 配置
export BS_MILVUS_CONNECTION_ARGS='{"host":"localhost","port":"19530","user":"","password":"","secure":false}'
export BS_MILVUS_IS_PARTITION='true'
export BS_MILVUS_PARTITION_SUFFIX='1'

# Elasticsearch 配置
export BS_ELASTICSEARCH_URL='http://localhost:9200'

# MinIO 配置
export BS_MINIO_ENDPOINT='localhost:9100'
export BS_MINIO_ACCESS_KEY='minioadmin'
export BS_MINIO_SECRET_KEY='minioadmin'
```

---

## ❓ 常见问题

### Q1: 端口被占用怎么办？

**症状**：启动时报端口已被占用

**解决方案**：
```bash
# 1. 检查是否有残留进程
lsof -i :7860
lsof -i :3001
lsof -i :4001

# 2. 使用停止脚本清理
./scripts/dev_stop.sh

# 3. 如果还不行，手动杀进程
lsof -ti:7860 | xargs kill -9
```

### Q2: Docker 服务启动失败？

**症状**：docker-compose up 报错

**解决方案**：
```bash
# 1. 查看 Docker 服务日志
docker-compose -p bisheng logs

# 2. 重启特定服务
docker-compose -p bisheng restart mysql
docker-compose -p bisheng restart redis

# 3. 完全重建（会丢失数据！）
docker-compose -p bisheng down -v
docker-compose -p bisheng up -d
```

### Q3: 后端依赖安装失败？

**症状**：`uv pip install -e .` 报错

**解决方案**：
```bash
# 1. 确保在正确的虚拟环境中
conda activate bisheng

# 2. 升级 pip 和 uv
pip install --upgrade pip uv

# 3. 清理缓存重装
rm -rf src/backend/.eggs
uv pip install -e . --system --no-cache-dir
```

### Q4: 前端无法访问后端 API？

**症状**：前端提示无法连接后端

**检查清单**：
1. ✅ 后端是否在运行：`lsof -i :7860`
2. ✅ 查看后端日志：`tail -f logs/backend/backend_api.log`
3. ✅ 检查代理配置是否正确（localhost:7860）
4. ✅ 确认防火墙没有阻止连接

### Q5: ASR/TTS 功能报错？

**症状**：语音识别或合成失败

**解决方案**：
```bash
# 1. 检查 ffmpeg 是否安装
which ffmpeg
ffmpeg -version

# 2. macOS 安装 ffmpeg
brew install ffmpeg

# 3. 检查阿里云 API Key 配置
# 在模型管理页面确认 API Key 已正确配置
```

### Q6: Celery Worker 不工作？

**症状**：异步任务不执行

**解决方案**：
```bash
# 1. 检查 Worker 是否在运行
ps aux | grep celery

# 2. 查看 Worker 日志
tail -f logs/backend/backend_worker.log

# 3. 手动重启 Worker
./scripts/dev_restart.sh -s backend
```

---

## 🎯 开发工作流建议

### 日常开发

```bash
# 早上开始工作
docker-compose -p bisheng up -d  # 启动依赖服务
./scripts/dev_start.sh           # 启动开发服务

# 开发过程中
./scripts/dev_restart.sh         # 代码修改后重启

# 晚上结束工作
./scripts/dev_stop.sh            # 停止开发服务
# Docker 服务保持运行（可选）
```

### 代码调试

1. **后端调试**：
   - 使用 VSCode 的 Python 调试器
   - 附加到运行的进程（PID 在 logs/backend/*.pid）
   - 或直接查看日志定位问题

2. **前端调试**：
   - 浏览器开发者工具
   - React Developer Tools
   - 查看控制台和网络请求

3. **日志分析**：
   - 养成实时查看日志的习惯
   - 使用 `grep` 过滤关键信息
   - 关注 ERROR 和 WARNING 级别日志

---

## 📚 进阶资源

- [BISHENG 项目文档](../README.md)
- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [Celery 最佳实践](https://docs.celeryq.dev/)
- [React 开发者工具](https://react.dev/learn/react-developer-tools)

---

## 💡 小贴士

1. **性能优化**：如果电脑性能有限，可以只启动需要的服务
   ```bash
   ./scripts/dev_start.sh -s backend  # 只开发后端
   ```

2. **保存现场**：下班时可以不关闭 Docker 服务，第二天继续
   ```bash
   ./scripts/dev_stop.sh  # 只关闭开发服务
   # Docker 服务保持运行
   ```

3. **快速排错**：遇到问题先看日志，90% 的问题都能在日志中找到线索

4. **环境隔离**：使用 conda 虚拟环境，避免污染系统 Python

5. **端口冲突**：如果常用端口被占用，可以修改配置文件更换端口

---

**祝你开发愉快！** 🎉

如有问题，请查看项目 README 或联系团队成员。
