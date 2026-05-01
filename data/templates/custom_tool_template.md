# -*- coding: utf-8 -*-
"""
自定义 OpenClaw 工具（Tool Extensions）开发流程模版
==================================================
版本: 1.0
创建: 2026-05-02
来源: code-reader 扩展实践

目录:
1. 文件结构
2. 核心文件：index.ts
3. 插件声明：openclaw.plugin.json
4. 包信息：package.json
5. 注册到 openclaw.json
6. 依赖安装
7. 重启生效
8. 验证
"""

# ============================================================
# 1. 文件结构
# ============================================================
"""
extensions/你的工具名/
  index.ts              ← 主代码，必须
  openclaw.plugin.json  ← 插件声明，必须
  package.json          ← 包信息，必须
  node_modules/         ← npm install 后自动生成
"""

# ============================================================
# 2. 核心文件：index.ts（标准模版）
# ============================================================

"""
// -*- coding: utf-8 -*-
// 导入需要的 Node 模块
import * as fs from "fs";
import * as path from "path";
// 如需额外依赖，npm install 后在 ts 中 import

/**
 * 工具执行函数
 * 参数: (toolCallId, params, signal)
 *   - toolCallId: string, 调用ID
 *   - params: object, 调用时传入的参数
 *   - signal: AbortSignal, 超时取消信号
 * 返回: { content: [{ type: "text", text: string }] }
 */
async function executeMyTool(
  _toolCallId: string,
  params: { /* 你的参数类型定义 */ },
  _signal?: AbortSignal
): Promise<{ content: Array<{ type: "text"; text: string }> }> {
  // 你的工具逻辑
  const result = "hello";
  return {
    content: [{ type: "text", text: result }]
  };
}

// 导出插件
const myPlugin = {
  id: "my-tool-id",           // 插件唯一ID，openclaw.plugin.json 中的 id 一致
  name: "My Tool",
  description: "工具描述",

  register(api: any) {
    api.registerTool({
      name: "my_tool",         // LLM调用的工具名（蛇形命名）
      label: "我的工具",        // 显示名称
      description: "对LLM的描述，决定了LLM何时调用此工具",  // 重要！
      parameters: {
        type: "object",
        properties: {
          param1: {
            type: "string",
            description: "参数描述"
          }
        },
        required: ["param1"]
      },
      execute: executeMyTool,
    } as any);
  },
};

export default myPlugin;
"""

# ============================================================
# 3. 插件声明：openclaw.plugin.json
# ============================================================

"""
{
  "id": "my-tool-id",          // 与 index.ts 中插件 id 一致
  "name": "My Tool",
  "description": "工具描述",
  "configSchema": {
    "type": "object",
    "additionalProperties": false,
    "properties": {}
  }
}
"""

# ============================================================
# 4. 包信息：package.json
# ============================================================

"""
{
  "name": "@openclaw/my-tool",
  "version": "1.0.0",
  "description": "工具描述",
  "main": "index.ts",
  "files": ["index.ts", "openclaw.plugin.json"],
  "openclaw": {
    "extensions": ["./index.ts"]    // 告诉Gateway加载此文件
  },
  "license": "MIT"
}
"""

# ============================================================
# 5. 注册到 openclaw.json
# ============================================================

"""
需要修改两处：

(1) plugins.entries 中启用插件：
{
  "plugins": {
    "entries": {
      "my-tool-id": {          // 与插件 id 一致
        "enabled": true
      }
    }
  }
}

(2) tools.alsoAllow 中添加工具名：
{
  "tools": {
    "alsoAllow": [
      "my_tool"                // 与 index.ts 中 registerTool name 一致
    ]
  }
}
"""

# ============================================================
# 6. 依赖安装
# ============================================================

"""
cd extensions/你的工具名/
npm install 你的依赖名

注意事项：
- 不要使用全局依赖，全部装在工具目录的 package.json 中
- OpenClaw 内置了 Node.js 的 fs、path 等模块，无需额外安装
"""

# ============================================================
# 7. 重启生效
# ============================================================

"""
修改 openclaw.json 后发送重启信号：
gateway.restart

或 CLI:
openclaw gateway --restart

重启后执行 openclaw doctor --non-interactive 验证
"""

# ============================================================
# 8. 验证
# ============================================================

"""
验证方法：
1. 检查 openclaw.json 中 plugins.entries 和 tools.alsoAllow 配置正确
2. 重启后让 LLM 尝试调用工具
3. 如果 LLM 不主动调用，在 tools.alsoAllow 中添加工具名后重试

注意事项：
- 原生工具（read、exec、edit）优先级不变
- 自定义工具与原生工具可共存
- LLM 根据 description 判断调用哪个工具
- 插件加载失败时 Gateway 一般不会崩溃，但会在日志中报错
"""

# ============================================================
# 实际范例：code-reader 插件
# ============================================================

"""
位置: C:\\Users\\Administrator\\.openclaw\\extensions\\code-reader\\
功能: 代码文件全量读取，支持行号、编码检测、多文件和通配符匹配
注册工具: code_read
"""

print("自定义 OpenClaw 工具开发流程模版已整理")
