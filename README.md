# 🛡️ GM-System 工业级后端架构白皮书 (v1.0)

> **发布日期**: 2026-01-01  
> **状态**: Release Candidate (1.0)  
> **架构师**: Lead Developer

---

## 🏗️ 1. 项目定位 (Positioning)

**GM-System** 是一套专为高并发游戏场景设计的后端管理系统。区别于传统的 CRUD 后台，本系统将 **资产安全**、**事务原子性** 和 **操作审计** 视为核心生命线。它通过 Django 5.0 的稳健生态结合 PostgreSQL 的强一致性特性，为游戏运营提供了一道坚不可摧的安全屏障。

---

## ⚡ 2. 硬核技术点 (Core Mechanics)

### 2.1 资产并发安全：行级锁 (Row-Level Locking)

在高并发的游戏业务中（如全服邮件领取、限时礼包抢兑），"超发"是绝对不可接受的灾难。本系统摒弃了不可靠的乐观锁，采用了 **悲观锁 (Pessimistic Locking)** 方案。

> [!IMPORTANT]
> **技术决策**: 使用 `select_for_update()` 配合 `transaction.atomic()` 实现强一致性。

#### 场景 A: 邮件附件领取 (Mails)
在 `mails/models.py` 中，我们实施了双重锁定策略：
1.  **锁定邮件行**: 防止同一个邮件被并发请求重复标记为 `is_claimed`。
2.  **锁定玩家行**: 防止在增加金币时发生 `Lost Update` 问题。

```python
with transaction.atomic():
    # 🔒 锁定邮件对象，阻塞其他并发请求
    mail = Mail.objects.select_for_update().get(pk=pk)
    if mail.is_claimed:
        raise ValueError("Double Claim Detected")
        
    # 🔒 锁定玩家资产
    player = Player.objects.select_for_update().get(pk=mail.receiver_id)
    player.gold += mail.item_count
    mail.is_claimed = True
    mail.save()
```

#### 场景 B: CDK 礼包抢兑 (CDKs)
在 `cdks/models.py` 中，针对限量礼包（如 `max_uses=10`），我们利用行级锁保证计数的绝对准确，杜绝 "第 11 个人兑换成功" 的情况。

---

## 👁️ 3. 安全审计机制 (Security Audit)

为了满足合规性要求及内部风控，我们设计了全量操作追溯系统。

### AuditLogMixin
通过 AOP (面向切面) 思想，在 `audit/mixins.py` 中重写了 Django Admin 的 `save_model` 和 `delete_model` 生命周期钩子。

| 拦截维度 | 说明 |
|:---|:---|
| **Actor** | 记录操作者 (Admin User) |
| **Action** | 创建 (Create) / 修改 (Update) / 删除 (Delete) |
| **Target** | 被操作对象 (如: 玩家 "User001") |
| **Detail** | 自动 diff 变更字段 (如: `gold: 100 -> 9999`) |
| **Context** | 记录客户端 IP (支持 X-Forwarded-For) |

---

## 🔌 4. API 规范 (API Standards)

为了降低前端联调成本，我们实现了更加 Pythonic 的统一响应流。

### 4.1 统一异常拦截 (Global Exception Handler)
位于 `utils/exception_handler.py`。即便是 `500 Server Error`，也会被捕获并转化为标准 JSON，前端无需处理 HTTP 状态码层面的崩溃。

### 4.2 成功响应包装 (Unified Renderer)
位于 `utils/renderers.py`。所有 DRF 的 Response 都会被自动包裹：

```json
{
    "code": 200,
    "message": "success",
    "data": {
        "id": "uuid",
        "nickname": "ProGamer"
    }
}
```

---

## 🛠️ 5. 工程质量 (Engineering Quality)

我们拒绝 "能跑就行" 的代码，追求工业级的交付标准。

-   **🔐 环境隔离**: 使用 `.env` 管理 `SECRET_KEY`、`DB_PASSWORD` 等敏感信息，严禁硬编码。
-   **🎟️ 双令牌机制**: 采用 JWT (`Access` + `Refresh`) 架构，兼顾安全性与用户体验。
-   **🧪 自动化测试**: 核心业务（邮件领取、CDK 兑换）覆盖了 100% 的边界测试用例（如过期、重复、并发）。
-   **🐳 Docker 化**: 提供标准容器环境，消除 "我本地是好的" 这类环境差异问题。

---

## 🔮 6. 未来路线 (Roadmap v2.0)

> [!NOTE]
> 随着用户量级突破 10w+，我们将引入以下架构升级：

1.  **Redis 缓存层**:
    -   缓存热点公告 (Notices) 和配置表，减轻 DB 压力。
    -   实现分布式锁 (Redlock) 替代 DB 行锁，提升吞吐量。

2.  **Celery 异步任务**:
    -   **邮件群发**: 将全服邮件发送逻辑从 Request-Response 循环中剥离，通过 MQ 异步处理。
    -   **日志归档**: 定时将审计日志转存至数仓 (Data Warehouse)。

---

**GM-System Backend Team**
*Building for Stability, Designing for Scale.*
