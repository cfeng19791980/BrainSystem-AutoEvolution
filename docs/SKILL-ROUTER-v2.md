# SKILL-ROUTER-v2

## 技能路由规则

### 0. Brain 系统技能（最高优先级）
| 关键词 | 优先级 | 技能 | 描述 | 自主调用 |
|--------|--------|------|------|----------|
| `brain` | 0 | `brain_entry.py` | Brain智能决策系统（知识检索+上下文增强+意图分析），100%触发 | ✅ P0自主 |

### 1. 搜索相关技能
| 关键词 | 优先级 | 技能 | 描述 |
|--------|--------|------|------|
| `反爬搜索` | 1 | `agent-browser` | 反爬模式浏览器搜索，使用 CDP + 反爬检测绕过 |
| `搜索` | 2 | `unified-search` | 统一搜索 v2，集成代理池和缓存机制，智能选择最佳方案 |
| `web_search` | 3 | `web-search-free` | 免费网页搜索（Playwright版） |
| `多引擎搜索` | 4 | `multi-search-engine` | 多搜索引擎集成 |
| `web_fetch` | 5 | - | 原生网页获取工具 |

### 2. 开发相关技能（自主调用）
| 关键词 | 优先级 | 技能 | 描述 | 自主调用 |
|--------|--------|------|------|----------|
| `架构设计` | 1 | `architect` | 系统架构师（技术选型+架构文档+ADR） | ✅ P1自主 |
| `技术选型` | 1 | `architect` | 技术栈选型决策（评估+对比+决策） | ✅ P1自主 |
| `架构师` | 1 | `architect` | 系统架构师角色（架构设计+评审+演进） | ✅ P1自主 |
| `需求分析` | 1 | `requirements-analyst` | 需求分析师（需求收集+PRD文档+用户故事） | ✅ P1自主 |
| `PRD文档` | 1 | `requirements-analyst` | 产品需求文档编写 | ✅ P1自主 |
| `用户故事` | 1 | `requirements-analyst` | User Story编写（验收标准+估时） | ✅ P1自主 |
| `需求文档` | 1 | `requirements-analyst` | 需求文档编写（PRD+用例+原型） | ✅ P1自主 |
| `代码` | 1 | `coding-agent` | 代码编写助手 | ✅ P1自主 |
| `调试` | 2 | `code-debug` | 代码调试 | ✅ P1自主 |
| `代码审查` | 1 | `code-review` | 代码审查与优化建议 | ✅ P1自主 |
| `重构` | 1 | `refactoring` | 代码重构优化 | ✅ P1自主 |
| `性能优化` | 1 | `performance` | 性能分析与优化 | ✅ P1自主 |
| `单元测试` | 1 | `unit-test` | 编写与运行单元测试 | ✅ P0自主 |
| `集成测试` | 2 | `integration-test` | 集成测试验证 | ✅ P0自主 |
| `文档生成` | 2 | `doc-gen` | 自动生成文档 | ✅ P1自主 |
| `错误分析` | 1 | `error-analysis` | 错误堆栈分析 | ✅ P0自主 |
| `github` | 3 | `github` | GitHub操作 | ✅ P2说明 |
| `git` | 4 | `code` | 版本控制 | ✅ P1自主 |

### 3. 自动化技能
| 关键词 | 优先级 | 技能 | 描述 |
|--------|--------|------|------|
| `智能登录` | 1 | `enhanced-browser-agent` | 智能登录管理（自动检测+交互式登录+状态保存），支持知乎/BOSS/智联 |
| `智能Cookie` | 1 | `enhanced-browser-agent` | 智能Cookie管理（自动检测登录状态+自动保存/恢复+交互式引导） |
| `自动登录` | 1 | `enhanced-browser-agent` | 自动登录系统（检测→恢复→交互→保存），完整登录状态生命周期 |
| `登录状态` | 1 | `enhanced-browser-agent` | 登录状态管理（保存/加载/验证/自动回填），支持多站点 |
| `视觉` | 1 | `enhanced-browser-agent` | 视觉爬虫（OCR截图识别），智能识别任务内容自动执行 |
| `视觉采集` | 1 | `enhanced-browser-agent` | 视觉数据采集（免费OCR+PaddleOCR），自动识别页面内容 |
| `视觉搜索` | 1 | `enhanced-browser-agent` | 视觉搜索（截图+OCR识别），绕过DOM反爬 |
| `视觉爬虫` | 1 | `enhanced-browser-agent` | 视觉爬虫自动化（浏览器+OCR+智能识别任务） |
| `OCR采集` | 1 | `enhanced-browser-agent` | OCR数据采集（免费PaddleOCR），识别图片/页面文字 |
| `截图识别` | 1 | `enhanced-browser-agent` | 截图文字识别（免费OCR方案），视觉理解页面内容 |
| `浏览器` | 1 | `enhanced-browser-agent` | 增强浏览器代理 V3（0 Bug认证），多标签+反检测+数据持久化 |
| `多标签浏览器` | 1 | `enhanced-browser-agent` | 多标签浏览器自动化（单Chrome进程，66%内存节省） |
| `浏览器V3` | 1 | `enhanced-browser-agent` | 浏览器自动化 V3 版本（CDP+智能导航+反爬） |
| `enhanced-browser` | 1 | `enhanced-browser-agent` | Enhanced Browser Agent V3（生产就绪） |
| `glm` | 2 | `autoglm-browser-agent` | AutoGLM 智能浏览器代理，AI控制浏览器执行任务 |
| `autoglm` | 2 | `autoglm-browser-agent` | AutoGLM 智能浏览器代理，AI控制浏览器执行任务 |
| `智能浏览器代理` | 2 | `autoglm-browser-agent` | 智能浏览器代理（qwen3.5-plus模型驱动） |
| `浏览器滚动` | 1 | `enhanced-browser-agent` | 浏览器智能滚动（模拟人类行为+自动加载+内容采集） |
| `自动滚动` | 1 | `enhanced-browser-agent` | 自动滚动页面（分段滚动+随机延迟+检测到底） |
| `滚动采集` | 1 | `enhanced-browser-agent` | 滚动并采集内容（先滚动加载全部，再提取内容） |
| `自动化` | 2 | `automation-workflows` | 工作流自动化 |
| `浏览器机器人` | 1 | `super-ai-browser-bot` | 超级AI浏览器RPA机器人 |
| `RPA` | 1 | `super-ai-browser-bot` | 机器人流程自动化 |
| `浏览器自动化` | 2 | `super-ai-browser-bot` | 浏览器自动化（表格导出+翻页+登录） |
| `AI浏览器` | 2 | `super-ai-browser-bot` | AI控制浏览器 |
| `浏览器截图` | 2 | `super-ai-browser-bot` | 浏览器截图功能（视口/全页/元素） |
| `浏览器搜索` | 2 | `super-ai-browser-bot` | 浏览器搜索功能（百度搜索+第二层详情） |
| `浏览器提取` | 2 | `super-ai-browser-bot` | 浏览器数据提取（链接/表格/图片/文本） |
| `浏览器填表` | 2 | `super-ai-browser-bot` | 浏览器自动填表功能 |
| `浏览器登录` | 2 | `super-ai-browser-bot` | 浏览器自动登录功能 |
| `智能浏览器` | 1 | `super-ai-browser-bot` | 智能浏览器机器人（自然语言理解+自动启动） |
| `桌面控制V2` | 1 | `desktop-control-v2` | AI桌面自动化（4层智能定位+贝塞尔曲线+自愈+自适应反检测），最强反爬方案 |
| `桌面自动化` | 1 | `desktop-control-v2` | 桌面自动化V2（人类-like操作+OCR+虚拟桌面），模拟真人绕过所有检测 |
| `AI桌面控制` | 1 | `desktop-control-v2` | AI驱动桌面控制（AI视觉定位+智能恢复+动态伪装），BOSS直聘克星 |
| `增强桌面` | 1 | `desktop-control-v2` | 增强桌面控制（AI+人类行为模拟+自愈+反检测），超越浏览器自动化的终极方案 |
| `桌面控制` | 3 | `desktop-control` | 桌面控制 |
| `浏览器自动化` | 4 | `agent-browser` | 浏览器自动化 |
| `浏览器求职` | 1 | `browser-job-automation` | 浏览器求职自动化（职位搜索+简历投递+申请管理） |
| `求职浏览器` | 1 | `browser-job-automation` | 求职专用浏览器自动化（多平台职位申请） |
| `职位搜索` | 2 | `browser-job-automation` | 多平台职位搜索（BOSS直聘+智联招聘） |
| `简历投递` | 2 | `browser-job-automation` | 自动简历投递（批量申请+智能筛选） |
| `求职申请` | 2 | `browser-job-automation` | 求职申请管理（申请跟踪+统计报告） |
| `浏览器+职位` | 3 | `browser-job-automation` | 浏览器+求职相关动作（智能解析用户意图） |
| `浏览器+求职` | 3 | `browser-job-automation` | 浏览器+求职动作（搜索/申请/管理） |

### 4. 测试相关技能（自主调用）
| 关键词 | 优先级 | 技能 | 描述 | 自主调用 |
|--------|--------|------|------|----------|
| `自动测试` | 1 | `auto-test-agent` | 全自动测试系统（AI驱动+浏览器/API测试+报告） | ✅ P0自主 |
| `auto-test` | 1 | `auto-test-agent` | Auto Test Agent v2.0（探索生成+并发执行+AI分析） | ✅ P0自主 |
| `测试系统` | 1 | `auto-test-agent` | 自动化测试系统（Playwright+mitmproxy+AI分析） | ✅ P0自主 |
| `自动化测试` | 2 | `qa-automation` | 自动化测试专家（测试框架+脚本+报告） | ✅ P0自主 |
| `测试脚本` | 2 | `qa-automation` | 测试脚本开发（Jest/Playwright） | ✅ P1自主 |
| `测试框架` | 2 | `qa-automation` | 测试框架设计（单元/接口/UI） | ✅ P1自主 |
| `测试计划` | 2 | `qa-automation` | 测试计划编写（策略+环境+范围） | ✅ P1自主 |
| `Playwright` | 2 | `qa-automation` | Playwright E2E测试 | ✅ P1自主 |
| `Jest` | 2 | `qa-automation` | Jest单元测试 | ✅ P0自主 |
| `E2E测试` | 2 | `qa-automation` | E2E端到端测试 | ✅ P1自主 |
| `单元测试` | 2 | `qa-automation` | 单元测试开发 | ✅ P0自主 |

### 5. 数据与分析技能
| 关键词 | 优先级 | 技能 | 描述 |
|--------|--------|------|------|
| `股票` | 1 | `stock-analysis` | 股票分析 |
| `天气` | 2 | `tianqi-weather` | 天气预报 |
| `数据分析` | 3 | `research` | 研究分析 |
| `地图` | 4 | `evomap` | 进化地图 |

### 6. 文档处理技能（自主调用）
| 关键词 | 优先级 | 技能 | 描述 | 自主调用 |
|--------|--------|------|------|----------|
| `office` | 1 | `office-document-specialist-suite` | Office文档处理（Word/Excel/PPT自动化） | ✅ P1自主 |
| `Word` | 1 | `office-document-specialist-suite` | Word文档创建与编辑（专业排版+模板） | ✅ P1自主 |
| `Excel` | 1 | `office-document-specialist-suite` | Excel数据处理（表格+数据分析） | ✅ P1自主 |
| `PPT` | 1 | `office-document-specialist-suite` | PowerPoint演示文稿（自动创建幻灯片） | ✅ P1自主 |
| `文档` | 2 | `office-document-specialist-suite` | Office文档操作（创建/编辑/分析） | ✅ P1自主 |
| `报告` | 2 | `office-document-specialist-suite` | 专业报告生成（Word模板+排版） | ✅ P1自主 |

### 7. 个人助理技能
| 关键词 | 优先级 | 技能 | 描述 |
|--------|--------|------|------|
| `简历` | 1 | `resume-job-matcher` | 简历与工作匹配 |
| `学习` | 2 | `education` | 教育辅助 |
| `写作` | 3 | `writing` | 写作助手 |
| `记忆` | 4 | `elite-longterm-memory` | 长期记忆 |

### 8. 团队协作技能（自主调用）
| 关键词 | 优先级 | 技能 | 描述 | 自主调用 |
|--------|--------|------|------|----------|
| `团队开发` | 1 | `team-development` | 一人领导三人团队协作开发（需求→架构→测试→开发→验证） | ✅ P1自主 |
| `三人团队` | 1 | `team-development` | 三人团队协作开发（Lisa需求+Alex架构+Tom测试） | ✅ P1自主 |

### 9. 系统技能
| 关键词 | 优先级 | 技能 | 描述 |
|--------|--------|------|------|
| `技能管理` | 1 | `find-skills` | 技能查找与管理 |
| `配置` | 2 | `core` | 核心配置 |
| `更新` | 3 | `skillhub-preference` | 技能中心 |

### 自主调用规则（Phase 3新增）

**调用原则**：
- P0任务：直接调用技能执行，无需说明
- P1任务：调用技能+记录决策日志
- P2任务：简要说明+调用技能
- P3任务：请示确认+调用技能

**调用示例**：
```
用户: "帮我修复这个bug"
→ 评估: P1（修改代码）
→ 调用: coding-agent（自主）
→ 执行: 修复代码
→ 记录: DECISION.md
→ 测试: 验证修复
→ 输出: 结果报告
```

```
用户: "审查这段代码"
→ 评估: P1（代码审查）
→ 调用: code-review（自主）
→ 执行: 审查并输出建议
→ 记录: DECISION.md
→ 输出: 审查报告
```

### 匹配规则
1. **精确匹配优先**：完全匹配关键词的技能优先
2. **前缀匹配**：用户消息以关键词开头
3. **内容匹配**：消息中包含关键词
4. **语义匹配**：相近含义的关键词

### 冲突解决
1. 相同优先级按字母顺序
2. 用户可以指定技能名称
3. 可以手动路由到特定技能

## 新增技能注册

新技能应在此文件中注册：
1. 确定技能类别
2. 定义关键词
3. 设置优先级（1-10，1最高）
4. 提供简短描述
5. **指定入口文件路径**

## 技能入口文件映射

| 技能名称 | 入口文件路径 | 说明 |
|----------|-------------|------|
| `brain_entry` | `C:/Users/Administrator/.openclaw/workspace-工程师/brain_entry.py` | Brain智能决策系统入口 |
| `agent-browser` | `skills/agent-browser/agent.py` | 反爬浏览器 |
| `unified-search` | `skills/unified-search/search.py` | 统一搜索 |
| `coding-agent` | `skills/coding-agent/coder.py` | 代码助手 |
| `enhanced-browser-agent` | `skills/enhanced-browser-agent/browser.py` | 增强浏览器 |

## 示例

```
用户: "反爬搜索 福州房价"
→ 匹配: "反爬搜索" → `agent-browser` (优先级1)

用户: "搜索福州养老政策"
→ 匹配: "搜索" → `unified-search` (优先级2)

用户: "帮我写代码"
→ 匹配: "代码" → `coding-agent` (优先级1)

用户: "今天天气怎么样"
→ 匹配: "天气" → `tianqi-weather` (优先级2)
```

## 维护说明

- 定期更新关键词列表
- 根据使用频率调整优先级
- 合并相似功能的技能
- 标记已废弃的技能

## 版本历史

- **v3.6** (2026-04-21): ✅ **Brain 系统技能注册** - 新增 `brain-entry` 技能（Brain智能决策系统），关键词：`brain`、`大脑`、`智能决策`、`知识检索`、`记忆搜索`，优先级0（最高），100%触发Brain系统
- **v3.5** (2026-04-18): ✅ **Auto Test Agent 技能注册** - 新增 `auto-test-agent` 技能（全自动测试系统），关键词：`自动测试`、`auto-test`、`测试系统`，支持 AI驱动用例生成 + 并发执行 + 根因分析 + HTML报告
- **v3.4** (2026-04-18): ✅ **Office文档技能注册** - 新增 `office-document-specialist-suite` 技能（Word/Excel/PPT自动化），关键词：`office`、`Word`、`Excel`、`PPT`、`文档`、`报告`
- **v3.3** (2026-04-16): ✅ **Desktop Control V2 发布** - 新增 `desktop-control-v2` 技能，AI驱动的桌面自动化（4层智能定位+贝zier曲线+90%自愈+自适应反检测），BOSS直聘等强反爬站点的终极解决方案
- **v3.2** (2026-04-16): ✅ **功能增强完成** - 新增 5 个站点配置、验证码识别、数据导出(Excel/CSV/Markdown)、定时任务、OCR 自动安装脚本
- **v3.1** (2026-04-16): ✅ **智能登录 V2** - 新增自动检测登录动作、自动保存状态、自动识别和自动回填功能
- **v3.0** (2026-04-16): ✅ **架构重构完成** - enhanced-browser-agent 升级为插件化架构 (BrowserAgent + Plugins)，代码耦合度降低70%，扩展性提升10x
- **v3.0** (2026-04-15): ✅ **架构重构完成** - enhanced-browser-agent 升级为插件化架构 (BrowserAgent + Plugins)，代码耦合度降低70%，扩展性提升10x
- **v2.9** (2026-04-15): 添加智能滚动功能到 enhanced-browser-agent，关键词：`浏览器滚动`、`自动滚动`、`滚动采集` - 支持模拟人类滚动行为、自动加载、滚动+采集一体化
- **v2.8** (2026-04-15): 添加智能Cookie管理功能到 enhanced-browser-agent，关键词：`智能登录`、`智能Cookie`、`自动登录`、`登录状态` - 支持自动检测、交互式登录、状态保存/恢复
- **v2.7** (2026-04-15): 添加视觉爬虫关键词到 enhanced-browser-agent，支持智能任务识别：`视觉`、`视觉采集`、`视觉搜索`、`视觉爬虫`、`OCR采集`、`截图识别`
- **v2.6** (2026-04-15): 添加 enhanced-browser-agent 技能（0 Bug认证），关键词：`增强浏览器`、`多标签浏览器`、`浏览器V3`、`enhanced-browser`
- **v2.5** (2026-04-15): 添加 autoglm-browser-agent 技能，关键词：`glm`、`autoglm`、`智能浏览器代理`
- **v2.4** (2026-04-14): 反爬搜索关键词绑定到 agent-browser，使用 CDP 协议实现反爬检测绕过
- **v2.3** (2026-04-14): 更新搜索优先级，将"反爬搜索"设为最高优先级(1)
- **v2.2** (2026-04-09): 扩展超级AI浏览器机器人功能，添加五个独立功能
- **v2.1** (2026-04-09): 添加超级AI浏览器RPA机器人技能
- **v2.0** (2026-04-07): 创建统一搜索路由
- **v1.0**: 初始版本

---

**注意**: 此文件是技能调用的主要参考，确保所有技能都正确注册。