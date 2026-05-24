# GM-System

GM-System 是一个基于 Django 和 Django REST Framework 的游戏后台管理服务示例。项目包含玩家管理、邮件发放、公告管理、CDK 兑换和审计日志等模块，使用 PostgreSQL 保存业务数据。

该项目主要演示后台服务中常见的管理接口、事务处理、操作审计和统一响应格式。

## 功能

- 玩家管理：玩家基础信息、等级、金币、钻石和账号状态。
- 邮件管理：单人邮件、全服邮件字段、附件领取状态和过期时间。
- CDK 管理：兑换码、有效期、使用次数和兑换记录。
- 公告管理：公告内容和生效时间。
- 审计日志：记录后台对象的创建、修改和删除。
- JWT 鉴权：使用 access token 和 refresh token。
- 统一响应格式：通过 DRF renderer 输出统一响应结构。
- 全局异常处理：统一返回错误结构。
- PostgreSQL 持久化。

## 技术栈

- Python
- Django
- Django REST Framework
- djangorestframework-simplejwt
- django-cors-headers
- PostgreSQL
- python-dotenv

## 目录结构

```text
backend/
  manage.py
  my_gm_backend/       Django 项目配置
  players/             玩家模块
  mails/               邮件模块
  notices/             公告模块
  cdks/                CDK 模块
  audit/               审计日志模块
  utils/               统一响应和异常处理
Frontend_API_Guide.md  前端接口说明
README.md
```

## 本地运行

### 1. 准备环境

建议使用 Python 3.12+ 和 PostgreSQL。

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\activate
```

当前仓库没有固定的 `requirements.txt`，可以按项目使用到的包安装：

```powershell
pip install django djangorestframework djangorestframework-simplejwt django-cors-headers python-dotenv psycopg2-binary
```

### 2. 配置数据库

项目会从环境变量或 `.env` 读取数据库配置：

```text
DB_NAME=gm_system
DB_USER=postgres
DB_PASSWORD=123456
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=change-me
DEBUG=True
```

`.env` 文件放在 `backend/` 目录下。

### 3. 初始化数据库

```powershell
python manage.py migrate
python manage.py createsuperuser
```

### 4. 启动服务

```powershell
python manage.py runserver
```

默认访问地址：

```text
http://127.0.0.1:8000/
```

## 接口模块

项目路由按 Django app 拆分：

- `players/`：玩家管理接口。
- `mails/`：邮件管理与领取接口。
- `notices/`：公告接口。
- `cdks/`：兑换码接口。
- `audit/`：审计日志接口。

更多接口说明见：

```text
Frontend_API_Guide.md
```

## 事务与状态控制

项目中部分业务使用 `transaction.atomic()` 和 `select_for_update()` 控制并发写入：

- 邮件附件领取：锁定邮件和玩家记录，避免重复领取。
- CDK 兑换：锁定兑换码记录，检查剩余次数和玩家兑换记录。

CDK 兑换记录使用联合唯一约束，保证同一玩家不能重复兑换同一个 CDK。

## 当前限制

- 当前仓库只包含后端服务，没有完整前端工程。
- 默认配置面向本地开发，生产环境需要修改 `SECRET_KEY`、数据库密码、`DEBUG` 和 `ALLOWED_HOSTS`。
- 没有提供 Docker Compose 或自动化部署脚本。
- 没有固定依赖锁文件，首次运行需要根据项目模块安装依赖。
- 邮件全服批量领取逻辑仍是预留能力。

## License

未指定。
