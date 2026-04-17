# happy-notes 技能评测指南

> 面向运营和测试同学，介绍如何使用 `skill-creator` 对 `happy-notes` 技能进行 Evals 评测。

---

## 一、什么是 Evals 评测？

Evals（Evaluations）是一套**自动化回归测试**，用来验证 happy-notes 技能在各种用户输入下是否做出了正确的响应。

简单理解：我们预先写好了 **88 条测试用例**，每条包含一个模拟的用户指令和对应的"标准答案"。评测时，系统会逐条把指令发给技能，然后用 AI 裁判自动判断技能的回答是否正确。

**适用场景：**

- 修改了 SKILL.md（技能提示词）后，跑一遍确认没有引入新 Bug
- 新增/调整 Pipeline 脚本后，回归验证历史用例
- 日常迭代中持续监控技能质量

---

## 二、前置准备

### 2.1 环境要求

- 已安装 [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI 工具
- 当前工作目录在 `iflow-skill` 项目根目录下

### 2.2 文件结构

评测相关文件位于：

```
skills/happy-notes/
├── SKILL.md                    # 被测技能的提示词定义
├── evals/
│   └── evals.json              # 评测用例集（88 条）
└── scripts/
    └── pipeline_*.py           # 各 Pipeline 脚本
```

### 2.3 理解评测用例格式

打开 `skills/happy-notes/evals/evals.json`，每条用例结构如下：

```json
{
  "id": 1,
  "category": "P1-KB创建",
  "prompt": "创建一个知识库叫AI论文，把这三篇论文传上去：a.pdf, b.pdf, c.pdf",
  "expected": "调用 Pipeline 1，--name 'AI论文' --files 'a.pdf,b.pdf,c.pdf' --no-generate",
  "anti_pattern": "不得为每个文件分别调用 Pipeline 1 创建多个知识库",
  "expectations": [
    "Response mentions pipeline_create_kb_and_generate.py or Pipeline 1 (P1)",
    "The --files parameter includes all three files (a.pdf, b.pdf, c.pdf) comma-separated",
    "The --name parameter is set to 'AI论文'",
    "Only one pipeline call is made, not three separate calls"
  ]
}
```

| 字段 | 含义 | 是否必填 |
|------|------|---------|
| `id` | 用例编号 | 是 |
| `category` | 分类标签（如 `P1-KB创建`、`P6-联网搜索`） | 是 |
| `prompt` | 模拟的用户输入 | 是 |
| `expected` | 期望的正确行为（自然语言描述） | 是 |
| `anti_pattern` | 禁止出现的错误行为 | 是 |
| `expectations` | 精确断言列表（可选，用于更严格的评判） | 否 |

---

## 三、运行评测

### 3.1 运行全量评测

在 Claude Code 中输入：

```
/skill-creator run evals for happy-notes
```

或直接用自然语言：

```
帮我跑一下 happy-notes 的评测
```

skill-creator 会自动：
1. 读取 `skills/happy-notes/evals/evals.json`
2. 逐条将 `prompt` 发送给 happy-notes 技能
3. 用 AI 裁判对比响应与 `expected` / `anti_pattern` / `expectations`
4. 输出每条用例的 pass/fail 结果

### 3.2 查看评测结果

评测完成后，你会看到类似这样的输出：

```
Eval Results: happy-notes
========================
Total: 88  |  Pass: 82  |  Fail: 6  |  Pass Rate: 93.2%

Failed cases:
  #54 [P2-query混淆] - 把搜索词放在了 --query 里
  #56 [P4-query混淆] - 未区分检索词和创作要求
  ...
```

### 3.3 方差分析（多次运行）

因为 LLM 响应具有随机性，同一条用例多次运行可能结果不同。可以请求多次运行来分析稳定性：

```
帮我跑 3 轮 happy-notes 的评测，做方差分析
```

这会输出每条用例在多次运行中的通过率，帮助识别**不稳定的用例**（有时过有时不过），这些通常是技能提示词需要加强的地方。

---

## 四、评测用例分类总览

当前 88 条用例覆盖以下场景：

| 分类前缀 | 覆盖场景 | 示例用例数 |
|----------|---------|-----------|
| `P1-` | 创建知识库 + 上传文件 + 生成 | 5 条 |
| `P2-` | 知识库内搜索 + 生成 | 3 条 |
| `P3-` | 向已有知识库追加内容 | 9 条 |
| `P4-` | 知识库内语义检索 | 4 条 |
| `P5-` | 文件管理（列出/删除/重命名/重试） | 6 条 |
| `P6-` | 联网搜索 / 深度研究 | 11 条 |
| `直接生成-` | 直接在已有知识库上生成内容 | 7 条 |
| `KB管理-` | 知识库增删改查 | 7 条 |
| `进度查询` | 查询生成任务进度 | 3 条 |
| `分享` | 分享知识库 | 1 条 |
| `搜索分流-` | 判断是否应触发技能 | 4 条 |
| `参数校验-` | 参数映射和混淆场景 | 4 条 |
| `易混淆-` | 容易误判的边界场景 | 5 条 |
| `英文触发` | 英文输入的识别 | 3 条 |
| `错误处理-` | 异常和错误上报 | 2 条 |
| `禁止-` | 不应出现的危险行为 | 2 条 |
| 其他 | 文件限制、状态提示、多步骤等 | 12 条 |

---

## 五、如何新增评测用例

当发现新的 Bug 或需要覆盖新场景时，按以下步骤新增用例。

### 5.1 手动添加

编辑 `skills/happy-notes/evals/evals.json`，在 `evals` 数组末尾追加：

```json
{
  "id": 89,
  "category": "你的分类",
  "prompt": "用户会说的话",
  "expected": "期望技能做什么（用自然语言描述）",
  "anti_pattern": "技能不应该做什么"
}
```

**注意事项：**
- `id` 必须唯一，建议递增
- `category` 尽量复用已有分类，保持一致性
- `prompt` 要写得像真实用户会说的话，不要太规范
- `anti_pattern` 要写明具体的错误行为，而不是泛泛的"不得出错"

### 5.2 借助 skill-creator 添加

也可以直接用自然语言要求 skill-creator 帮你添加：

```
帮 happy-notes 新增一个评测用例：用户说"把上周的会议录音转成文字存到知识库"，
期望是调 Pipeline 3 导入，不应该创建新知识库
```

skill-creator 会自动生成规范格式并写入 evals.json。

### 5.3 添加精确断言（可选）

对于关键用例，可以增加 `expectations` 字段提高评判精度：

```json
{
  "id": 89,
  "category": "P3-音频导入",
  "prompt": "把上周的会议录音转成文字存到知识库",
  "expected": "调用 Pipeline 3 导入文件",
  "anti_pattern": "不得创建新知识库",
  "expectations": [
    "Response mentions pipeline_import_and_generate.py or Pipeline 3 (P3)",
    "Response does NOT create a new knowledge base via Pipeline 1",
    "The --no-generate flag is included"
  ]
}
```

`expectations` 中的每一条都是一个**独立的 pass/fail 断言**，全部通过才算该用例通过。

---

## 六、评判机制说明

评测使用 **LLM-as-Judge**（AI 裁判）机制，而非简单的字符串匹配。

### 工作原理

```
用户 prompt → happy-notes 技能响应 → AI 裁判评判
                                    ├── 对照 expected（应该做什么）
                                    ├── 对照 anti_pattern（不应该做什么）
                                    └── 对照 expectations（精确断言，如果有）
```

### 判定规则

| 情况 | 结果 |
|------|------|
| 响应符合 `expected`，不触犯 `anti_pattern` | Pass |
| 响应触犯了 `anti_pattern` 中的任何一项 | Fail |
| 有 `expectations` 且任一断言未通过 | Fail |

### 为什么用 AI 裁判？

因为 LLM 的输出每次都不完全一样，不能用精确的字符串匹配。AI 裁判能理解语义，判断"调用了 Pipeline 1 创建知识库"和"使用 pipeline_create_kb_and_generate.py 新建 KB"表达的是同一件事。

---

## 七、评测最佳实践

### 7.1 什么时候跑评测？

| 时机 | 建议 |
|------|------|
| 修改 SKILL.md 后 | **必跑**，这是最容易引入回归的操作 |
| 修改 Pipeline 脚本后 | 建议跑相关分类的用例 |
| 新增功能后 | 先补用例，再跑全量 |
| 日常巡检 | 建议每周跑一次全量 |

### 7.2 用例编写原则

1. **从真实 Bug 出发**：每个 `anti_pattern` 都应该来自一个真实发生过的错误
2. **覆盖决策边界**：重点测试容易混淆的场景（如 P2 vs P4、P1 vs P3、P6 vs 不触发）
3. **一条用例一个关注点**：不要在一条用例里测太多东西
4. **保持 prompt 自然**：用真实用户的说法，包括口语化、省略、歧义

### 7.3 评测失败后怎么办？

1. **分析失败原因**：看 AI 裁判的具体评判理由
2. **判断是技能问题还是用例问题**：
   - 技能问题 → 修改 SKILL.md 中的提示词，加强对应场景的引导
   - 用例问题 → 修改 evals.json 中的 `expected` 或 `anti_pattern`
3. **修复后重跑**：确认修复有效且没有引入新的失败

---

## 八、常见问题

**Q: 评测需要消耗 iflow API 配额吗？**
A: 评测过程中技能会调用 Pipeline 脚本，但 skill-creator 的 eval 模式通常是检查技能的"决策"（选了哪个 Pipeline、传了什么参数），不一定会真正执行到 iflow 后端。具体取决于评测的运行模式。

**Q: 一次评测大概需要多久？**
A: 88 条用例全量评测通常需要几分钟到十几分钟，取决于模型响应速度。

**Q: 可以只跑某个分类的用例吗？**
A: 可以，在跑评测时指定分类：
```
帮我只跑 happy-notes 中 P6 相关的评测用例
```

**Q: expectations 和 expected/anti_pattern 有什么区别？**
A: `expected` 和 `anti_pattern` 是自然语言描述，AI 裁判自行理解和判断；`expectations` 是精确的逐条断言，每条独立判 pass/fail，更严格。建议对核心路径的用例加上 `expectations`。

**Q: 我不会写代码，能添加用例吗？**
A: 完全可以。你只需要知道"用户会说什么"和"技能应该做什么/不应该做什么"，用自然语言告诉 skill-creator 即可，它会帮你生成 JSON 格式。
