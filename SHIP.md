# SHIP — 发群前清单

Spike 开发冻结后用。做完勾掉；不要再开新功能，除非验收证明有强信号。

**在线：** https://zodiacxmbti-ydpwplvynjy5tvxexxyjws.streamlit.app

## 技术

- [ ] `.streamlit/secrets.toml` 已填：`OPENAI_*`（或 DeepSeek）+ `GEONAMES_USERNAME`（Web Services 已启用）
- [ ] API 账户消费上限已设（建议 ≤ $10）
- [ ] `secrets.toml` **未**进 git（`git status` 确认）
- [ ] 本地自测路径：
  - [ ] 知道生时 + 有「想问的事」→ §§1–5，第 4 节最长；§6 三条可折叠且每条有解析
  - [ ] 不填「想问的事」→ 无第 4 节，仍有第 5、6 节
  - [ ]「不知道出生时间」→ 金钱节无宫位 + 依据较少说明
  - [ ] 日期控件可见「公历」说明；城市 caption 含陕西 Shaanxi / 山西 Shanxi
  - [ ] 已选 MBTI → 摘要下出现「你的隐藏人格」人设卡（怪名 + 母图）
  - [ ] MBTI「不确定」→ 人设卡位置为提示，不编怪名
  - [ ] 塔罗抽牌不重跑主报告；预填问题可改；结尾为「三张牌共同指向」
  - [ ] 下载在折叠「下载报告（可选）」内，默认收起
- [ ] **手机 + 桌面**打开一轮（Hero / 坐标条 / 摘要卡 / **星盘可见（base64 图）** / 人设卡 / §6 折叠 / 翻牌 / 下载折叠）
- [ ] `python -m unittest discover -s tests` 通过（推荐）
- [ ] 推送到公开 GitHub → Streamlit Cloud 绑定 `app.py` → Secrets 同步
- [ ] 用手机打开 Cloud 链接冷启动一次（提醒朋友「第一次可能要等半分钟」）

## 发放与观察

- [ ] 发群文案附：首次打开可能慢；出生地用拼音/英文城市名；链接用 Cloud URL
- [ ] 发放当天记下 LLM 调用基线（主报告 vs 塔罗分开看）
- [ ] **之后不再主动催**；两周后问约 10 人是否回访/转发
- [ ] 强信号 = 转发到你不认识的人且对方使用；仅朋友本人客气回访 = 弱信号

## 不做

- 不再打磨 prompt / UI / 新功能（除非强信号触发商业化审查）
- 不建账号、不存用户数据、不加监控栈
- 不另建 `memory.md`；跨会话要记住的事写进 `history.md` / `agent.md`（见 [DOCS.md](DOCS.md)）
