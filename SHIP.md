# SHIP — 发群前清单

Spike 开发冻结后用。做完勾掉；不要再开新功能，除非验收证明有强信号。

**在线：** [https://zodiacxmbti-ydpwplvynjy5tvxexxyjws.streamlit.app](https://zodiacxmbti-ydpwplvynjy5tvxexxyjws.streamlit.app)

## 技术

- [x] `.streamlit/secrets.toml` 已填：`OPENAI_*`（或 DeepSeek）+ `GEONAMES_USERNAME`（Web Services 已启用）
- [x] API 账户消费上限已设（建议 ≤ $10）
- [x] `secrets.toml` **未**进 git（`git status` 确认）
- [x] 本地自测路径：
  - [x] 知道生时 + 有「想问的事」→ §§1–5，第 4 节最长；§6 三条可折叠且每条有解析
  - [x] 不填「想问的事」→ 无第 4 节，仍有第 5、6 节
- [x] **手机 + 桌面**打开一轮（Hero / 坐标条 / 摘要卡 / **星盘可见（base64 图）** / 人设卡 / §6 折叠 / 翻牌 / 下载折叠）
- [x] `python -m unittest discover -s tests` 通过（推荐）
- [x] 推送到公开 GitHub → Streamlit Cloud 绑定 `app.py` → Secrets 同步
- [x] 用手机打开 Cloud 链接冷启动一次（提醒朋友「第一次可能要等半分钟」）



## 发放与观察

- [x] 发群文案附：首次打开可能慢；出生地用拼音/英文城市名；链接用 Cloud URL
- [x] 发放当天记下 LLM 调用基线（主报告 vs 塔罗分开看）
- [x] **之后不再主动催**；两周后问约 10 人是否回访/转发
- [x] 强信号 = 转发到你不认识的人且对方使用；仅朋友本人客气回访 = 弱信号

## 观察期 — 匿名统计（2026-07-27 起）

Cloud 测试用户的数据写在容器内 `cache/usage.sqlite`，**不会同步到你本机**。查看方式：

1. Streamlit Cloud → App → **Secrets** 增加 `STATS_PASSWORD`（长密码，勿发给测试用户）
2. 打开同一 Cloud 链接 → 滚到页脚 → **运营统计（需密码）** → 输入密码
3. 查看：总生成次数、写问题次数、§1–§5「准 / 不像我」与命中率
4. 定期点 **下载统计 JSON** 备份（redeploy / 休眠后计数可能归零）
5. 可选 Secrets：`GENERATION_COUNT_BASE` / `QUESTION_COUNT_BASE`（手动补历史基数）

公开展示（无需密码）：主按钮下方的「已生成 N 次 · 其中 M 次写下了想问的事」。

人设卡：**十二星座 × 16 MBTI** 专属成品图已全部接入（共 192 张）。详见 [log20260727_mentor.md](log20260727_mentor.md)。

### 快照基线（2026-07-30 UTC 导出）

| 指标 | 值 |
|------|-----|
| 主报告生成 `total` | 19 |
| 写了问题 | 7（37%） |
| 未写问题 | 12 |
| §1 准 / 不像 | 8 / 0 |
| §2 | 5 / 0 |
| §3 | 5 / 1 |
| §4 | 3 / 0 |
| §5 | 5 / 1 |

**怎么读：** n=19、各节投票仅 3–8，**不能**据此改 `MAIN_SYSTEM` 或开大功能。价值是「无明显翻车」+ 对比基线。强信号仍是陌生人转发使用（见上）。

**决策门槛（写死）：**

- 累计生成 **< 50**，或单节 miss **< 5** → 只观察 / 定性问朋友，**不**因个别 miss 重写提示词。
- 投票远少于生成时，优先考虑半句反馈引导文案，而不是改解读内容。
- 本地摘要：`python tools/summarize_usage_snapshot.py path/to/usage_stats_snapshot.json`
- 原始 JSON **不进 git**；本机建议固定目录：`Documents\zodiacxMBTI-stats\usage_YYYY-MM-DD.json`（首份已存为 `usage_2026-07-30.json`）。Cloud SQLite 会丢，以你下载备份为准。

下次导出后，用同一表对比 `total` / `with_question` / 各节 hit+miss。

### LLM 费用与质量红线

- 费用主要来自：主报告 +（偶发）§4 补全 +（可选）塔罗，各自附带完整 `context_xml`。
- **质量优先：** 不为省 token 压缩 `MAIN_SYSTEM` / 瘦 XML / 给 completion 加可能截断的 `max_tokens`。
- 允许的省钱：会话缓存避免重复主报告；§4 标题变体识别正确以免**误触发**第二次补全。
- 只读量体积：`python tools/measure_llm_payload.py --live-chart`