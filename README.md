# zodiacxMBTI

星盘 × MBTI 性格解读 — 可逆实验（spike），不是产品立项。

给朋友圈约 10 人用的中文手机链接：填出生信息 + MBTI → 一次出报告。免费、不推广、不收费、不留账号。

**在线试用：** [https://zodiacxmbti-ydpwplvynjy5tvxexxyjws.streamlit.app](https://zodiacxmbti-ydpwplvynjy5tvxexxyjws.streamlit.app)

## 这是什么

一条直线链路：

1. Streamlit 表单收集出生日期 / 时间 / 地点 / MBTI /（选填）最近在纠结的事
2. [kerykeion](https://github.com/g-battaglia/kerykeion)（Swiss Ephemeris）算行星落座、宫位、上升，并出暗色轮盘 SVG
3. 按太阳座 × MBTI 查出「隐藏人格」人设卡（192 选 1；**白羊、金牛各有 16 张 MBTI 专属图**，其余星座用 12 张星座母图）
4. LLM API（OpenAI 兼容，可用 DeepSeek）流式生成中文分节解读（含金钱事业；有问题时加「纠结」专节；末尾「延伸探索」三条短解析）
5. （可选）报告页「再抽三张牌」——3D 翻牌演出 + 结合星盘/MBTI 的补充解读
6. 可下载**完整页面 HTML**（含图）或**文字版 PDF**

详细边界见 [architecture.md](architecture.md) 与 [history.md](history.md)；发群与观察期统计见 [SHIP.md](SHIP.md)；导师批次见 [log20260727_mentor.md](log20260727_mentor.md)；纸面方案原文见 [`星盘MBTI解读spike需求与实施方案.md`](星盘MBTI解读spike需求与实施方案.md)（v1.4 封版）。协作约定见 [agent.md](agent.md)。文档索引见 [DOCS.md](DOCS.md)。

## 状态

- **阶段**：Cloud 已上线；发群观察中（匿名统计 + 节末反馈已接，见 [SHIP.md](SHIP.md)）
- **在线**：https://zodiacxmbti-ydpwplvynjy5tvxexxyjws.streamlit.app
- **时间盒**：两个周末，硬上限
- **验收**：两周后看 LLM 调用是否有自发增量；定性问朋友是否回访/转发。商业化只认强信号

## 本地运行

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

配置密钥（**切勿提交**）：

```bash
# Windows
copy .streamlit\secrets.toml.example .streamlit\secrets.toml
# macOS / Linux
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

编辑 `.streamlit/secrets.toml`（OpenAI 或 DeepSeek 二选一）：

```toml
# DeepSeek 示例（便宜，适合 spike 试跑）
OPENAI_API_KEY = "sk-..."
OPENAI_MODEL = "deepseek-chat"
OPENAI_BASE_URL = "https://api.deepseek.com"

GEONAMES_USERNAME = "your_geonames_username"

# 可选：页脚「运营统计」密码（Cloud 上查看生成次数与各节准/不像我；不设则不显示入口）
# STATS_PASSWORD = "choose-a-long-secret"
# 可选：容器重建后手动累加历史基数
# GENERATION_COUNT_BASE = "0"
# QUESTION_COUNT_BASE = "0"
```

- `GEONAMES_USERNAME` — [GeoNames](https://www.geonames.org/login) 注册后，在 manageaccount **启用免费 Web Services**
- API 账户设 **硬性消费上限**（建议 $10）

```bash
# Windows（推荐用 venv 里的可执行文件）
.\.venv\Scripts\streamlit.exe run app.py
# macOS / Linux
streamlit run app.py
```

部署：推送到 GitHub 后，在 [Streamlit Community Cloud](https://streamlit.io/cloud) 绑定本仓库，入口填 `app.py`，Secrets 粘贴与本地相同的键（含可选 `STATS_PASSWORD`）。

## 工程结构

```
app.py                 # Streamlit UI、主题 CSS、session_state、导出、节末反馈、运营统计
design_system.py       # 共享色板 / 字体栈 / CSS 变量（app + 导出 + 塔罗）
chart.py               # 排盘 / 生时降级 / 月亮换座 / 暗色轮盘 SVG；CN 城市映射
china_cities.py        # 中文市名 → GeoNames 英文（精确匹配）
sun_preview.py         # 表单用大致太阳座（非 kerykeion）
usage_stats.py         # 匿名计数 SQLite（无 PII）
interpret.py           # MAIN / TAROT / §4 repair + 流式 LLM
persona_cards.py       # 192 卡查表 + 专属/母图 + HTML / 分享 PNG
tarot.py               # 78 张牌 + 三牌阵（纯 random）
tarot_ui.py            # 翻牌 HTML + 牌面映射（展示层）
report_export.py       # 完整页 HTML + 文字 PDF；§6 折叠解析
data/china_cities.json # 中文城市映射表
cache/usage.sqlite     # 本地/Cloud 匿名计数（gitignore）
tests/                 # design_system / question_flow / persona_cards / usage_stats / mentor_batch / …
persona_cards/         # persona_cards.json（192 真相源）
personapicture/zodiac_tarot_masters/v1/     # 12 张星座母图（回落）
personapicture/mbti_tarot_cards/aries/v1/   # 白羊 × 16（已接线）
personapicture/mbti_tarot_cards/taurus/v1/  # 金牛 × 16（已接线）
assets/tarot/          # LuciellaES CC0 韦特牌面
assets/fonts/          # Noto Sans SC（PDF 中文）
requirements.txt       # + pillow（人设 PNG）
.streamlit/config.toml
.streamlit/secrets.toml.example
```

`st.session_state` 缓存星盘、SVG、主报告与塔罗结果；点塔罗只追加一次 LLM，不重跑主报告。

## 产品要点（已实现）

| 能力 | 说明 |
|---|---|
| 表单默认 | 日期空；生时默认「不知道」；MBTI 须选类型或「不确定」 |
| 生时未知 | 正午行星；无上升/宫位；月亮换座则双可能 |
| 出生国家 | 下拉（中国默认），「其他」才填两位码 |
| 中文城市 | 常见市名可直接中文；`data/china_cities.json` 精确映射，失败仍走 GeoNames |
| 想问的事 | 选填 `text_area`（在 MBTI 上方）；有则 §4 展开（缺节会补全）；预填塔罗 |
| 人设卡 | 太阳×MBTI → 192 文案；**白羊/金牛各 16 张专属图**（`st.image`），其它星座用母图 |
| 流式解读 | `st.write_stream`；结束后写入 session 缓存 |
| 报告结构 | ①画像 ②金钱 ③关系 ④纠结（可选）⑤建议 ⑥延伸探索（3 条折叠） |
| 节末反馈 | §§1–5「这段准 / 不像我」→ 匿名计数（验收用，非个性化学习） |
| 生成统计 | 按钮下显示总次数与「写了问题」次数；运营可看密码门统计 + JSON 导出 |
| 主按钮 | `解读我的{预览太阳}×{MBTI}` 或「生成解读」；隐私在提交旁 |
| 篇幅 / 钩子 / 塔罗 / 摘要 / 星盘 / UI | 同前（见 architecture.md） |
| 导出 | 完整 HTML + 文字 PDF；人设卡可下 PNG |

## 隐私

出生信息仅用于当次计算，**不存储出生数据、不写日志、不存问题原文**。  
仅累计匿名计数（总生成次数、是否写过问题、各节准/不像我票数）于 `cache/usage.sqlite`；Cloud 上可能随容器重建丢失，运营可用页脚密码统计导出 JSON。报告底部固定免责声明。

## 许可

应用代码 MIT。排盘依赖 [kerykeion](https://github.com/g-battaglia/kerykeion) 为 AGPL-3.0：本仓库保持公开；若将来闭源商业化，需切到其官方 Astrologer API 或自研排盘，不再嵌入该库。
