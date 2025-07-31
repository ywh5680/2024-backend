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
[
  {
    "id": 1,
    "content": "这个活动很棒！",
    "datetime": "2023-10-15T14:30:00Z",
    "qq": "123****89",
    "email": "u***@example.com",
    "children": [2, 3]  // 子评论的ID列表
  }
]
```

### 1.2 获取评论回复
- **URL**: `/api/comment/<parent_id>/`
- **Method**: GET
- **响应** (200 OK):
```json
[
  {
    "id": 2,
    "content": "回复内容",
    "datetime": "2023-10-15T14:35:00Z",
    "qq": "456****01",
    "email": "r***@example.com",
    "children": []
  }
]
```

### 1.3 创建新评论
- **URL**: `/api/comment/`
- **Method**: POST
- **参数** (JSON):
  | 参数名 | 类型 | 必填 | 说明 |
  |--------|------|------|------|
  | `content` | string | 是 | 评论内容 |
  | `parent` | int | 否 | 父评论ID |
  | `qq` | string | 条件必填 | QQ号(与email二选一) |
  | `email` | string | 条件必填 | 邮箱(与qq二选一) |
- **响应**:
  - 成功 (200 OK):
  ```json
  {}
  ```
  - 失败 (400 Bad Request):
  ```json
  {
    "detail": "at least one of qq or email shall be given"
  }
  ```
  - 父评论不存在 (404 Not Found):
  ```json
  {
    "detail": "parent不存在"
  }
  ```

## 2. 报名系统

### 2.1 提交报名信息
- **URL**: `/api/enroll/`
- **Method**: POST
- **参数** (JSON):
  | 参数名 | 类型 | 必填 | 说明 |
  |--------|------|------|------|
  | `name` | string | 是 | 姓名 |
  | `uid` | string | 是 | 学号 |
  | `major` | string | 是 | 年级专业 |
  | `phone` | string | 是 | 手机号 |
  | `email` | string | 是 | 邮箱 |
  | `department` | int | 是 | 意向部门(0-5) |
  | `content` | string | 否 | 报名原因 |
  | `qq` | string | 否 | QQ号 |
  | `code` | string | 是 | 邮箱验证码 |
- **响应**:
  - 成功 (201 Created):
  ```json
  {
    "id": 123,
    "name": "张三",
    ...
  }
  ```
  - 重复报名 (409 Conflict):
  ```json
  {
    "detail": "已经使用此email报名，当前状态：已报名"
  }
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
  {
    "alive_minutes": 5
  }
  ```
  - 邮箱格式错误 (422 Unprocessable Entity):
  ```json
  {
    "detail": "邮箱格式错误"
  }
  ```
  - 邮件发送失败 (500 Internal Server Error):
  ```json
  {
    "detail": "发送失败原因"
  }
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
  | `name` | string | 否 | 姓名 |
- **响应**:
  - 成功 (200 OK):
  ```json
  {
    "idx": 2,
    "progress": "一面已到"
  }
  ```
  - 未找到 (404 Not Found):
  ```json
  {
    "detail": "EnrollModel matching query does not exist."
  }
  ```
  - 参数缺失 (400 Bad Request):
  ```json
  {
    "detail": "no valid item used as key to look up"
  }
  ```
- **限流规则**: 同一IP每秒最多1次请求

### 2.4 查询报名截止状态
- **URL**: `/api/query_ddl/`
- **Method**: GET
- **响应**:
  - 未截止 (200 OK):
  ```json
  {}
  ```
  - 已截止 (499):
  ```json
  {}
  ```

## 3. 安全与限流规范

### 限流配置
| 接口 | 规则 | 响应码 |
|------|------|--------|
| POST /api/send_code/ | 6次/分钟/IP | 429 |
| POST /api/get_status/ | 1次/秒/IP | 429 |

### 部门编号对应关系
| 编号 | 部门名称 |
|------|----------|
| 0 | 程序开发 |
| 1 | Web开发 |
| 2 | 游戏开发 |
| 3 | APP开发 |
| 4 | UI设计 |
| 5 | ios |

## 4. 环境信息
- **基础环境**: https://2024.itstudio.club
- **后端仓库**: [GitHub](https://github.com/ywh5680/2024-backend)

## 贡献与支持
**维护团队**：爱特工作室  
**问题反馈**：请提交 issue 至项目仓库  

