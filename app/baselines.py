"""Baselines from config.yaml: B1 and B2 fixed shifts, B3 heat-only optimizer.

Every plan's `cost` is scored with the same (default or given) dual-hazard weights so costs are
comparable; B3 only *chooses* its blocks with its heat-only weights.
"""
from app.config import load_config
from app.exposure import hhmm_to_slot, plan_cost
from app.models import Block, ShiftPlan
from app.optimizer import optimize


def fixed(name: str, temp_f, aqi, weights: dict | None = None, cfg: dict | None = None) -> ShiftPlan:
    c = cfg or load_config()
    b = c["baselines"][name]
    blocks = [Block(start_slot=hhmm_to_slot(b["start"], c), end_slot=hhmm_to_slot(b["end"], c))]
    return ShiftPlan(name=name, blocks=blocks, cost=plan_cost(blocks, temp_f, aqi, weights, c))


def b1(temp_f, aqi, weights=None, cfg=None) -> ShiftPlan:
    return fixed("B1", temp_f, aqi, weights, cfg)


def b2(temp_f, aqi, weights=None, cfg=None) -> ShiftPlan:
    return fixed("B2", temp_f, aqi, weights, cfg)


def b3(temp_f, aqi, weights=None, cfg=None, **shift_kw) -> ShiftPlan:
    c = cfg or load_config()
    heat_only = {**(weights or {}), **{k: v for k, v in c["baselines"]["B3"].items() if k.startswith("w_")}}
    plan = optimize(temp_f, aqi, weights=heat_only, cfg=c, name="B3", **shift_kw)
    return plan.model_copy(update={"cost": plan_cost(plan.blocks, temp_f, aqi, weights, c)})


def all_baselines(temp_f, aqi, weights=None, cfg=None, **shift_kw) -> list[ShiftPlan]:
    return [b1(temp_f, aqi, weights, cfg), b2(temp_f, aqi, weights, cfg), b3(temp_f, aqi, weights, cfg, **shift_kw)]
