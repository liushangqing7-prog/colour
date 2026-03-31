from __future__ import annotations

from pydantic import BaseModel, Field


class ColorExtractResponse(BaseModel):
    algorithm: str
    colors: list[dict]


class AdjustResponse(BaseModel):
    image_base64: str


class HSVAdjustRequest(BaseModel):
    hue_shift: float = Field(0, ge=-180, le=180)
    sat_scale: float = Field(1, ge=0, le=3)
    value_scale: float = Field(1, ge=0, le=3)
    mode: str = Field("HSV")


class LabAdjustRequest(BaseModel):
    a_shift: float = Field(0, ge=-128, le=128)
    b_shift: float = Field(0, ge=-128, le=128)
