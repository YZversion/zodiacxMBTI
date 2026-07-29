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

人设卡：**白羊→天蝎共 8 星座 × 16 MBTI** 已用专属图（共 128 张）；其它星座暂不展示人格成品图。详见 [log20260727_mentor.md](log20260727_mentor.md)。