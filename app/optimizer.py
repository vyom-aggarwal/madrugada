"""Exhaustive 1-2 block shift search on the slot grid (numpy prefix sums) and a Pareto sweep.

Plans have exactly ceil(target / slot) worked slots, which satisfies paid hours >= target while
keeping paid hours constant across compared plans.
"""
import math

import numpy as np

from app.config import load_config
from app.exposure import exposure, hhmm_to_slot, slot_cost, slot_hours
from app.models import Block, ParetoPoint, ShiftPlan


def hours_to_slots(hours: float, cfg: dict | None = None) -> int:
    return math.ceil(hours / slot_hours(cfg) - 1e-9)


def search(cost, n_work: int, earliest: int, latest: int, min_block: int, min_gap: int,
           max_blocks: int = 2, tie_break: str = "early") -> tuple[float, list[tuple[int, int]]]:
    """Exact minimum over every layout of 1 or 2 blocks with n_work slots total inside [earliest, latest).

    Each block >= min_block slots, gap >= min_gap slots. Ties broken by: lower cost, fewer blocks,
    then (tie_break="early") earlier start, earlier end of block 1, earlier start of block 2, or
    (tie_break="late") the same keys latest-first. Returns (cost, [(start, end)]).
    """
    if tie_break not in ("early", "late"):
        raise ValueError(f"tie_break must be 'early' or 'late', got {tie_break!r}")
    sign = 1 if tie_break == "early" else -1
    P = np.concatenate([[0.0], np.cumsum(np.asarray(cost, dtype=float))])
    rows = []  # (cost, n_blocks, s1, e1, s2)
    if n_work >= min_block:
        s = np.arange(earliest, latest - n_work + 1)
        if s.size:
            c = P[s + n_work] - P[s]
            rows.append(np.column_stack([c, np.ones_like(c), s, s + n_work, np.full_like(c, -1)]))
    if max_blocks >= 2:
        for a in range(min_block, n_work - min_block + 1):
            b = n_work - a
            s1 = np.arange(earliest, latest - a - min_gap - b + 1)
            s2 = np.arange(earliest + a + min_gap, latest - b + 1)
            if not (s1.size and s2.size):
                continue
            S1, S2 = np.meshgrid(s1, s2, indexing="ij")
            ok = S2 >= S1 + a + min_gap
            S1, S2 = S1[ok], S2[ok]
            c = (P[S1 + a] - P[S1]) + (P[S2 + b] - P[S2])
            rows.append(np.column_stack([c, np.full(c.shape, 2.0), S1, S1 + a, S2]))
    if not rows:
        raise ValueError("no feasible shift for these constraints")
    r = np.concatenate(rows)
    best = r[np.lexsort((sign * r[:, 4], sign * r[:, 3], sign * r[:, 2], r[:, 1], np.round(r[:, 0], 9)))[0]]
    s1, e1 = int(best[2]), int(best[3])
    blocks = [(s1, e1)]
    if best[1] == 2:
        s2 = int(best[4])
        blocks.append((s2, s2 + n_work - (e1 - s1)))
    return float(best[0]), blocks


def optimize(temp_f, aqi, paid_hours_target: float | None = None, earliest_start: str | None = None,
             latest_end: str | None = None, min_block_hours: float | None = None,
             min_gap_hours: float | None = None, max_blocks: int | None = None,
             weights: dict | None = None, cfg: dict | None = None, name: str = "optimized",
             tie_break: str = "early") -> ShiftPlan:
    """Min-cost shift on (temp_f, aqi). Unset arguments use config.yaml `shift` defaults."""
    c = cfg or load_config()
    s = c["shift"]

    def pick(v, key):
        return s[key] if v is None else v

    total, blocks = search(
        slot_cost(temp_f, aqi, weights, c),
        hours_to_slots(pick(paid_hours_target, "default_paid_hours"), c),
        hhmm_to_slot(pick(earliest_start, "default_earliest_start"), c),
        hhmm_to_slot(pick(latest_end, "default_latest_end"), c),
        hours_to_slots(pick(min_block_hours, "min_block_hours"), c),
        hours_to_slots(pick(min_gap_hours, "min_gap_hours"), c),
        pick(max_blocks, "max_blocks"),
        tie_break,
    )
    return ShiftPlan(name=name, blocks=[Block(start_slot=a, end_slot=b) for a, b in blocks], cost=total)


def dominates(p: ParetoPoint, q: ParetoPoint) -> bool:
    """p dominates q: no worse on all of (heat_hours down, smoke_hours down, paid_hours up), better on one."""
    no_worse = p.heat_hours <= q.heat_hours and p.smoke_hours <= q.smoke_hours and p.paid_hours >= q.paid_hours
    better = p.heat_hours < q.heat_hours or p.smoke_hours < q.smoke_hours or p.paid_hours > q.paid_hours
    return no_worse and better


def non_dominated(points: list[ParetoPoint]) -> list[ParetoPoint]:
    keep, seen = [], set()
    for p in points:
        key = (p.heat_hours, p.smoke_hours, p.paid_hours)
        if key in seen or any(dominates(q, p) for q in points):
            continue
        seen.add(key)
        keep.append(p)
    return keep


def pareto(temp_f, aqi, paid_hours_target: float | None = None, cfg: dict | None = None,
           **shift_kw) -> list[ParetoPoint]:
    """Sweep paid fraction (config pareto) x heat/smoke weight ratio; return the non-dominated set.

    heat_hours = hours >= shade trigger (80F); smoke_hours = hours AQI >= 101.
    """
    c = cfg or load_config()
    p = c["pareto"]
    target = c["shift"]["default_paid_hours"] if paid_hours_target is None else paid_hours_target
    n = int(round((p["paid_fraction_max"] - p["paid_fraction_min"]) / p["paid_fraction_step"])) + 1
    points = []
    for frac in np.round(p["paid_fraction_max"] - p["paid_fraction_step"] * np.arange(n), 6):
        for ratio in p["heat_smoke_ratios"]:
            w = {"w_heat": ratio * c["weights"]["w_smoke"], "w_smoke": c["weights"]["w_smoke"]}
            try:
                plan = optimize(temp_f, aqi, paid_hours_target=float(frac) * target, weights=w, cfg=c,
                                name=f"pareto_{frac:.2f}_{ratio:g}", **shift_kw)
            except ValueError:  # e.g. reduced hours fall below min_block_hours: skip that fraction
                continue
            m = exposure(temp_f, aqi, plan.blocks, target, c)
            points.append(ParetoPoint(paid_fraction=float(frac), heat_smoke_ratio=ratio,
                                      heat_hours=m.hours_ge_80f, smoke_hours=m.hours_aqi_ge_101,
                                      paid_hours=m.paid_hours, plan=plan.model_copy(update={"metrics": m})))
    return non_dominated(points)
