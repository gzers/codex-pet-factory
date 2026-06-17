from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StateSpec:
    row: int
    state: str
    note: str
    frames: int


CELL_WIDTH = 192
CELL_HEIGHT = 208
COLUMNS = 8

DEFAULT_STATES = [
    StateSpec(0, "idle", "待机", 6),
    StateSpec(1, "running-right", "向右奔跑", 8),
    StateSpec(2, "running-left", "向左奔跑", 8),
    StateSpec(3, "waving", "挥手或打招呼", 4),
    StateSpec(4, "jumping", "跳跃或翻滚", 5),
    StateSpec(5, "failed", "失败或哭泣", 8),
    StateSpec(6, "waiting", "等待或躺倒", 6),
    StateSpec(7, "running", "原地循环动作", 6),
    StateSpec(8, "review", "趣味彩蛋动作", 6),
]


def pet_id_from_name(name: str) -> str:
    cleaned = []
    last_dash = False
    for char in name.lower().strip():
        if char.isascii() and char.isalnum():
            cleaned.append(char)
            last_dash = False
        elif not last_dash:
            cleaned.append("-")
            last_dash = True
    value = "".join(cleaned).strip("-")
    return value or "custom-pet"
