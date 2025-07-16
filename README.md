# 爱特工作室2025迎新网-API 文档

## 项目概述
**中国海洋大学信息科学与工程学部爱特工作室2025年迎新网项目**
RESTfulAPI，JWT，HTTPS
## 1. 评论系统

### 1.1 获取评论列表
- **URL**: `/api/comment/`
- **Method**: GET
- **参数**:
  | 参数名 | 类型 | 必填 | 默认值 | 说明 |
  |--------|------|------|--------|------|
  | `limit` | int | 否 | 20 | 返回评论数量限制 |
  | `start` | int | 否 | 0 | 起始位置（分页偏移量） |
- **响应** (200 OK):
```json
{
  "count": 85,
  "next": "/api/comment/?start=20&limit=20",
  "previous": null,
  "results": [
    {
      "id": 1,
      "content": "这个活动很棒！",
      "created_at": "2023-10-15T14:30:00Z",
      "qq": "123****89",
      "email": "u***@example.com",
      "replies": [
        {
          "id": 2,
          "content": "我也这么认为",
          "created_at": "2023-10-15T15:00:00Z",
          "qq": "456****01"
        }
      ]
    }
  ]
}
```

### 1.2 创建新评论
- **URL**: `/api/comment/`
- **Method**: POST
- **参数** (JSON):
  | 参数名 | 类型 | 必填 | 说明 |
  |--------|------|------|------|
  | `content` | string | 是 | 评论内容(10-500字符) |
  | `parent` | int | 否 | 父评论ID |
  | `qq` | string | 条件必填 | QQ号(与email二选一) |
  | `email` | string | 条件必填 | 邮箱(与qq二选一) |
- **响应**:
  - 成功 (201 Created):
  ```json
  {"id": 123, "created_at": "2023-10-16T09:15:00Z"}
  ```
  - 失败 (400 Bad Request):
  ```json
  {
    "error": "VALIDATION_ERROR",
    "detail": {
      "content": ["内容长度需在10-500字符之间"],
      "non_field_errors": ["必须提供qq或email"]
    }
  }
  ```

---

## 2. 报名系统

### 2.1 提交报名信息
- **URL**: `/api/enroll/`
- **Method**: POST
- **参数** (JSON):
  | 参数名 | 类型 | 必填 | 说明 |
  |--------|------|------|------|
  | `name` | string | 是 | 姓名(2-20字符) |
  | `uid` | string | 是 | 学号(格式校验) |
  | `major` | string | 是 | 年级专业 |
  | `phone` | string | 是 | 手机号(格式校验) |
  | `email` | string | 是 | 邮箱 |
  | `department` | string | 是 | 意向部门 |
  | `content` | string | 否 | 报名原因(可选) |
  | `qq` | string | 否 | QQ号(可选) |
  | `code` | string | 是 | 邮箱验证码 |
- **响应**:
  - 成功 (200 OK):
  ```json
  {"status": "success", "enroll_id": 456}
  ```
  - 验证码错误 (400 Bad Request):
  ```json
  {"error": "INVALID_CODE", "message": "验证码错误或已过期"}
  ```
  - 已报名 (409 Conflict):
  ```json
  {"error": "ALREADY_ENROLLED", "message": "该邮箱已报名"}
  ```

### 2.2 发送验证码
- **URL**: `/api/send_code/`
- **Method**: POST
- **参数** (JSON):
  | 参数名 | 类型 | 必填 | 说明 |
  |--------|------|------|------|
  | `email` | string | 是 | 邮箱地址 |
- **响应**:
  - 成功 (200 OK):
  ```json
  {"expire_in": 300, "message": "验证码已发送"}
  ```
  - 无效邮箱 (400 Bad Request):
  ```json
  {"error": "INVALID_EMAIL", "message": "邮箱格式不正确"}
  ```
  - 限流响应 (429 Too Many Requests):
  ```json
  {"error": "RATE_LIMITED", "message": "请求过于频繁，请1分钟后再试"}
  ```
- **限流规则**: 同一IP每分钟最多6次请求

### 2.3 查询报名状态
- **URL**: `/api/get_status/`
- **Method**: POST
- **参数** (JSON，至少提供一项):
  | 参数名 | 类型 | 必填 | 说明 |
  |--------|------|------|------|
  | `email` | string | 否 | 邮箱 |
  | `phone` | string | 否 | 手机号 |
  | `qq` | string | 否 | QQ号 |
  | `name` | string | 否 | 姓名(模糊匹配) |
- **响应**:
  - 成功 (200 OK):
  ```json
  {
    "enroll_id": 456,
    "name": "张*",
    "department": "技术部",
    "progress": "初审通过",
    "idx": 2,
    "last_updated": "2023-10-15T14:30:00Z"
  }
  ```
  - 未找到 (404 Not Found):
  ```json
  {"error": "NOT_FOUND", "message": "未找到报名记录"}
  ```
  - 参数缺失 (400 Bad Request):
  ```json
  {"error": "MISSING_PARAMS", "message": "至少需要提供一个查询参数"}
  ```
- **限流规则**: 同一IP每秒最多1次请求

### 2.4 报名截止状态
**前端依据实际截止时间对页面表单进行更改**

---

## 3. 安全与限流规范

### 全局安全策略
1. **输入验证**:
   - 所有字符串参数进行XSS过滤
   - 邮箱/手机号格式校验
   - 学号格式正则校验：`/^[A-Z0-9]{8,12}$/`

2. **数据脱敏**:
   ```python
   # 示例：手机号脱敏
   def desensitize_phone(phone):
       return phone[:3] + '****' + phone[-4:]
   ```

3. **SQL防护**:
   - 使用ORM参数化查询
   - 姓名模糊查询特殊字符过滤

### 限流配置
| 接口 | 规则 | 响应码 |
|------|------|--------|
| POST /api/send_code/ | 6次/分钟/IP | 429 |
| POST /api/get_status/ | 1次/秒/IP | 429 |
| POST /api/comment/ | 5次/分钟/IP | 429 |

---

## 4. 错误码体系

| 错误码 | HTTP状态 | 说明 |
|--------|----------|------|
| `VALIDATION_ERROR` | 400 | 参数验证失败 |
| `INVALID_CODE` | 400 | 验证码错误 |
| `RATE_LIMITED` | 429 | 请求过于频繁 |
| `NOT_FOUND` | 404 | 资源不存在 |
| `ALREADY_ENROLLED` | 409 | 重复报名 |
| `SYSTEM_BUSY` | 503 | 系统繁忙 |

---

## 5. 前后端协作说明

### 环境信息
- **基础环境**: https://2024.itstudio.club
- **测试环境**: https://test.enroll.example.com
- **生产环境**: https://enroll.example.com
- **后端仓库**: [GitHub](https://github.com/ywh5680/2024-backend)
- **API文档**: [Apifox](https://app.apifox.com/invite/project?token=AeKoWXrVX459GEXPqKjZP)


---

## 优化改进点(一些细节问题)

1. **评论系统增强**:
   - 增加内容安全过滤（自动过滤敏感词）
   - 添加点赞功能字段（预留扩展）
   - 邮箱/QQ号自动脱敏

2. **报名流程优化**:
   - 验证码有效期明确为5分钟（300秒）
   - 学号格式统一校验规则
   - 防止重复提交机制（相同邮箱24小时内限1次）

3. **状态查询改进**:
   - 返回部分脱敏的姓名（保护隐私）
   - 添加最后更新时间戳
   - 状态索引标准化（0=已提交, 1=一面, 2=二面, 3=已录取）

4. **安全增强**:
   - 关键操作添加请求签名
   - 生产环境禁用详细错误信息
   - 管理员接口IP白名单机制

---

## 贡献与支持
**维护团队**：爱特工作室  
**问题反馈**：请提交 issue 至项目仓库  
**更新日志**：[查看更新历史](CHANGELOG.md)

> **重要提示**：实际部署前请确保所有依赖服务（数据库、邮件服务等）已正确配置。注册接口的验证码功能需配合邮件服务实现。
> 根据您的需求，我对接口文档进行了全面优化，确保功能合理性和前后端协作效率。以下是完善的接口文档：
