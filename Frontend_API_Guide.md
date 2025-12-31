# 🦄 前端联调启动任务书 (Frontend Integration Launch Brief)

> **致**: 前端开发组  
> **来自**: 后端技术负责人  
> **日期**: 2026-01-01  
> **优先级**: P0 (最高)



## 1. 仓库与环境准备 (Repo & Environment)

### 1.1 获取最新代码
请确保你的本地仓库与远程 `main` 分支保持同步，获取最新的后端基建代码。
```bash
git checkout main
git pull origin main
```

### 1.2 配置环境变量 (Critical)
后端项目依赖环境变量隔离敏感信息。请在 `backend/` 目录下操作：

1.  **复制模板文件**：
    找到 `backend/.env.example`，将其复制一份并重命名为 `.env`。
    ```bash
    cd backend
    cp .env.example .env
    ```

2.  **配置本地密钥**：
    打开 `.env` 文件，确保以下配置已填入（本地开发环境专用）：
    ```ini
    # 数据库密码 (本地 Docker 默认)
    DB_PASSWORD=123456
    
    # 开启调试模式
    DEBUG=True
    ```

---

## 2. 快速启动指南 (Run the Backend)

### 2.1 启动数据库 (Docker)
请确保你已安装 Docker Desktop，并在项目根目录下运行：
```bash
# 启动 PostgreSQL 容器
docker run --name gm-db -e POSTGRES_PASSWORD=123456 -p 5432:5432 -d postgres
```
*(如果已有本地 Postgres 服务，请确保库名为 `gm_system` 且密码匹配)*

### 2.2 准备 Python 环境
确保你已安装依赖，特别是 **`python-dotenv`**，否则后端无法读取环境变量：
```bash
cd backend
# 激活你的 venv
# Windows: .\venv\Scripts\activate
# Mac/Linux: source venv/bin/activate

pip install -r requirements.txt
pip install python-dotenv  # ⚠️ 务必确认此包已安装
```

### 2.3 启动后端服务
```bash
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```
看到 `Starting development server at http://0.0.0.0:8000/` 即表示启动成功。

---

## 3. 第一个联调任务：认证通顺 (First Milestone: Auth)

**目标**：验证前后端连通性，成功获取 JWT 令牌。

请在你的 Vue 项目中（或使用 Postman）发起第一个测试请求：

-   **动作**：调用登录接口
-   **URL**：`http://127.0.0.1:8000/api/token/`
-   **Method**：`POST`
-   **Body**：`{"username": "admin", "password": "your_password"}` *(注：请先通过 `python manage.py createsuperuser` 创建一个本地管理员)*

**验收标准**：
服务器返回 `200 OK`，且响应体中包含标准的 JWT 结构：
```json
{
    "access": "eyJ0eXB...",
    "refresh": "eyJ0eXB..."
}
```

> 💡 **详细文档**：具体的接口参数和完整响应格式，请查阅项目根目录下的 **[Frontend_API_Guide.md](../Frontend_API_Guide.md)**。

---

## 4. 协作守则 (Branching Policy)

为了保证代码库的稳定性，请严格遵守以下分支规范，**违者代码将无法合并**。

1.  🚫 **严禁直接修改 `main` 分支**
    `main` 分支受到 Ruleset 保护，禁止直接 Push。

2.  ✅ **使用 `dev-frontend` 分支**
    你的所有开发工作都应在 `dev-frontend` 分支（或从其切出的功能分支）上进行。

3.  🔀 **Pull Request (PR) 流程**
    -   开发完成后，请提交 PR 至 `main` 分支。
    -   指定后端负责人为 Reviewer。
    -   严禁强行合并，必须等待 CI 通过且审批通过。

---

**Let's build something amazing! 🚀**
