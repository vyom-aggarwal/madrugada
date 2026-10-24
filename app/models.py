"""Pydantic data models. Types and validation only; no domain logic."""
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

SLOTS_PER_DAY = 96  # mirrors config.yaml grid.slots_per_day; checked in tests

Provenance = Literal["real_cached", "synthetic"]
HHMM = Field(pattern=r"^([01]\d|2[0-3]):[0-5]\d$")


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
