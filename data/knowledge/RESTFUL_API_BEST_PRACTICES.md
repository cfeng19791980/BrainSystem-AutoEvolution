# RESTful API设计最佳实践

## 基于Auth0: Best Practices for Flask API Development

---

## API设计概览

### Framework Comparison

| Framework | Type | Features | Use Case |
|-----------|------|----------|----------|
| Django | Full-stack | ORM, Admin UI, Auth | Large enterprise |
| Flask | Minimalist | Flexible, Extensions | Microservices |
| FastAPI | Modern | Async, Type hints, Fast | High performance |

---

## 1. 资源命名规范

### 核心原则

**REST定义**: 资源(Resource)是数据的第一级表示

**命名原则**:
```
✓ 使用名词复数形式
✓ 使用小写字母
✓ 使用连字符分隔单词
✓ 使用正斜杠表示层级
✓ 保持命名一致性
```

---

### 资源命名示例

**电商网站案例**:

```
✅ 正确命名:
/customers                     → 所有客户集合
/customers/{customerId}        → 单个客户
/customers/{customerId}/orders → 客户的订单集合
/customers/{customerId}/orders/{orderId} → 单个订单

❌ 错误命名:
/Customers                     → 不应使用大写
/customer                      → 应使用复数
/customers_orders              → 应使用斜杠表示层级
/customersOrders               → 应使用连字符
```

---

### 命名最佳实践清单

**资源命名**:
```
✅ /users                       → 用户集合
✅ /users/{userId}              → 单个用户
✅ /users/{userId}/playlists    → 用户播放列表
✅ /users/{userId}/mobile-devices → 用户移动设备

❌ /users/{userId}/mobileDevices → 不用驼峰命名
❌ /users/{userId}/mobile_devices → 不用下划线
❌ /Users/{userId}/Mobile-Devices → 不用大写
```

---

## 2. HTTP动词使用规范

### HTTP Request Methods

| Method | 用途 | 示例 |
|--------|------|------|
| GET | 数据检索 | GET /users |
| POST | 创建资源 | POST /users |
| PUT | 更新资源 | PUT /users/{userId} |
| DELETE | 删除资源 | DELETE /users/{userId} |
| PATCH | 部分更新 | PATCH /users/{userId} |

---

### 正确使用HTTP动词

**电商网站案例**:

```
✅ 正确使用:
GET    /users                    → 获取所有用户列表
POST   /users                    → 创建新用户
PUT    /users/{userId}           → 更新用户完整信息
DELETE /users/{userId}           → 删除用户
PATCH  /users/{userId}           → 部分更新用户信息
GET    /users/{userId}/orders    → 获取用户订单列表
POST   /users/{userId}/cart/checkout → 执行checkout动作

❌ 错误使用:
GET    /users/get-all            → 不应在URI中包含动词
POST   /users/create             → 不应显式声明create
GET    /users/{userId}/list-orders → 不应包含list
```

---

### CRUD vs Actions

**区分**:
```
CRUD操作 → 使用HTTP动词
- Create → POST
- Read → GET
- Update → PUT/PATCH
- Delete → DELETE

Actions → 使用URI表示动作
- checkout → /users/{userId}/cart/checkout
- play → /users/{userId}/playlists/{playlistId}/play
- run → /jobs/{jobId}/run
```

---

## 3. 应用结构设计

### Flask项目结构

```
project/
├── api/
│   ├── model/
│   │   ├── __init__.py
│   │   └── welcome.py         → 数据模型
│   ├── route/
│   │   └── home.py            → API路由
│   ├── schema/
│   │   ├── __init__.py
│   │   └── welcome.py         → 输入输出schema
│   └── service/
│       ├── __init__.py
│       └── welcome.py         → 业务逻辑
│   └── __init__.py
│
├── test/
│   ├── route/
│   │   ├── __init__.py
│   │   └── test_home.py       → 路由测试
│   └── __init__.py
│
├── .gitignore
├── app.py                     → 应用入口
├── Pipfile
├── Pipfile.lock
```

---

### 结构说明

**模块分工**:
```
Models → 数据描述，与数据库关联
Routes → API路由，资源和动作定义
Schemas → 输入输出定义，参数验证
Services → 业务逻辑，处理函数
Tests → 单元测试，集成测试
```

---

## 4. Blueprint路由组织

### Blueprint使用

```python
from flask import Blueprint
from http import HTTPStatus
from flasgger import swag_from
from api.model.welcome import WelcomeModel
from api.schema.welcome import WelcomeSchema

# 创建Blueprint
home_api = Blueprint('api', __name__)

@home_api.route('/')
@swag_from({
    'responses': {
        HTTPStatus.OK.value: {
            'description': 'Welcome to the Flask Starter Kit',
            'schema': WelcomeSchema
        }
    }
})
def welcome():
    """
    1 liner about the route
    
    A more detailed description of the endpoint
    """
    result = WelcomeModel()
    return WelcomeSchema().dump(result), 200
```

---

### 多Blueprint组织

```python
# app.py
from flask import Flask
from api.route.home import home_api

def create_app():
    app = Flask(__name__)
    
    # Register Blueprints
    app.register_blueprint(home_api, url_prefix='/api')
    app.register_blueprint(user_api, url_prefix='/api/users')
    app.register_blueprint(order_api, url_prefix='/api/orders')
    
    return app
```

---

## 5. Schema验证

### Marshmallow Schema

```python
from marshmallow import Schema, fields

class WelcomeSchema(Schema):
    """
    Welcome endpoint response schema.
    """
    message = fields.Str(required=True)
    status = fields.Str(required=True)

class UserSchema(Schema):
    """
    User model schema.
    """
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    email = fields.Email(required=True)
    created_at = fields.DateTime(dump_only=True)

class UserCreateSchema(Schema):
    """
    User creation input schema.
    """
    name = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=lambda p: len(p) >= 8)
```

---

### Schema使用

```python
from flask import request
from api.schema.user import UserSchema, UserCreateSchema

@user_api.route('/', methods=['POST'])
def create_user():
    """
    Create new user.
    """
    # 验证输入
    schema = UserCreateSchema()
    data = schema.load(request.json)
    
    # 业务逻辑
    user = create_user_service(data)
    
    # 返回输出
    return UserSchema().dump(user), 201

@user_api.route('/', methods=['GET'])
def list_users():
    """
    List all users.
    """
    users = get_all_users()
    return UserSchema(many=True).dump(users), 200
```

---

## 6. HTTP状态码规范

### 状态码分类

| Category | Range | Meaning |
|----------|-------|---------|
| Informational | 100-199 | 请求处理中 |
| Success | 200-299 | 请求成功 |
| Redirection | 300-399 | 需要重定向 |
| Client Error | 400-499 | 客户端错误 |
| Server Error | 500-599 | 服务端错误 |

---

### 常用状态码

```python
from http import HTTPStatus

# 成功状态码
HTTPStatus.OK           # 200 - 成功
HTTPStatus.CREATED      # 201 - 创建成功
HTTPStatus.NO_CONTENT   # 204 - 成功但无内容

# 客户端错误
HTTPStatus.BAD_REQUEST          # 400 - 错误请求
HTTPStatus.UNAUTHORIZED         # 401 - 未授权
HTTPStatus.FORBIDDEN            # 403 - 禁止访问
HTTPStatus.NOT_FOUND            # 404 - 资源不存在
HTTPStatus.CONFLICT             # 409 - 冲突
HTTPStatus.UNPROCESSABLE_ENTITY # 422 - 无法处理

# 服务端错误
HTTPStatus.INTERNAL_SERVER_ERROR # 500 - 服务器错误
HTTPStatus.SERVICE_UNAVAILABLE   # 503 - 服务不可用
```

---

### 状态码使用示例

```python
@user_api.route('/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """
    Update user by ID.
    """
    # 检查用户是否存在
    user = get_user(user_id)
    if not user:
        return {'error': 'User not found'}, HTTPStatus.NOT_FOUND
    
    # 验证输入
    try:
        data = UserUpdateSchema().load(request.json)
    except ValidationError as e:
        return {'error': e.messages}, HTTPStatus.BAD_REQUEST
    
    # 更新用户
    updated_user = update_user_service(user_id, data)
    
    return UserSchema().dump(updated_user), HTTPStatus.OK
```

---

## 7. 错误处理

### 统一错误处理

```python
from flask import jsonify
from http import HTTPStatus

class APIError(Exception):
    """
    Base API Exception.
    """
    def __init__(self, message, status_code=HTTPStatus.BAD_REQUEST):
        self.message = message
        self.status_code = status_code

class NotFoundError(APIError):
    """
    Resource not found error.
    """
    def __init__(self, resource):
        super().__init__(
            f"{resource} not found",
            HTTPStatus.NOT_FOUND
        )

class ValidationError(APIError):
    """
    Input validation error.
    """
    def __init__(self, errors):
        super().__init__(
            errors,
            HTTPStatus.UNPROCESSABLE_ENTITY
        )

# 注册错误处理器
@app.errorhandler(APIError)
def handle_api_error(error):
    response = jsonify({
        'error': error.message,
        'status': error.status_code
    })
    return response, error.status_code
```

---

### 使用示例

```python
@user_api.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """
    Get user by ID.
    """
    user = User.query.get(user_id)
    
    if not user:
        raise NotFoundError('User')
    
    return UserSchema().dump(user), HTTPStatus.OK
```

---

## 8. API文档生成

### Flasgger集成

```python
from flasgger import Swagger, swag_from

# 配置Swagger
app.config['SWAGGER'] = {
    'title': 'My API',
    'version': '1.0',
    'description': 'API Documentation',
    'specs_route': '/docs/'
}

Swagger(app)

# 使用示例
@user_api.route('/', methods=['GET'])
@swag_from({
    'responses': {
        HTTPStatus.OK.value: {
            'description': 'List of users',
            'schema': UserSchema
        }
    },
    'parameters': [
        {
            'name': 'limit',
            'in': 'query',
            'type': 'int',
            'description': 'Limit number of results'
        }
    ]
})
def list_users():
    """
    List all users.
    """
    users = User.query.all()
    return UserSchema(many=True).dump(users), HTTPStatus.OK
```

---

## 9. 测试策略

### 单元测试

```python
import pytest
from flask import Flask
from api.route.home import home_api

@pytest.fixture
def app():
    app = Flask(__name__)
    app.register_blueprint(home_api)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_welcome(client):
    """
    Test welcome endpoint.
    """
    response = client.get('/')
    
    assert response.status_code == 200
    assert 'message' in response.json
```

---

### 集成测试

```python
def test_create_user(client):
    """
    Test user creation flow.
    """
    # 创建用户
    create_response = client.post('/api/users', json={
        'name': 'Test User',
        'email': 'test@example.com',
        'password': 'testpassword123'
    })
    
    assert create_response.status_code == 201
    user_id = create_response.json['id']
    
    # 获取用户
    get_response = client.get(f'/api/users/{user_id}')
    
    assert get_response.status_code == 200
    assert get_response.json['name'] == 'Test User'
    
    # 删除用户
    delete_response = client.delete(f'/api/users/{user_id}')
    
    assert delete_response.status_code == 204
    
    # 验证删除
    get_deleted_response = client.get(f'/api/users/{user_id}')
    
    assert get_deleted_response.status_code == 404
```

---

## 10. Brain System API设计

### Brain Entry API

```python
from flask import Blueprint, request, jsonify
from http import HTTPStatus
from core.brain_entry import brain_entry

brain_api = Blueprint('brain', __name__)

@brain_api.route('/decision', methods=['POST'])
def get_decision():
    """
    Get brain decision for user input.
    
    Request:
        {
            "query": "user input text",
            "context": {...}
        }
    
    Response:
        {
            "intent": "detected intent",
            "confidence": 0.98,
            "action": "recommended action"
        }
    """
    data = request.json
    
    if not data or 'query' not in data:
        return jsonify({
            'error': 'Missing query parameter'
        }), HTTPStatus.BAD_REQUEST
    
    # Get brain decision
    decision = brain_entry(data['query'], data.get('context'))
    
    return jsonify(decision), HTTPStatus.OK

@brain_api.route('/semantic_search', methods=['POST'])
def semantic_search():
    """
    Semantic search in knowledge base.
    
    Request:
        {
            "query": "search query",
            "limit": 10
        }
    
    Response:
        {
            "results": [...],
            "total": 20
        }
    """
    data = request.json
    query = data.get('query')
    limit = data.get('limit', 10)
    
    if not query:
        return jsonify({
            'error': 'Missing query'
        }), HTTPStatus.BAD_REQUEST
    
    results = semantic_search_service(query, limit)
    
    return jsonify({
        'results': results,
        'total': len(results)
    }), HTTPStatus.OK
```

---

## 11. csi10 API设计

### Stock Analysis API

```python
stock_api = Blueprint('stock', __name__)

@stock_api.route('/indices', methods=['GET'])
def get_indices():
    """
    Get market indices data.
    
    Response:
        {
            "hs300": {...},
            "zz500": {...},
            "composite": {...}
        }
    """
    indices = fetch_all_indices()
    
    return jsonify(indices), HTTPStatus.OK

@stock_api.route('/analysis', methods=['POST'])
def analyze_stock():
    """
    Analyze stock with technical indicators.
    
    Request:
        {
            "code": "000001",
            "indicators": ["SMA", "RSI", "MACD"]
        }
    
    Response:
        {
            "indicators": {...},
            "signals": [...],
            "recommendation": "buy/hold/sell"
        }
    """
    data = request.json
    code = data.get('code')
    indicators = data.get('indicators', [])
    
    if not code:
        return jsonify({
            'error': 'Missing stock code'
        }), HTTPStatus.BAD_REQUEST
    
    result = analyze_stock_service(code, indicators)
    
    return jsonify(result), HTTPStatus.OK
```

---

## API设计检查清单

```
✅ 资源命名规范
  - 使用名词复数
  - 使用小写字母
  - 使用连字符分隔
  - 保持一致性

✅ HTTP动词正确使用
  - GET: 检索数据
  - POST: 创建资源
  - PUT: 更新资源
  - DELETE: 删除资源
  - PATCH: 部分更新

✅ 状态码规范
  - 200: 成功
  - 201: 创建成功
  - 400: 错误请求
  - 404: 资源不存在
  - 500: 服务器错误

✅ Schema验证
  - 输入验证
  - 输出格式化

✅ 错误处理
  - 统一错误格式
  - 错误日志记录

✅ API文档
  - Swagger/OpenAPI
  - 示例请求/响应

✅ 测试覆盖
  - 单元测试
  - 集成测试
```

---

## Pattern-Key

`api.restful.best_practices` - RESTful API设计最佳实践

---

**来源**: Auth0 - Best Practices for Flask API Development
**更新时间**: 2026-04-23 15:25
**适用项目**: BrainSystem + csi10 + Gateway