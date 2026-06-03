---
name: happy-notes-reports
description: 内容生成子技能，支持 PDF/DOCX/MARKDOWN/PPT/XMIND/PODCAST/VIDEO/HHVIDEO/QUIZ/GRAPH/TRANSLATION/PPT_EDIT 十二种产出类型的创建、状态查询和进度展示。
---

# Reports (内容生成)

> Prerequisites: see root `../SKILL.md` for setup, credentials, and `iflow_api()` helper.

基于知识库中选定的文件，生成多种类型的内容产出。这是 iflow 的核心差异化能力。

完整数据结构和接口参数详见 `references/api.md`。

## 十二种产出类型

| type 值 | 产出类型 | 说明 | 预估耗时 | 等待策略 |
|---------|---------|------|---------|---------|
| `PDF` | PDF 报告 | 生成 PDF 格式报告 | 10-20分钟 | 异步，不阻塞 |
| `DOCX` | Word 报告 | 生成 Word 格式报告 | 10-20分钟 | 异步，不阻塞 |
| `MARKDOWN` | Markdown 报告 | 生成 Markdown 格式报告（支持 7 种类型变体，见「query 内容传达指引」） | 10-20分钟 | 异步，不阻塞 |
| `PPT` | 演示文稿 | 支持 `preset`：`"商务"` / `"卡通"` | 15-30分钟 | 异步，不阻塞 |
| `XMIND` | 思维导图 | — | 15-30分钟 | 异步，不阻塞 |
| `PODCAST` | 播客 | 支持时长（3-30 分钟）、单/双口、10 种音色、调性（由 query 描述，LLM 自动推断） | 10-20分钟 | 异步，不阻塞 |
| `VIDEO` | 视频（有声 PPT 讲解） | TTS 旁白 + PPT 页面演示 | 15-30分钟 | 异步，不阻塞 |
| `HHVIDEO` | AI 视频（**v2 新增**） | 支持 T2V / I2V / Seed 三种模式，通过 `videoConfig` 显式配置 | 5-15分钟 | 异步，不阻塞 |
| `QUIZ` | 多选题（**v2 新增**） | 自动生成 N 道题，含 4 选项 + 正确答案 + 解释；题量/难度由 query 描述 | 5-10分钟 | 异步，不阻塞 |
| `GRAPH` | 信息图（**v2 新增**） | 单张数据可视化图；风格（minimal/cartoon/cool）+ 尺寸（方/横/竖）由 query 描述 | 5-10分钟 | 异步，不阻塞 |
| `TRANSLATION` | 文件翻译（**v2 新增**） | 支持 PDF/DOCX/MD/TXT 互译，10 种语言；源/目标语言由 query 描述 | 5-20分钟 | 异步，不阻塞 |
| `PPT_EDIT` | PPT 增量编辑（**v2 新增**） | 基于已有 PPT + 用户编辑指令做修改；**依赖前序 PPT 上下文** | 10-20分钟 | 异步，不阻塞 |

> **注意**: `PDF`/`DOCX`/`MARKDOWN` 都是报告的不同输出格式。用户没指定格式时默认使用 `PDF`。
>
> **`VIDEO` vs `HHVIDEO`**：`VIDEO` 是 TTS 旁白 + PPT 页面演示（"有声 PPT"）；`HHVIDEO` 是真正的 AI 视频生成。用户说"做个视频"时倾向于 `HHVIDEO`；说"配音演示"、"讲解视频"时用 `VIDEO`。

## 意图识别与参数映射

| 用户说的 | type | preset | 说明 |
|---------|------|--------|------|
| "生成报告"/"写份报告" | `PDF` | — | 未指定格式时默认 PDF |
| "导出 Word" | `DOCX` | — | — |
| "生成 Markdown 报告" | `MARKDOWN` | — | — |
| "写篇博客"/"做篇公众号文章" | `MARKDOWN` | — | 通过 query 完整传达"博客/公众号"等关键词，下游 LLM 会识别为 `blog_article` 类型 |
| "深度研究"/"调研报告" | `MARKDOWN` | — | 下游识别为 `deep_research` 类型 |
| "文献综述"/"文献回顾" | `MARKDOWN` | — | 下游识别为 `literature_review` 类型 |
| "审稿意见"/"论文 review" | `MARKDOWN` | — | 下游识别为 `shadow_review` 类型 |
| "高管简报"/"执行摘要"/"给老板看的总结" | `MARKDOWN` | — | 下游识别为 `executive_summary` 类型 |
| "学习指南"/"教学材料"/"考点整理" | `MARKDOWN` | — | 下游识别为 `study_guide` 类型 |
| "按 SWOT 写"/"分 5 段" | `MARKDOWN` | — | 下游识别为 `custom_format` 自定义结构 |
| "做个PPT"/"生成演示文稿" | `PPT` | `"商务"` | 默认商务风格 |
| "做个活泼的PPT"/"卡通风格" | `PPT` | `"卡通"` | 关键词触发 |
| "生成播客"/"做个播客" | `PODCAST` | — | 用户提到的时长/音色/单双口/调性需**完整保留在 query** |
| "做个 10 分钟的女声轻松风格播客" | `PODCAST` | — | query 必须包含"10 分钟""女声""轻松"，不能简化 |
| "生成思维导图"/"画个脑图" | `XMIND` | — | — |
| "生成视频"/"做个视频" | `HHVIDEO` | — | **默认走 HHVIDEO**（AI 视频）；如果用户明确说"讲解视频/配音演示"才用 `VIDEO` |
| "做个 AI 视频"/"生成短视频" | `HHVIDEO` | — | 默认 T2V 文生视频，传 `--video-images` 切 I2V/Seed |
| "用这几张图生成视频" | `HHVIDEO` | — | 传 `--video-images --video-image-type reference`（I2V） |
| "用这张图作为开头做视频" | `HHVIDEO` | — | 传 `--video-images --video-image-type first_frame`（Seed） |
| "出几道题"/"做个测验"/"考考我" | `QUIZ` | — | 用户说的题量/难度（"10 道"/"难一点"）**必须完整传到 query** |
| "做张信息图"/"数据可视化" | `GRAPH` | — | 用户说的风格（卡通/极简/酷炫）和尺寸（方/横/竖）**必须完整传到 query** |
| "翻译这个文档"/"译成英文"/"中译英" | `TRANSLATION` | — | 用户说的源/目标语言**必须完整传到 query** |
| "修改这页 PPT"/"重做第 N 页" | `PPT_EDIT` | — | **依赖前序 PPT 上下文**，需要 Agent 知道当前会话已经生成过 PPT |
| "同时生成报告和PPT" | 多个 | — | 并行提交 |
| "帮我总结一下" | `PDF` | — | 总结 = 报告，通过 query 描述总结要求 |
| "对比分析这两篇论文" | `PDF` | — | 通过 query 传达分析要求 |

> **PPT 风格引导**：用户要求生成 PPT 但未指定风格时，Agent 应主动询问：「PPT 有**商务**和**卡通**两种风格，您想用哪种？默认使用商务风格。」用户说"随便"或不选择时使用商务。

## query 内容传达指引（⚠️ 重要）

iflow-notebook 内部会从 user_query 文本中通过 LLM 推断各种创作维度配置（时长 / 音色 / 难度 / 风格 / 字数 / 语言 / 调性等），**接口层只接受 type 字符串 + query 文本，没有这些维度的显式参数**（HHVIDEO 的 videoConfig 是唯一例外）。

**这意味着：Agent 不能简化 query 丢失用户信息**，否则下游 LLM 推断时拿不到完整信息，输出质量下降。

| 类型 | 用户说到这些信息时必须完整保留在 query | 反例（❌ 错误简化） | 正例（✅ 完整保留） |
|---|---|---|---|
| **MARKDOWN** | 类型变体（"深度研究"/"文献综述"/"审稿"/"高管简报"/"学习指南"/"博客"/"SWOT/PEST/MECE 等结构"）；字数（"2 万字"）；语言（"英文"）；调性（"犀利"/"专业"/"通俗"） | "给我写一份关于 X 的文献综述，2 万字，专业语气" → query 写成"写报告" | "给我写一份关于 X 的**文献综述**，**2 万字**，**专业语气**" |
| **PODCAST** | 时长（"10 分钟"/"30 分钟"）；主持人数（"单口"/"对谈"）；音色（"女声"/"男声"/"温暖"）；调性（"轻松"/"严肃"/"科普"）；语言 | "做个 15 分钟的女声轻松播客" → query 写成"做个播客" | "做个 **15 分钟**的**女声轻松风格**播客" |
| **QUIZ** | 题量（"10 道"/"20 道"）；难度（"简单"/"中等"/"困难"）；语言 | "出 20 道难题考考我" → query 写成"出题" | "出 **20 道难题**考考我" |
| **GRAPH** | 风格（"极简"/"卡通"/"酷炫"）；尺寸（"方图"/"横版"/"竖版"） | "做张卡通风格的竖版信息图" → query 写成"做张信息图" | "做张**卡通风格**的**竖版**信息图" |
| **TRANSLATION** | 源语言 + 目标语言（"中译英"/"翻成日语"） | "把这个文件翻成日语" → query 写成"翻译" | "把这个文件**翻成日语**" |
| **PPT** | 除 preset 外的字数（"做 20 页"）、语言（"英文 PPT"） | "做个 20 页英文 PPT" → query 写成"做 PPT" | "做个 **20 页英文** PPT" |
| 其它 | 任何用户主动提到的风格 / 字数 / 语言 / 调性 / 偏好 | 不要因为"觉得不必要"而省略 | — |

> **核心原则**：除 `--output-type` 这类必须映射到 type 字符串的关键词外，**用户提到的所有其它修饰信息全部原样塞到 `--query` 里**。query 写得越完整，下游 LLM 推断越准。
>
> **HHVIDEO 例外**：HHVIDEO 有专属的 `--video-ratio`/`--video-resolution`/`--video-duration`/`--video-images`/`--video-image-type` 参数，这些维度走显式 videoConfig 子对象传递，**不需要写在 query 里**。其它类型的所有维度都靠 query。

## 推荐方式

**优先使用 Pipeline 脚本**，无需手动拼接 API：

```shell
# 对已有知识库直接生成
python3 scripts/pipeline_generate.py --kb "知识库名称" --output-type PDF --query "创作要求"

# 查看生成进度
python3 scripts/pipeline_check_status.py --kb "知识库名称"
```

> 以下 API 细节仅供 Pipeline 不可用时参考。

## 接口决策表

| 用户意图 | 调用接口 | 关键参数 |
|---------|---------|---------|
| 生成报告（PDF/DOCX/MARKDOWN） | `POST /api/v1/knowledge/creationTask` | `collectionId`, `type`, `query`, `files` |
| 生成 PPT（商务/卡通） | `POST /api/v1/knowledge/creationTask` | `collectionId`, `type=PPT`, `preset`, `query`, `files` |
| 生成播客/思维导图/视频 | `POST /api/v1/knowledge/creationTask` | `collectionId`, `type`, `query`, `files` |
| 查看创作列表和状态 | `GET /api/v1/knowledge/creationList` | `collectionId`, `pageNum`, `pageSize` |

## creationTask 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `collectionId` | string | 是 | 知识库 ID |
| `type` | string | 是 | 创作类型：`PDF`/`DOCX`/`MARKDOWN`/`PPT`/`XMIND`/`PODCAST`/`VIDEO`/`HHVIDEO`/`QUIZ`/`GRAPH`/`TRANSLATION`/`PPT_EDIT` |
| `query` | string | 否 | 用户对产出的自定义要求。不传则系统自动规划。**所有非显式参数维度（时长/音色/难度/风格/字数/语言等）都通过 query 文本透传给下游 LLM** |
| `files` | array | 否 | 参考文件列表。**不传则使用知识库全部文件** |
| `preset` | string | 否 | PPT 风格：`"商务"` / `"卡通"`。仅 `type=PPT` 时有效 |
| `videoConfig` | object | 否 | HHVIDEO 视频生成配置。仅 `type=HHVIDEO` 时有效，详见下表 |

`files` 数组中每个元素：

| 字段 | 类型 | 说明 |
|------|------|------|
| `contentId` | string | 文件的 contentId（来自 `upload` 返回的 `data.contentId`，或 `pageQueryContents` 返回的文件记录中的 `contentId` 字段） |

`videoConfig` 子字段（仅 `type=HHVIDEO` 使用）：

| 字段 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `images` | List\<String\> | `[]` | 参考图片 CDN URL 列表；空 = T2V 文生视频 |
| `ratio` | string | `"16:9"` | 视频宽高比：`16:9` / `9:16` / `1:1`，仅 T2V 生效 |
| `imageType` | string | `"reference"` | `reference`（百炼 I2V）/ `first_frame`（Seed） |
| `resolution` | string | `"720p"` | 分辨率：`720p` / `1080p`，Seed 模式忽略 |
| `duration` | int | `5` | 时长（秒）：`5` / `10` / `15`，Seed 模式忽略 |

## 内容生成工作流

### 1. 确定参数

```bash
# 如果用户没指定文件，默认使用知识库全部文件（不传 files）
# 如果用户想选文件，先查询文件列表（参数通过 URL query string 传递）：
iflow_api POST "/api/v1/knowledge/pageQueryContents?collectionId=${COLLECTION_ID}&pageNum=1&pageSize=50"
```

用户没指定文件时，**不需要询问**，直接使用全部文件。仅当用户说"用那几篇论文"这类限定时才需要定位具体文件。

**定向选择文件**：Agent 需要：
1. 获取文件列表（含 `fileName` 和 `summary` 字段）
2. 根据文件名和摘要匹配用户需求
3. 将匹配的文件 `contentId` 传给创作任务

### 2. 提交生成任务

```bash
# 生成 PDF 报告（使用全部文件）
iflow_api POST "/api/v1/knowledge/creationTask" "{
  \"collectionId\": \"${COLLECTION_ID}\",
  \"type\": \"PDF\",
  \"query\": \"${USER_PROMPT}\"
}"

# 生成 PDF 报告（指定文件）
iflow_api POST "/api/v1/knowledge/creationTask" "{
  \"collectionId\": \"${COLLECTION_ID}\",
  \"type\": \"PDF\",
  \"query\": \"重点分析架构差异\",
  \"files\": [
    {\"contentId\": \"${CONTENT_ID1}\"},
    {\"contentId\": \"${CONTENT_ID2}\"}
  ]
}"
# 返回: {"success": true, "code": "200", "data": "creation_id"}

# 生成 PPT（卡通风格）
iflow_api POST "/api/v1/knowledge/creationTask" "{
  \"collectionId\": \"${COLLECTION_ID}\",
  \"type\": \"PPT\",
  \"preset\": \"卡通\",
  \"query\": \"生成演示文稿\"
}"

# 生成播客
iflow_api POST "/api/v1/knowledge/creationTask" "{
  \"collectionId\": \"${COLLECTION_ID}\",
  \"type\": \"PODCAST\",
  \"query\": \"请创建一份播客脚本\"
}"

# 生成思维导图
iflow_api POST "/api/v1/knowledge/creationTask" "{
  \"collectionId\": \"${COLLECTION_ID}\",
  \"type\": \"XMIND\"
}"

# 生成视频
iflow_api POST "/api/v1/knowledge/creationTask" "{
  \"collectionId\": \"${COLLECTION_ID}\",
  \"type\": \"VIDEO\"
}"
```

### 3. 等待策略

> **⚠️ `submitted` ≠ 已完成**：提交成功（`creationStatus: "submitted"`）仅表示任务进入队列，生成尚未开始或正在进行。Agent **绝不能**在此时告诉用户"已生成完成"。只有 `status=success` 才代表真正完成。

**所有创作任务耗时较长（10-30分钟），提交后不要阻塞等待**，立即告知用户预估时间：

```
生成任务已提交
预计需要 10-20 分钟（报告/播客）/ 15-30 分钟（PPT/思维导图/视频）

你可以：
1. 继续做其他事情，稍后问我"做好了吗"
2. 我在后台帮你盯着
```

**用户稍后询问进度或选择后台监控时**，轮询检查状态：

```bash
CREATION_ID="..."  # creationTask 返回的 data
for i in $(seq 1 60); do
  RESULT=$(iflow_api GET "/api/v1/knowledge/creationList?collectionId=${COLLECTION_ID}&pageSize=10")
  STATUS=$(echo "$RESULT" | jq -r --arg cid "$CREATION_ID" '.data[] | select(.contentId == $cid) | .extra.status')

  case "$STATUS" in
    "success")
      echo "生成完成"
      break
      ;;
    "failed")
      echo "生成失败"
      break
      ;;
    "pending")
      echo "已提交，正在排队等待处理…"
      sleep 30
      ;;
    *)
      # processing
      sleep 30
      ;;
  esac
done
```

### 4. 多产出并行生成

用户说"同时生成报告和PPT"时，并行提交多个任务：

```bash
OUT1=$(iflow_api POST "/api/v1/knowledge/creationTask" '{"collectionId":"...","type":"PDF","query":"撰写综合报告"}')
OUT2=$(iflow_api POST "/api/v1/knowledge/creationTask" '{"collectionId":"...","type":"PPT","preset":"商务"}')
# 分别轮询，汇总展示
```

展示：
```
PDF 报告 — 生成中
演示文稿 — 生成中

PDF 报告 — 已完成
演示文稿 — 已完成
```

### 5. 查看创作结果

```bash
iflow_api GET "/api/v1/knowledge/creationList?collectionId=${COLLECTION_ID}"
```

返回结构：
```json
{
  "success": true,
  "code": "200",
  "data": [
    {
      "contentType": "CREATION",
      "contentId": "XLNO20260328...",
      "status": "processing",
      "extra": {
        "fileType": "PODCAST",
        "status": "processing",
        "query": "请创建一份播客脚本",
        "files": [{"contentId": "xxx", "url": "...", "fileId": "xxx"}],
        "permitId": "...",
        "startCreationTimestamp": "..."
      }
    }
  ]
}
```

创作状态：`pending`（排队中） → `processing`（生成中） → `success`（完成） | `failed`（失败）

> 如果状态为 `pending`，说明任务已提交成功、正在排队等待处理，这是正常流程。应告知用户："生成任务已提交，正在排队等待处理。"

> **⚠️ 如何匹配具体的创作任务**：`creationList` 返回的是该知识库下所有创作记录。需要用 `contentId` 字段匹配 `creationTask` 返回的 `data`（创作任务 ID）来找到对应的任务。不要直接取第一条记录。

## 状态查询

用户说"视频做好了吗""报告进度怎样""查看进度"时，**优先使用 Pipeline 脚本**：

```shell
python3 scripts/pipeline_check_status.py --kb "知识库名称"
# 或指定特定任务：--creation-id "xxx"
```

> 直接调 API（仅在 Pipeline 不可用时）：`iflow_api GET "/api/v1/knowledge/creationList?collectionId=${COLLECTION_ID}"`

**排队中（pending）：**
```
任务: 请创建一份播客脚本 (播客)
状态: 已提交，正在排队等待处理
```

**处理中（processing）：**
```
任务: 请创建一份播客脚本 (播客)
状态: 生成中
```

**已完成：**
```
任务: 请创建一份播客脚本 (播客)
状态: 已完成
```

**失败：**
```
任务: 请创建一份播客脚本 (播客)
状态: 生成失败
可能原因: 源文件内容不足或格式异常
建议: 检查源文件是否已解析成功，或更换文件后重试
```

> Agent 应主动从 `creationList` 响应的 `extra` 字段提取失败详情（`fileType`、`query`），展示给用户。不要只说"失败"而不给出原因。

## query 参数用法

`query` 让用户自定义产出内容和风格。所有产出类型均支持。

| 用户说的 | query 值 |
|---------|---------|
| "重点分析架构差异" | `重点分析架构差异` |
| "生成一份面向非技术人员的报告" | `面向非技术人员，使用通俗语言` |
| "做个讲解 Transformer 的播客" | `围绕 Transformer 架构进行讲解` |
| "画个关于模型对比的思维导图" | `对比不同模型的架构和性能` |
| "写篇博客" | `以博客形式撰写，语言生动活泼` |
| （不说具体要求） | 不传，系统自动规划 |

## 错误处理

常见错误：`40004`（文件解析中）→ 等解析完成再重试。完整错误码列表见 `references/api.md` 错误码章节。

## 注意事项

- 提交生成任务前，必须确认相关文件解析完成（`parseStatusThenCallBack` 或 `pageQueryContents` 中 `status=success`）
- 所有产出类型均通过 `creationTask` 和 `creationList` 接口实现
- 不支持 Webhook/回调通知，需要轮询检查状态
- **接口限流**：搜索和创作接口共享限流，合计 20 次/分钟，超限返回 `500`。Pipeline 脚本内部已自动重试
