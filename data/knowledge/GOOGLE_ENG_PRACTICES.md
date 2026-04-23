# Google Engineering Practices - Code Review

## 来源
- **官方链接**: https://google.github.io/eng-practices/review/
- **权威性**: Google官方工程实践标准
- **适用范围**: 全行业顶级标准

---

## 核心原则

### The Golden Rule

> **Reviewers should favor approving a CL once it definitely improves overall code health, even if not perfect.**

关键点:
- 没有"完美代码"，只有"更好的代码"
- 追求持续改进，不是完美
- CL整体改善系统可维护性 → 应批准
- 不要因为"不完美"延迟数天/数周

---

## 审查清单

| 维度 | 检查点 |
|------|--------|
| **Design** | 是否设计良好？是否适合系统？ |
| **Functionality** | 行为是否正确？对用户是否友好？ |
| **Complexity** | 能否更简单？其他开发者能否理解？ |
| **Tests** | 是否有正确的自动化测试？ |
| **Naming** | 变量/类/方法命名是否清晰？ |
| **Comments** | 注释是否清晰有用？ |
| **Style** | 是否遵循Style Guide？ |
| **Documentation** | 是否更新相关文档？ |

---

## Reviewer原则

| 原则 | 说明 |
|------|------|
| **Technical facts > Opinions** | 技术事实优于个人意见 |
| **Style guide authority** | Style Guide是绝对权威 |
| **Design principles** | 软件设计基于原则，非偏好 |
| **Consistency** | 无规则时保持一致性 |

---

## Nit评论

> **Prefix: "Nit:"**

用途:
- 非关键性改进建议
- 教育性评论（非强制性）
- 作者可选择忽略

示例:
```
Nit: 这个变量名可以更具体，比如用userCount代替count
```

---

## 冲突解决

### 步骤

```
1. Developer + Reviewer → 共识
2. 难达成 → 面对面/视频会议
3. 记录讨论结果 → CL评论
4. 仍未解决 → 升级Tech Lead/Maintainer
```

---

## 最佳Reviewer选择

| 标准 | 说明 |
|------|------|
| **能力** | 最彻底、最正确的审查 |
| **响应时间** | 合理时间内响应 |
| **代码所有权** | 通常是代码Owner |
| **不可用时** | 至少CC他们 |

---

## Brain系统Pattern映射

| Pattern ID | 内容 |
|------------|------|
| google_core_principle | CL批准标准 |
| google_review_checklist | 8维度审查清单 |
| google_reviewer_principles | 4原则 |
| google_cl_size | 小CL原则 |
| google_conflict_resolution | 冲突解决流程 |
| google_nit_comments | Nit标记用法 |
| google_best_reviewer | Reviewer选择标准 |
| google_mentor_function | 知识传授功能 |

---

**导入时间**: 2026-04-23 22:44
**embeddings**: +8条
**总embeddings**: 98条
**署名**: 付郁 (cfeng19791980)