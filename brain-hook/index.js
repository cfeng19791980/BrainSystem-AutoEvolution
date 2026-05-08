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

      log(`User content length: ${userContent.length}, preview: ${userContent.slice(0, 80)}`);

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
          return {
            prependSystemContext: result.processed_content,
            appendSystemContext: result.processed_content,
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
