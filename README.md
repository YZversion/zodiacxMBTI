# zodiacxMBTI

星盘 × MBTI 性格解读 — 可逆实验（spike），不是产品立项。

给朋友圈约 10 人用的中文手机链接：填出生信息 + MBTI → 一次出报告。免费、不推广、不收费、不留账号。

## 这是什么

一条直线链路：

1. Streamlit 表单收集出生日期 / 时间 / 地点与 MBTI
2. [kerykeion](https://github.com/g-battaglia/kerykeion)（Swiss Ephemeris）算行星落座、宫位、上升，并出 SVG 星盘图
3. LLM API 基于 `to_context` XML + MBTI 生成中文分节解读
4. （可选）报告页「再抽三张牌」——韦特牌阵 + 结合星盘/MBTI 的补充解读

详细边界见 [architecture.md](architecture.md) 与 [history.md](history.md)；纸面方案原文见 [`星盘MBTI解读spike需求与实施方案.md`](星盘MBTI解读spike需求与实施方案.md)（v1.4 封版）。协作约定见 [agent.md](agent.md)。

## 状态

- **阶段**：全链路代码已就绪（表单 → 排盘 → 报告 → 可选塔罗）
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

编辑 `.streamlit/secrets.toml`：

- `OPENAI_API_KEY` — 必填
- `OPENAI_MODEL` — 默认 `gpt-4o-mini`
- `GEONAMES_USERNAME` — [GeoNames](https://www.geonames.org/login) 免费注册后填入（强烈建议；否则会落到库默认账号，易被限流）
- `OPENAI_BASE_URL` — 可选，兼容网关

在 OpenAI（或所用提供商）账户设置 **硬性消费上限**（建议 $10）。

```bash
streamlit run app.py
```

部署：推送到 GitHub 后，在 [Streamlit Community Cloud](https://streamlit.io/cloud) 绑定本仓库，入口填 `app.py`，并在应用 Secrets 中粘贴与本地相同的键。

## 工程结构

```
app.py                 # Streamlit UI + session_state 缓存
chart.py               # kerykeion 排盘 / 生时降级 / 月亮换座 / SVG
interpret.py           # 主报告与塔罗 LLM prompt
tarot.py               # 78 张牌 + 三牌阵
requirements.txt
.streamlit/config.toml
.streamlit/secrets.toml.example
```

`st.session_state` 会缓存星盘上下文、SVG 与主报告；点塔罗只追加一次 LLM 调用，不会重跑整份报告。

## 隐私

出生信息仅用于当次计算，不存储、不写日志、无数据库。报告底部固定免责声明。

## 许可

本仓库应用代码以 [MIT](LICENSE) 发布。运行时依赖 **kerykeion（AGPL-3.0）**；若将来商业化闭源，计划切换到 [Astrologer API](https://github.com/g-battaglia/Astrologer-API)。
