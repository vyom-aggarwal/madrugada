"""Pydantic data models. Types and validation only; no domain logic."""
import math
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

from app.config import load_config

SLOTS_PER_DAY = 96  # mirrors config.yaml grid.slots_per_day; checked in tests

Provenance = Literal["real_cached", "synthetic"]
HHMM_RE = r"^([01]\d|2[0-3]):[0-5]\d$"
HHMM = Field(pattern=HHMM_RE)
_CFG = load_config()


def _minutes(hhmm: str) -> int:
    h, m = map(int, hhmm.split(":"))
    return h * 60 + m


class PlanRequest(BaseModel):
    """API request for one day's plan. Defaults come from config.yaml `shift`."""
    day_id: str = Field(min_length=1, max_length=200)
    paid_hours: float = Field(default=_CFG["shift"]["default_paid_hours"], ge=2, le=12)
    earliest: str = Field(default=_CFG["shift"]["default_earliest_start"], pattern=HHMM_RE)
    latest: str = Field(default=_CFG["shift"]["default_latest_end"], pattern=HHMM_RE)
    oracle: bool = False

    @model_validator(mode="after")
    def _window_fits(self):
        step = _CFG["grid"]["slot_minutes"]
        e, l = _minutes(self.earliest), _minutes(self.latest)
        if e % step or l % step:
            raise ValueError(f"earliest and latest must be on the {step}-minute grid")
        if e >= l:
            raise ValueError(f"earliest ({self.earliest}) must be before latest ({self.latest})")
        paid = math.ceil(self.paid_hours * 60 / step - 1e-9) * step  # minutes actually scheduled
        if paid < _CFG["shift"]["min_block_hours"] * 60:
            raise ValueError(f"paid_hours must be at least min_block_hours ({_CFG['shift']['min_block_hours']} h)")
        if l - e < paid:  # a single block needs no gap; two blocks would need paid + min_gap
            raise ValueError(f"window {self.earliest}-{self.latest} ({(l - e) / 60:g} h) cannot hold "
                             f"{paid / 60:g} paid hours")
        return self


class DayRecord(BaseModel):
    id: str
    label: str
    region: str
    provenance: Provenance
    date: str | None = Field(default=None, pattern=r"^\d{4}-\d{2}-\d{2}$")  # local date; forecast needs it
    temp_f: list[float]
    rh: list[float]
    solar_wm2: list[float]
    pm25_ugm3: list[float]

    @field_validator("temp_f", "rh", "solar_wm2", "pm25_ugm3")
    @classmethod
    def _full_day(cls, v: list[float]) -> list[float]:
        if len(v) != SLOTS_PER_DAY:
            raise ValueError(f"expected {SLOTS_PER_DAY} slots, got {len(v)}")
        return v


class ShiftRequest(BaseModel):
    day_id: str
    paid_hours_target: float = Field(gt=0, le=16)
    earliest_start: str = HHMM
    latest_end: str = HHMM
    min_block_hours: float = 2.0
    min_gap_hours: float = 1.0
    max_blocks: int = Field(default=2, ge=1, le=2)
    oracle: bool = False  # True = plan on day D truth (upper bound), labeled ORACLE

    @model_validator(mode="after")
    def _window_order(self):
        if self.earliest_start >= self.latest_end:
            raise ValueError("earliest_start must be before latest_end")
        return self


class Block(BaseModel):
    start_slot: int = Field(ge=0, lt=SLOTS_PER_DAY)
    end_slot: int = Field(gt=0, le=SLOTS_PER_DAY)  # exclusive

    @model_validator(mode="after")
    def _ordered(self):
        if self.end_slot <= self.start_slot:
            raise ValueError("end_slot must be after start_slot")
        return self


class ExposureMetrics(BaseModel):
    hours_ge_95f: float
    hours_ge_80f: float
    hours_aqi_ge_101: float
    hours_aqi_ge_151: float
    dual_hazard_hours: float
    paid_hours: float
    paid_hours_retained_pct: float


class ShiftPlan(BaseModel):
    name: str  # e.g. "optimized", "B1", "B2", "B3"
    blocks: list[Block] = Field(min_length=1, max_length=2)
    cost: float
    metrics: ExposureMetrics | None = None


class ParetoPoint(BaseModel):
    paid_fraction: float
    heat_smoke_ratio: float
    heat_hours: float
    smoke_hours: float
    paid_hours: float
    plan: ShiftPlan


class PlanResponse(BaseModel):
    day_id: str
    provenance: Provenance
    oracle: bool
    label: str  # "ORACLE" when oracle=True, else "FORECAST"
    plan: ShiftPlan
    baselines: list[ShiftPlan] = []
    pareto: list[ParetoPoint] = []
    warnings: list[str] = []
