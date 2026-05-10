# Python常见错误及处理指南

## 基于BetterStack: 15 Common Errors in Python

---

## 错误分类概览

### Error Categories

| Category | Error Types | Frequency | Difficulty |
|----------|-------------|-----------|------------|
| Syntax Errors | SyntaxError, IndentationError | High | Easy |
| Name Errors | NameError, UnboundLocalError | Medium | Medium |
| Type Errors | TypeError, ValueError | High | Medium |
| Runtime Errors | IndexError, KeyError, ZeroDivisionError | High | Easy |
| Memory Errors | MemoryError, OSError | Low | Hard |

---

## 1. SyntaxError (语法错误)

### 错误说明

**定义**: Python解释器解析代码时发现不符合语法规则的代码

**常见原因**:
```
✗ 未闭合的字符串
✗ 缩进问题
✗ 错误使用赋值运算符 (=)
✗ Python关键字拼写错误
✗ 缺少括号、圆括号或大括号
✗ 在旧版本Python使用新语法
```

---

### 案例1: 字典缺少冒号

**错误代码**:
```python
employees = {"pam" 30, "jim" 28}
```

**Traceback**:
```
File "/home/user/main.py", line 1
employees = {"pam" 30,
            ^^^^^^^^
SyntaxError: invalid syntax. Perhaps you forgot a comma?
```

**解决方案**:
```python
# Correct: Add colon to separate key and value
employees = {"pam": 30, "jim": 28}
```

---

### 案例2: 未闭合字符串

**错误代码**:
```python
message = "Hello World
print(message)
```

**Traceback**:
```
SyntaxError: EOL while scanning string literal
```

**解决方案**:
```python
# Correct: Close the string
message = "Hello World"
print(message)
```

---

### 最佳实践

**预防措施**:
```
1. 配置Linter (Pylint, Flake8)
2. 使用IDE自动语法检查 (VS Code + Pylance)
3. 代码编辑器自动格式化 (Black)
4. 执行前静态分析
```

---

## 2. IndentationError (缩进错误)

### 错误说明

**定义**: Python代码缩进不符合规范

**常见原因**:
```
✗ 混合使用Tab和空格
✗ 缩进空格数不正确
✗ 嵌套块缩进错误
✗ 语句开头有空白
```

---

### 案例: 缺少缩进块

**错误代码**:
```python
if True:
print("Missing indentation")
```

**Traceback**:
```
File "/home/user/main.py", line 2
    print("Missing colon")
    ^
IndentationError: expected an indented block after 'if' statement on line 1
```

**解决方案**:
```python
# Correct: Add indentation (4 spaces)
if True:
    print("Correct indentation")
```

---

### 最佳实践

**缩进规范**:
```
✓ 使用4个空格作为标准缩进
✓ 不混合使用Tab和空格
✓ 配置编辑器自动格式化 (Black)
✓ 使用Pylance检查缩进错误
```

---

## 3. NameError (名称错误)

### 错误说明

**定义**: 使用未定义或超出作用域的标识符

**常见原因**:
```
✗ 变量未定义就使用
✗ 变量名拼写错误
✗ 变量作用域问题
✗ 导入模块缺失
```

---

### 案例: 未定义变量

**错误代码**:
```python
print(name)  # name not defined
```

**Traceback**:
```
Traceback (most recent call last):
File "/home/user/main.py", line 1, in <module>
    print(name)
NameError: name 'name' is not defined
```

**解决方案**:
```python
# Correct: Define variable before use
name = "Alice"
print(name)
```

---

### 案例: 变量拼写错误

**错误代码**:
```python
count = 10
print(cont)  # typo: count → cont
```

**解决方案**:
```python
# Correct: Fix typo
count = 10
print(count)
```

---

### 最佳实践

**预防措施**:
```
✓ 使用前先定义变量
✓ 检查变量名拼写
✓ 确认变量作用域
✓ 配置Linter提前发现
✓ 使用IDE变量提示
```

---

## 4. ValueError (值错误)

### 错误说明

**定义**: 函数收到正确数据类型但值无效

**常见原因**:
```
✗ int()传入非整数字符串
✗ max()或min()传入空iterable
✗ 数值转换失败
```

---

### 案例1: int()转换非整数字符串

**错误代码**:
```python
num = int("forty-two")  # Not integer string
```

**Traceback**:
```
Traceback (most recent call last):
File "/home/user/main.py", line 1, in <module>
    num = int("forty-two")
ValueError: invalid literal for int() with base 10: 'forty-two'
```

**解决方案**:
```python
# Correct: Use valid integer string
num = int("42")  # Valid

# Alternative: Use try-except for user input
try:
    num = int(user_input)
except ValueError:
    print("Invalid input, please enter a number")
```

---

### 案例2: max()空列表

**错误代码**:
```python
result = max([])  # Empty list
```

**Traceback**:
```
ValueError: max() arg is an empty sequence
```

**解决方案**:
```python
# Correct: Check if list is empty
data = []
if data:
    result = max(data)
else:
    result = None

# Alternative: Provide default value
result = max(data, default=0)
```

---

## 5. UnboundLocalError (局部变量未绑定)

### 错误说明

**定义**: 在函数中引用局部变量前未赋值

**常见原因**:
```
✗ 函数内引用全局变量同名局部变量
✗ 在赋值前引用局部变量
✗ 使用del删除后引用
```

---

### 案例: 全局变量遮蔽

**错误代码**:
```python
name = "Global"

def display_name():
    print(name)  # Reference before assignment
    name = "Local"  # Local variable shadows global

display_name()
```

**Traceback**:
```
Traceback (most recent call last):
File "/home/user/main.py", line 5, in <module>
    display_name()
File "/home/user/main.py", line 2, in display_name
    print(name)
UnboundLocalError: local variable 'name' referenced before assignment
```

**解决方案**:
```python
# Solution 1: Use different variable name
name_global = "Global"

def display_name():
    name_local = "Local"
    print(name_local)

display_name()

# Solution 2: Use global keyword
name = "Global"

def display_name():
    global name
    print(name)
    name = "Local"

display_name()
```

---

## 6. TypeError (类型错误)

### 错误说明

**定义**: 操作不支持的对象数据类型

**常见原因**:
```
✗ 字符串和数字运算
✗ 非iterable对象迭代
✗ 函数参数类型错误
✗ 参数数量不匹配
✗ 不同类型比较
```

---

### 案例1: 字符串和数字除法

**错误代码**:
```python
result = "hello" / 3  # String division by int
```

**Traceback**:
```
Traceback (most recent call last):
File "/home/user/main.py", line 1, in <module>
    print("hello" / 3)
TypeError: unsupported operand type(s) for /: 'str' and 'int'
```

**解决方案**:
```python
# Correct: Use correct types
result = 10 / 3  # Number division

# Or convert types
text = "hello"
count = 3
result = text * count  # String repetition
```

---

### 案例2: 非iterable迭代

**错误代码**:
```python
for item in 123:  # Integer not iterable
    print(item)
```

**Traceback**:
```
TypeError: 'int' object is not iterable
```

**解决方案**:
```python
# Correct: Iterate over iterable
for item in [1, 2, 3]:
    print(item)
```

---

## 7. IndexError (索引错误)

### 错误说明

**定义**: 访问列表超出范围的索引

**常见原因**:
```
✗ 索引超过列表长度
✗ 空列表访问索引
✗ 负索引超出范围
```

---

### 案例: 列表索引超出范围

**错误代码**:
```python
numbers = [1, 2, 3]
print(numbers[4])  # Index 4 out of range
```

**Traceback**:
```
Traceback (most recent call last):
File "/home/user/main.py", line 2, in <module>
    print(numbers[4])
IndexError: list index out of range
```

**解决方案**:
```python
# Solution 1: Check length
numbers = [1, 2, 3]
if len(numbers) > 4:
    print(numbers[4])
else:
    print("Index out of range")

# Solution 2: Use try-except
try:
    print(numbers[4])
except IndexError:
    print("Index out of range")

# Solution 3: Use safe indexing
def safe_index(lst, idx):
    return lst[idx] if idx < len(lst) else None

result = safe_index(numbers, 4)
```

---

## 8. KeyError (键错误)

### 错误说明

**定义**: 访问字典不存在键

**常见原因**:
```
✗ 字典键不存在
✗ 键拼写错误
✗ 嵌套字典键缺失
```

---

### 案例: 字典键不存在

**错误代码**:
```python
my_dict = {"name": "Alice", "age": 30}
print(my_dict["location"])  # Key not exists
```

**Traceback**:
```
Traceback (most recent call last):
File "/home/user/main.py", line 2, in <module>
    print(my_dict["location"])
KeyError: 'location'
```

**解决方案**:
```python
# Solution 1: Use .get() method
location = my_dict.get("location", "Unknown")
print(location)

# Solution 2: Check key exists
if "location" in my_dict:
    print(my_dict["location"])
else:
    print("Key not found")

# Solution 3: Use try-except
try:
    print(my_dict["location"])
except KeyError:
    print("Key not found")
```

---

## 9. AttributeError (属性错误)

### 错误说明

**定义**: 对象没有指定属性或方法

**常见原因**:
```
✗ 对象类型错误
✗ 属性名拼写错误
✗ 方法不存在
```

---

### 案例: list对象调用字符串方法

**错误代码**:
```python
my_list = [1, 2, 3]
print(my_list.lower())  # list has no .lower() method
```

**Traceback**:
```
Traceback (most recent call last):
File "/home/user/main.py", line 2, in <module>
    print(my_list.lower())
AttributeError: 'list' object has no attribute 'lower'
```

**解决方案**:
```python
# Correct: Check object type
my_list = [1, 2, 3]

if isinstance(my_list, str):
    print(my_list.lower())
else:
    # Convert to string first
    print(str(my_list).lower())
```

---

## 10. ZeroDivisionError (除零错误)

### 错误说明

**定义**: 除法运算除数为零

**案例**:
```python
result = 5 / 0  # Division by zero
```

**Traceback**:
```
Traceback (most recent call last):
File "/home/user/main.py", line 1, in <module>
    result = 5 / 0
ZeroDivisionError: division by zero
```

**解决方案**:
```python
# Solution 1: Check divisor
divisor = 0
if divisor != 0:
    result = 5 / divisor
else:
    result = None

# Solution 2: Use try-except
try:
    result = 5 / divisor
except ZeroDivisionError:
    print("Cannot divide by zero")
    result = None
```

---

## 11. MemoryError (内存错误)

### 错误说明

**定义**: 内存不足以执行操作

**案例**:
```python
large_list = [0] * (10**9)  # Billion elements
```

**Traceback**:
```
MemoryError
```

**解决方案**:
```python
# Solution 1: Use generator
def generate_large_sequence(n):
    for i in range(n):
        yield i

# Solution 2: Process in chunks
chunk_size = 1000000
for i in range(0, 10**9, chunk_size):
    chunk = [0] * chunk_size
    process_chunk(chunk)
```

---

## 12. ImportError/ModuleNotFoundError

### 错误说明

**定义**: 导入模块不存在或路径错误

**案例**:
```python
import non_existent_module
```

**Traceback**:
```
ModuleNotFoundError: No module named 'non_existent_module'
```

**解决方案**:
```python
# Solution 1: Install missing module
# pip install non_existent_module

# Solution 2: Check module path
import sys
sys.path.append('/path/to/module')

# Solution 3: Use try-except
try:
    import module
except ImportError:
    print("Module not found, using fallback")
    import fallback_module
```

---

## 13. FileNotFoundError

### 错误说明

**定义**: 文件不存在

**案例**:
```python
with open("non_existent.txt", "r") as f:
    content = f.read()
```

**Traceback**:
```
FileNotFoundError: [Errno 2] No such file or directory: 'non_existent.txt'
```

**解决方案**:
```python
# Solution 1: Check file exists
import os
if os.path.exists("file.txt"):
    with open("file.txt", "r") as f:
        content = f.read()

# Solution 2: Use try-except
try:
    with open("file.txt", "r") as f:
        content = f.read()
except FileNotFoundError:
    print("File not found")
```

---

## 14. UnicodeDecodeError

### 错误说明

**定义**: 文件编码错误

**案例**:
```python
with open("file.txt", "r", encoding="utf-8") as f:
    content = f.read()
```

**Traceback**:
```
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xe9
```

**解决方案**:
```python
# Solution 1: Specify correct encoding
with open("file.txt", "r", encoding="cp1252") as f:
    content = f.read()

# Solution 2: Use errors='ignore'
with open("file.txt", "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

# Solution 3: Use errors='replace'
with open("file.txt", "r", encoding="utf-8", errors="replace") as f:
    content = f.read()
```

---

## 15. PermissionError

### 错误说明

**定义**: 权限不足操作文件

**案例**:
```python
with open("/root/protected.txt", "w") as f:
    f.write("content")
```

**Traceback**:
```
PermissionError: [Errno 13] Permission denied: '/root/protected.txt'
```

**解决方案**:
```python
# Solution 1: Check permissions
import os
if os.access("/root/protected.txt", os.W_OK):
    with open("/root/protected.txt", "w") as f:
        f.write("content")

# Solution 2: Use try-except
try:
    with open("/root/protected.txt", "w") as f:
        f.write("content")
except PermissionError:
    print("Permission denied")
```

---

## 通用错误处理策略

### Strategy 1: Try-Except Block

**基本结构**:
```python
try:
    # Code that may raise exception
    result = operation()
except SpecificError as e:
    # Handle specific error
    print(f"Error: {e}")
except Exception as e:
    # Handle general error
    print(f"Unexpected error: {e}")
finally:
    # Cleanup code
    cleanup()
```

---

### Strategy 2: Validation Before Execution

**预防式检查**:
```python
def safe_operation(data):
    # Validate input
    if not data:
        return None
    
    if not isinstance(data, list):
        raise TypeError("Expected list")
    
    # Safe execution
    try:
        return process(data)
    except IndexError:
        return None
```

---

### Strategy 3: Logging Errors

**错误日志记录**:
```python
import logging

logging.basicConfig(level=logging.ERROR)

def operation_with_logging():
    try:
        result = risky_operation()
    except Exception as e:
        logging.error(f"Operation failed: {e}")
        raise
```

---

## BrainSystem中的错误处理

### Brain Hook错误处理

```python
def brain_hook_safe(user_input):
    try:
        decision = brain_hook.get_decision(user_input)
        
        if decision['confidence'] < 0.95:
            raise ValueError("Low confidence")
        
        return decision
        
    except ValueError as e:
        # Fallback to keyword match
        return keyword_match(user_input)
    
    except Exception as e:
        # Log error and return default
        logging.error(f"Brain hook error: {e}")
        return default_decision()
```

---

### Semantic Search错误处理

```python
def semantic_search_safe(query):
    try:
        # Primary: NVIDIA Embedding
        return nvidia_embedding_search(query)
        
    except ConnectionError:
        # Fallback: FTS
        return fts_search(query)
        
    except Exception as e:
        # Fallback: Keyword match
        logging.warning(f"Search error: {e}")
        return keyword_match(query)
```

---

## Pattern-Key

`python.errors.handling` - Python常见错误及处理指南

---

**来源**: BetterStack - 15 Common Errors in Python
**更新时间**: 2026-04-23 15:15
**适用项目**: BrainSystem + csi10 + Gateway