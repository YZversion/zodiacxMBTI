"""78-card Rider–Waite deck and three-card draws."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Literal

Position = Literal["过去", "现在", "未来"]

MAJOR = [
    "愚者",
    "魔术师",
    "女祭司",
    "皇后",
    "皇帝",
    "教皇",
    "恋人",
    "战车",
    "力量",
    "隐者",
    "命运之轮",
    "正义",
    "倒吊人",
    "死神",
    "节制",
    "恶魔",
    "高塔",
    "星星",
    "月亮",
    "太阳",
    "审判",
    "世界",
]

SUITS = {
    "权杖": "Wands",
    "圣杯": "Cups",
    "宝剑": "Swords",
    "星币": "Pentacles",
}

RANKS = [
    "王牌",
    "二",
    "三",
    "四",
    "五",
    "六",
    "七",
    "八",
    "九",
    "十",
    "侍从",
    "骑士",
    "王后",
    "国王",
]


def _full_deck() -> list[str]:
    cards = [f"大阿卡纳·{name}" for name in MAJOR]
    for suit_zh in SUITS:
        for rank in RANKS:
            cards.append(f"{suit_zh}{rank}")
    assert len(cards) == 78, len(cards)
    return cards


DECK = _full_deck()


@dataclass(frozen=True)
class DrawnCard:
    name: str
    position: Position
    reversed: bool

    def label_zh(self) -> str:
        orient = "逆位" if self.reversed else "正位"
        return f"{self.position}：{self.name}（{orient}）"


def draw_three(rng: random.Random | None = None) -> list[DrawnCard]:
    """Past / present / future; independent upright/reversed per card."""
    r = rng or random.Random()
    picks = r.sample(DECK, 3)
    positions: tuple[Position, Position, Position] = ("过去", "现在", "未来")
    return [
        DrawnCard(name=name, position=pos, reversed=bool(r.getrandbits(1)))
        for name, pos in zip(picks, positions)
    ]
