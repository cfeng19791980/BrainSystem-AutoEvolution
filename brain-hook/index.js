// Brain Hook V9.3 - Sidecar 模式，通过 Gateway WebSocket 订阅 before_prompt_build 事件
// 这个文件由 sidecar 进程加载，拥有自己的 HTTP server
const http = require('http');
const fs = require('fs');
const path = require('path');

const BRAIN_PORT = 5002;
const LOG_FILE = path.join(process.env.USERPROFILE || 'C:\\Users\\10341', '.openclaw', 'logs', 'brain-hook.log');

function log(msg) {
  const ts = new Date().toISOString();
  const line = `[${ts}] ${msg}\n`;
  console.log(`[brain-hook] ${msg}`);
  try { fs.appendFileSync(LOG_FILE, line, 'utf-8'); } catch(e) {}
}

log('V9.3 Loading');

module.exports = {
  id: "brain-hook",
  register(api) {
    log('register() called');

    api.on('before_prompt_build', async (event) => {
      log(`before_prompt_build triggered, messages: ${event.messages?.length || 0}`);

      if (!event.messages?.length) {
        log('No messages, skip');
        return;
      }

      const lastUserMsg = event.messages.filter(m => m.role === 'user').pop();
      if (!lastUserMsg) {
        log('No user message, skip');
        return;
      }

      let userContent = '';
      if (typeof lastUserMsg.content === 'string') {
        userContent = lastUserMsg.content;
      } else if (lastUserMsg.content?.[0]?.text) {
        userContent = lastUserMsg.content[0].text;
      } else if (lastUserMsg.content?.text) {
        userContent = lastUserMsg.content.text;
      }

      if (!userContent || userContent.length < 10) {
        log('Content too short, skip');
        return;
      }

      try {
        log('Calling Brain /entry...');
        const result = await callBrainEntry(userContent.slice(0, 80000));

        if (result && result.success && result.processed_content) {
          log(`Brain OK: intent=${result.brain_context?.intent?.type}, conf=${result.brain_context?.intent?.confidence}, len=${result.processed_content.length}`);

          // Inject via multiple fields to ensure at least one works
          // Add a local identity notice and tool description so the model knows it's running locally
          // and can access files through the Brain Tool API
          const toolDescription = `

## 本地身份说明 (LOCAL IDENTITY NOTICE)

重要：你正在用户的本地机器上通过 LM Studio 运行（qwen3-vl 本地模型）。
你是本地助手，不是云端 AI，具备以下本地文件访问能力：

### 可用工具 (通过 Brain Tool API)

当你需要读取文件或列出目录时，用户的后台系统（Brain）可以直接执行 JavaScript 代码
或直接读取文件。你有以下方式获取本地文件：

1. **run_javascript (Brain 内置)** - 通过 Brain 的 /tools/run_js 端点，
   可以在本地 Deno 沙箱中执行 JavaScript/TypeScript 代码。
   Deno 具有对 E:/, D:/, C:/Users/ 的只读访问权限。
   示例代码：\`Deno.readTextFileSync("E:/some/file.txt")\`

2. **read_file (Brain 内置)** - 通过 Brain 的 /tools/read_file 端点，
   可以直接读取 E:/, D:/, C:/Users/ 路径下的文件。

3. **list_dir (Brain 内置)** - 通过 Brain 的 /tools/list_dir 端点，
   可以列出本地目录内容。

### 注意事项
- 你完全有能力访问用户的本地文件系统（E盘中包含 brain-system 等数据）。
- 当用户请求访问本地文件时，直接使用 run_javascript 工具执行 Deno 代码。
- 不要声称自己无法访问本地文件——你能，通过 run_javascript 工具。
- 所有操作在用户的本地机器上执行，不会发送数据到云端。
`;
          // 编码规范
          const codingRules = `

## 编码规范 (请严格遵守)
一、所有代码必须设置UTF8编码
二、先思考再编写代码，明确用户需求，避免自作假设。
三、简单优先，只实现当前任务所需的最少代码，避免过度工程化。例如 200 行代码能用 50 行完成，就应简化。
四、外科手术式修改，只动必须动的部分，不顺手改动相邻代码或格式，也不重构未损坏的功能。每行修改都应可追溯到用户请求。
五、目标驱动执行，将任务拆解为明确可验证的目标，例如"添加验证"应转化为"先为无效输入写测试，然后让它们通过"。
六、先备份后修改可回滚，做好版本管理。
七、编码测试完成后，清理临时文件（如测试脚本/修复脚本等），保持文件架构整洁。
`;
          const enhancedContent = result.processed_content + toolDescription + codingRules;
          return {
            prependSystemContext: enhancedContent,
            appendSystemContext: enhancedContent,
            prependContext: result.processed_content
          };
        } else {
          log(`Brain response: success=${result?.success}, has content=${!!result?.processed_content}`);
        }
      } catch (err) {
        log(`API error: ${err.message}`);
      }

      log('Hook completed without injection');
    });

    log('V9.3 Ready');
  }
};

function callBrainEntry(content) {
  return new Promise((resolve, reject) => {
    const postData = JSON.stringify({ content });
    const options = {
      hostname: '127.0.0.1',
      port: BRAIN_PORT,
      path: '/entry',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(postData)
      },
      timeout: 15000
    };
    const req = http.request(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try { resolve(JSON.parse(data)); }
        catch (e) { log(`JSON parse error: ${e.message}`); reject(new Error('Invalid JSON')); }
      });
    });
    req.on('error', (e) => { log(`Request error: ${e.message}`); reject(e); });
    req.on('timeout', () => { log('Request timeout'); req.destroy(); reject(new Error('Timeout')); });
    req.write(postData);
    req.end();
  });
}
