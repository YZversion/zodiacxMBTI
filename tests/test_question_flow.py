from __future__ import annotations

import unittest
from types import SimpleNamespace

from interpret import build_question_section_prompt
from report_export import (
    QUESTION_SECTION_HEADING,
    has_complete_question_section,
    upsert_question_section,
)


class QuestionFlowTests(unittest.TestCase):
    def test_repair_prompt_keeps_the_users_exact_question(self) -> None:
        chart = SimpleNamespace(
            preface_notes=["出生时间未知，不使用宫位。"],
            mbti="INFP",
            resolved_city="Shanghai",
            city="Shanghai",
            nation="CN",
            resolved_tz="Asia/Shanghai",
            context_xml="<chart><sun sign='Ari'/></chart>",
        )
        question = "要不要生孩子哈哈哈"

        prompt = build_question_section_prompt(chart, user_question=question)

        self.assertIn(question, prompt)
        self.assertIn("INFP", prompt)
        self.assertIn(chart.context_xml, prompt)

    def test_question_section_is_inserted_before_advice(self) -> None:
        report = "## 3. 关系与沟通风格\n正文\n\n## 5. 当前阶段的一句话建议\n建议"
        body = "这是针对问题的具体分析。" * 12

        repaired = upsert_question_section(report, body)

        self.assertLess(repaired.index(QUESTION_SECTION_HEADING), repaired.index("## 5."))
        self.assertTrue(has_complete_question_section(repaired))

    def test_short_existing_section_is_replaced_without_duplication(self) -> None:
        report = (
            "## 3. 关系与沟通风格\n正文\n\n"
            f"{QUESTION_SECTION_HEADING}\n太短\n\n"
            "## 5. 当前阶段的一句话建议\n建议"
        )
        complete = f"{QUESTION_SECTION_HEADING}\n" + "具体且可操作的分析。" * 15

        repaired = upsert_question_section(report, complete)

        self.assertEqual(repaired.count(QUESTION_SECTION_HEADING), 1)
        self.assertNotIn("太短", repaired)
        self.assertTrue(has_complete_question_section(repaired))

    def test_title_only_heading_counts_as_complete_without_repair(self) -> None:
        """Model sometimes omits '4.'; must not trigger a second LLM call."""
        body = "针对原话给出的决策模式与自我欺骗方式，以及可执行判断框架。" * 3
        report = (
            "## 3. 关系与沟通风格\n正文\n\n"
            f"## 关于你正在纠结的事\n{body}\n\n"
            "## 5. 当前阶段的一句话建议\n建议"
        )
        self.assertTrue(has_complete_question_section(report))

    def test_numbered_heading_variants_count_as_complete(self) -> None:
        body = "具体行为推断与可操作出口，覆盖决策模式与自我欺骗，并给出可观察验证点。" * 3
        for heading in (
            "## 4. 关于你正在纠结的事",
            "## 4、关于你正在纠结的事",
            "## 4 关于你正在纠结的事",
        ):
            report = f"{heading}\n{body}\n\n## 5. 当前阶段的一句话建议\n建议"
            self.assertTrue(has_complete_question_section(report), heading)

    def test_missing_or_stub_section_still_needs_repair(self) -> None:
        self.assertFalse(has_complete_question_section("## 3. 关系\n正文\n\n## 5. 建议\n嗯"))
        stub = f"{QUESTION_SECTION_HEADING}\n太短了\n\n## 5. 当前阶段的一句话建议\n建议"
        self.assertFalse(has_complete_question_section(stub))


if __name__ == "__main__":
    unittest.main()
