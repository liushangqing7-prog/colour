from __future__ import annotations

import base64
from io import BytesIO

import numpy as np
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image

from .color_algorithms import (
    adjust_hue_saturation,
    adjust_lab_channels,
    extract_colors_histogram,
    extract_colors_kmeans,
    extract_colors_meanshift,
    image_to_png_bytes,
    reinhard_color_transfer,
)
from .schemas import AdjustResponse, ColorExtractResponse

app = FastAPI(title="Color Extract & Adjustment API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def read_image(file: UploadFile) -> np.ndarray:
    if file.content_type not in {"image/jpeg", "image/png"}:
        raise HTTPException(status_code=400, detail="Only JPEG and PNG are supported")
    data = await file.read()
    try:
        img = Image.open(BytesIO(data)).convert("RGB")
        return np.array(img)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid image file") from exc


def to_base64_png(img: np.ndarray) -> str:
    encoded = image_to_png_bytes(img)
    return base64.b64encode(encoded).decode("utf-8")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/extract-colors", response_model=ColorExtractResponse)
async def extract_colors(
    file: UploadFile = File(...),
    algorithm: str = Form("kmeans"),
    n_colors: int = Form(6),
) -> ColorExtractResponse:
    img = await read_image(file)
    algo = algorithm.lower()

    if algo == "kmeans":
        swatches = extract_colors_kmeans(img, n_colors=n_colors)
    elif algo == "meanshift":
        swatches = extract_colors_meanshift(img)
    elif algo == "histogram":
        swatches = extract_colors_histogram(img, top_n=n_colors)
    else:
        raise HTTPException(status_code=400, detail="Unknown algorithm")

    return ColorExtractResponse(
        algorithm=algo,
        colors=[{"rgb": s.rgb, "hex": s.hex, "ratio": s.ratio} for s in swatches],
    )


@app.post("/api/adjust-hsv", response_model=AdjustResponse)
async def adjust_hsv(
    file: UploadFile = File(...),
    hue_shift: float = Form(0),
    sat_scale: float = Form(1),
    value_scale: float = Form(1),
    mode: str = Form("HSV"),
) -> AdjustResponse:
    img = await read_image(file)
    out = adjust_hue_saturation(img, hue_shift=hue_shift, sat_scale=sat_scale, value_scale=value_scale, mode=mode)
    return AdjustResponse(image_base64=to_base64_png(out))


@app.post("/api/adjust-lab", response_model=AdjustResponse)
async def adjust_lab(
    file: UploadFile = File(...),
    a_shift: float = Form(0),
    b_shift: float = Form(0),
) -> AdjustResponse:
    img = await read_image(file)
    out = adjust_lab_channels(img, a_shift=a_shift, b_shift=b_shift)
    return AdjustResponse(image_base64=to_base64_png(out))


@app.post("/api/reinhard-transfer", response_model=AdjustResponse)
async def reinhard_transfer(
    source_file: UploadFile = File(...),
    target_file: UploadFile = File(...),
) -> AdjustResponse:
    source = await read_image(source_file)
    target = await read_image(target_file)
    out = reinhard_color_transfer(source, target)
    return AdjustResponse(image_base64=to_base64_png(out))
