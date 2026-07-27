# log20260727 — 导师建议批次 + Cloud 验收统计

> 状态：**已实现**（2026-07-27，commits `e09567f` → `fcfbac4`）。  
> 来源：导师 triage 计划（默认值 / 节末反馈 / 中文城市 / 白羊 16 卡 / 运营统计）。  
> 关联：`app.py` / `usage_stats.py` / `china_cities.py` / `sun_preview.py` / `persona_cards.py` / `tests/test_*`

## 批次 A — 表单与提交

- 出生日期默认空；「不知道出生时间」默认勾选
- MBTI 哨兵「请选择类型」；「不确定」置底；哨兵提交报错（不当成不确定）
- 动态主按钮 `key="generate_report"`，文案 `解读我的{太阳}×{MBTI}` 或「生成解读」
- 隐私说明挪到提交旁；日期下大致太阳座（标明以排盘为准）
- 「纠结」改为 `text_area`，放在 MBTI 上方

## 批次 B — 匿名统计

- `cache/usage.sqlite`：`main_report` / `with_question` / `without_question` / `s1_hit` … `s5_miss`
- 公开展示：`已生成 N 次 · 其中 M 次写下了想问的事`（按钮下 + 结果页顶）
- 报告 §§1–5 末「这段准 / 这段不像我」；session 锁防连点；仅成功生成 +1 一次

## 批次 C — 城市与分享

- `data/china_cities.json` 精确中文市名 → GeoNames 英文（仅剥「市」后缀，不剥区/县）
- 人设卡 PNG 下载（`build_persona_share_png` + session 缓存）

## 白羊 / 金牛专属卡图

- 资产：`personapicture/mbti_tarot_cards/aries/v1/`、`…/taurus/v1/`（各 16 张 `NN_{MBTI}_{Sign}_*.png`）
- 运行时：`persona_art_path` 优先专属图；结果页用 `st.image` 展示（避免 3MB+ base64 在 `st.html` 里静默失败）
- 其它星座仍回落 `zodiac_tarot_masters/v1/` 12 张母图

## Cloud 运营查看统计

- Secrets：`STATS_PASSWORD`（不设则页脚不出现统计入口）
- 页脚折叠「运营统计（需密码）」：总次数、各节准/不像我、下载 JSON 备份
- 可选：`GENERATION_COUNT_BASE` / `QUESTION_COUNT_BASE` / `USAGE_DB_PATH`
- **局限**：Streamlit Cloud 容器重建后 SQLite 可能清零 → 定期下载 JSON

## 测试

```bash
python -m unittest discover -s tests
```
