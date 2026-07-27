# zodiacxMBTI

星盘 × MBTI 性格解读 — 可逆实验（spike），不是产品立项。

给朋友圈约 10 人用的中文手机链接：填出生信息 + MBTI → 一次出报告。免费、不推广、不收费、不留账号。

**在线试用：** [https://zodiacxmbti-ydpwplvynjy5tvxexxyjws.streamlit.app](https://zodiacxmbti-ydpwplvynjy5tvxexxyjws.streamlit.app)

## 这是什么

一条直线链路：

1. Streamlit 表单收集出生日期 / 时间 / 地点 / MBTI /（选填）最近在纠结的事
2. [kerykeion](https://github.com/g-battaglia/kerykeion)（Swiss Ephemeris）算行星落座、宫位、上升，并出暗色轮盘 SVG
3. 按太阳座 × MBTI 查出「隐藏人格」人设卡（192 选 1 + 星座母图）
4. LLM API（OpenAI 兼容，可用 DeepSeek）流式生成中文分节解读（含金钱事业；有问题时加「纠结」专节；末尾「延伸探索」三条短解析）
5. （可选）报告页「再抽三张牌」——3D 翻牌演出 + 结合星盘/MBTI 的补充解读
6. 可下载**完整页面 HTML**（含图）或**文字版 PDF**

详细边界见 [architecture.md](architecture.md) 与 [history.md](history.md)；发群清单见 [SHIP.md](SHIP.md)；纸面方案原文见 [`星盘MBTI解读spike需求与实施方案.md`](星盘MBTI解读spike需求与实施方案.md)（v1.4 封版）。协作约定见 [agent.md](agent.md)。文档索引见 [DOCS.md](DOCS.md)。

## 状态

- **阶段**：Cloud 已上线（含人设卡、§6 折叠延伸、共享设计系统、导出）；发群观察见 [SHIP.md](SHIP.md)
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
```

- `GEONAMES_USERNAME` — [GeoNames](https://www.geonames.org/login) 注册后，在 manageaccount **启用免费 Web Services**
- API 账户设 **硬性消费上限**（建议 $10）

```bash
# Windows（推荐用 venv 里的可执行文件）
.\.venv\Scripts\streamlit.exe run app.py
# macOS / Linux
streamlit run app.py
```

部署：推送到 GitHub 后，在 [Streamlit Community Cloud](https://streamlit.io/cloud) 绑定本仓库，入口填 `app.py`，Secrets 粘贴与本地相同的键。

## 工程结构

```
app.py                 # Streamlit UI、主题 CSS、session_state、导出按钮
design_system.py       # 共享色板 / 字体栈 / CSS 变量（app + 导出 + 塔罗）
chart.py               # 排盘 / 生时降级 / 月亮换座 / 暗色轮盘 SVG
interpret.py           # MAIN / TAROT / §4 repair + 流式 LLM
persona_cards.py       # 192 卡查表 + 星座母图 HTML
tarot.py               # 78 张牌 + 三牌阵（纯 random）
tarot_ui.py            # 翻牌 HTML + 牌面映射（展示层）
report_export.py       # 完整页 HTML + 文字 PDF；§6 折叠解析
tests/                 # design_system / question_flow / persona_cards
persona_cards/         # persona_cards.json（192 真相源）
personapicture/zodiac_tarot_masters/v1/  # 12 张人设母图（运行时）
assets/tarot/          # LuciellaES CC0 韦特牌面
assets/fonts/          # Noto Sans SC（PDF 中文）
requirements.txt
.streamlit/config.toml           # dark theme（对齐 design_system）
.streamlit/secrets.toml.example
```

`st.session_state` 缓存星盘、SVG、主报告与塔罗结果；点塔罗只追加一次 LLM，不重跑主报告。

## 产品要点（已实现）

| 能力 | 说明 |
|---|---|
| 生时未知 | 正午行星；无上升/宫位；月亮换座则双可能 |
| 出生国家 | 下拉（中国默认），「其他」才填两位码 |
| 想问的事 | 选填；有则报告第 4 节针对性展开（缺节会补全）；并预填塔罗问题框 |
| 人设卡 | 太阳座 × MBTI → 192 中唯一一张；怪名/矛盾/出口 + 星座母图；MBTI「不确定」不出卡 |
| 流式解读 | `st.write_stream`；结束后写入 session 缓存 |
| 报告结构 | ①画像 ②金钱与事业 ③关系 ④纠结（可选）⑤一句话建议 ⑥延伸探索（3 条标题+短解析，UI/HTML 默认折叠） |
| 篇幅 | 第 1–5 节约 1000–1300 字；§6 每条正文 80–120 字；塔罗约 500–650 字 |
| 钩子 | 节首揭示性格矛盾（即本节结论）；禁止「想知道吗」伪 CTA |
| 塔罗 | 过去 / 现在 / 未来 / 三张牌共同指向；结尾落锤收束 |
| 摘要卡 | 太阳/月亮/上升 × MBTI + 第 5 节一句话 |
| 星盘 | 结果页直接展示暗色轮盘（CN 标签 + Noto；SVG→base64 `<img>`，避开 DOMPurify 剥 SVG / iframe 测高） |
| 塔罗 UI | CSS 3D 翻牌；牌面 base64；inline fragment + reduced-motion |
| 导出 | 完整 HTML（含图，可浏览器打印成 PDF）+ 文字 PDF；共享设计 token |
| UI | 夜空蓝坐标感主题；Hero + 输入坐标条；本地字体栈（无 Google Fonts） |

## 隐私

出生信息仅用于当次计算，不存储、不写日志、无数据库。报告底部固定免责声明。

## 许可

应用代码 MIT。排盘依赖 [kerykeion](https://github.com/g-battaglia/kerykeion) 为 AGPL-3.0：本仓库保持公开；若将来闭源商业化，需切到其官方 Astrologer API 或自研排盘，不再嵌入该库。
