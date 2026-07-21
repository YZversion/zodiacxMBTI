# zodiacxMBTI

星盘 × MBTI 性格解读 — 可逆实验（spike），不是产品立项。

给朋友圈约 10 人用的中文手机链接：填出生信息 + MBTI → 一次出报告。免费、不推广、不收费、不留账号。

## 这是什么

一条直线链路：

1. Streamlit 表单收集出生日期 / 时间 / 地点与 MBTI
2. [kerykeion](https://github.com/g-battaglia/kerykeion)（Swiss Ephemeris）算行星落座、宫位、上升，并出 SVG 星盘图
3. LLM API 基于结构化星盘上下文 + MBTI 生成中文分节解读
4. （可选）报告页底部「再抽三张牌」——韦特牌阵 + 结合星盘/MBTI 的补充解读

详细边界、删除清单与验收标准见 [architecture.md](architecture.md) 与 [history.md](history.md)；纸面方案原文见 [`星盘MBTI解读spike需求与实施方案.md`](星盘MBTI解读spike需求与实施方案.md)（v1.4 封版）。

## 状态

- **阶段**：周末一前置 — 仓库与文档就绪，尚未写应用代码
- **时间盒**：两个周末，硬上限
- **验收**：两周后看 LLM 调用是否有自发增量；定性问十位朋友是否回访/转发。商业化只认强信号（转发到作者不认识的人且对方使用）

## 本地运行（待实现后）

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install streamlit kerykeion openai
# 或 anthropic，按所选 LLM 提供商

# 配置密钥（切勿提交）
# .streamlit/secrets.toml
# GEONAMES_USERNAME = "..."
# OPENAI_API_KEY = "..."   # 或 ANTHROPIC_API_KEY

streamlit run app.py
```

部署目标：Streamlit Community Cloud。API 账户设硬性消费上限（建议 $10）。

## 隐私

出生信息仅用于当次计算，不存储、不写日志、无数据库。报告底部固定免责：内容由 AI 生成，仅供娱乐与自我探索，不构成心理、医疗或重大决策建议。

## 许可

本仓库源码以 [MIT](LICENSE) 发布。运行时依赖 **kerykeion（AGPL-3.0）**；若将来商业化闭源，计划切换到 [Astrologer API](https://github.com/g-battaglia/Astrologer-API) 以避开 copyleft。公开开源阶段请同时遵守依赖方协议要求。

## 给 Agent

协作约定见 [agent.md](agent.md)。
