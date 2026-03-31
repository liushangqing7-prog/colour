"""Core color extraction and color adjustment algorithms."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import cv2
import numpy as np
from sklearn.cluster import KMeans, MeanShift, estimate_bandwidth


@dataclass
class ColorSwatch:
    rgb: tuple[int, int, int]
    hex: str
    ratio: float


def _to_uint8_image(img: np.ndarray) -> np.ndarray:
    if img.dtype != np.uint8:
        img = np.clip(img, 0, 255).astype(np.uint8)
    return img


def _rgb_hex(rgb: Iterable[int]) -> str:
    r, g, b = [int(x) for x in rgb]
    return f"#{r:02X}{g:02X}{b:02X}"


def extract_colors_kmeans(img: np.ndarray, n_colors: int = 6) -> list[ColorSwatch]:
    """Extract dominant colors via K-Means clustering."""
    pixels = img.reshape(-1, 3).astype(np.float32)
    model = KMeans(n_clusters=n_colors, random_state=42, n_init=10)
    labels = model.fit_predict(pixels)

    counts = np.bincount(labels)
    centers = model.cluster_centers_.astype(np.uint8)

    order = np.argsort(counts)[::-1]
    total = counts.sum()
    return [
        ColorSwatch(
            rgb=tuple(int(v) for v in centers[idx]),
            hex=_rgb_hex(centers[idx]),
            ratio=float(counts[idx] / total),
        )
        for idx in order
    ]


def extract_colors_meanshift(img: np.ndarray, quantile: float = 0.15) -> list[ColorSwatch]:
    """Extract dominant colors via Mean Shift clustering."""
    pixels = img.reshape(-1, 3).astype(np.float32)

    sample_size = min(len(pixels), 8000)
    sample_idx = np.random.default_rng(42).choice(len(pixels), size=sample_size, replace=False)
    sample = pixels[sample_idx]

    bandwidth = estimate_bandwidth(sample, quantile=quantile, n_samples=min(4000, sample_size))
    if not np.isfinite(bandwidth) or bandwidth <= 0:
        bandwidth = 25.0

    model = MeanShift(bandwidth=bandwidth, bin_seeding=True)
    labels = model.fit_predict(sample)

    counts = np.bincount(labels)
    centers = np.clip(model.cluster_centers_, 0, 255).astype(np.uint8)

    order = np.argsort(counts)[::-1]
    total = counts.sum()
    return [
        ColorSwatch(
            rgb=tuple(int(v) for v in centers[idx]),
            hex=_rgb_hex(centers[idx]),
            ratio=float(counts[idx] / total),
        )
        for idx in order[:10]
    ]


def extract_colors_histogram(img: np.ndarray, bins_per_channel: int = 8, top_n: int = 8) -> list[ColorSwatch]:
    """Extract dominant colors by 3D RGB histogram peaks."""
    bin_size = 256 // bins_per_channel
    quantized = (img // bin_size).astype(np.int32)

    flat = quantized.reshape(-1, 3)
    keys = flat[:, 0] * bins_per_channel * bins_per_channel + flat[:, 1] * bins_per_channel + flat[:, 2]
    counts = np.bincount(keys, minlength=bins_per_channel**3)

    top_idx = np.argsort(counts)[::-1][:top_n]
    total = counts.sum()

    swatches: list[ColorSwatch] = []
    for idx in top_idx:
        if counts[idx] == 0:
            continue
        r_bin = idx // (bins_per_channel * bins_per_channel)
        g_bin = (idx // bins_per_channel) % bins_per_channel
        b_bin = idx % bins_per_channel

        rgb = np.array([(r_bin + 0.5), (g_bin + 0.5), (b_bin + 0.5)]) * bin_size
        rgb = np.clip(rgb, 0, 255).astype(np.uint8)
        swatches.append(
            ColorSwatch(
                rgb=(int(rgb[0]), int(rgb[1]), int(rgb[2])),
                hex=_rgb_hex(rgb),
                ratio=float(counts[idx] / total),
            )
        )

    return swatches


def adjust_hue_saturation(
    img: np.ndarray,
    hue_shift: float,
    sat_scale: float,
    value_scale: float,
    mode: str = "HSV",
) -> np.ndarray:
    """Adjust hue/saturation/value(lightness) in HSV or HSL color spaces."""
    img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    if mode.upper() == "HSL":
        hls = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HLS).astype(np.float32)
        hls[..., 0] = (hls[..., 0] + hue_shift / 2.0) % 180
        hls[..., 2] = np.clip(hls[..., 2] * sat_scale, 0, 255)
        hls[..., 1] = np.clip(hls[..., 1] * value_scale, 0, 255)
        out_bgr = cv2.cvtColor(hls.astype(np.uint8), cv2.COLOR_HLS2BGR)
    else:
        hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[..., 0] = (hsv[..., 0] + hue_shift / 2.0) % 180
        hsv[..., 1] = np.clip(hsv[..., 1] * sat_scale, 0, 255)
        hsv[..., 2] = np.clip(hsv[..., 2] * value_scale, 0, 255)
        out_bgr = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

    return cv2.cvtColor(out_bgr, cv2.COLOR_BGR2RGB)


def adjust_lab_channels(img: np.ndarray, a_shift: float, b_shift: float) -> np.ndarray:
    """Fine-tune Lab a/b channels."""
    img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB).astype(np.float32)

    lab[..., 1] = np.clip(lab[..., 1] + a_shift, 0, 255)
    lab[..., 2] = np.clip(lab[..., 2] + b_shift, 0, 255)

    out_bgr = cv2.cvtColor(lab.astype(np.uint8), cv2.COLOR_LAB2BGR)
    return cv2.cvtColor(out_bgr, cv2.COLOR_BGR2RGB)


def reinhard_color_transfer(source_img: np.ndarray, target_img: np.ndarray) -> np.ndarray:
    """Apply Reinhard color transfer from target image to source image."""
    src_bgr = cv2.cvtColor(source_img, cv2.COLOR_RGB2BGR)
    tgt_bgr = cv2.cvtColor(target_img, cv2.COLOR_RGB2BGR)

    src_lab = cv2.cvtColor(src_bgr, cv2.COLOR_BGR2LAB).astype(np.float32)
    tgt_lab = cv2.cvtColor(tgt_bgr, cv2.COLOR_BGR2LAB).astype(np.float32)

    src_mean, src_std = cv2.meanStdDev(src_lab)
    tgt_mean, tgt_std = cv2.meanStdDev(tgt_lab)

    src_mean = src_mean.reshape(1, 1, 3)
    src_std = np.maximum(src_std.reshape(1, 1, 3), 1e-6)
    tgt_mean = tgt_mean.reshape(1, 1, 3)
    tgt_std = np.maximum(tgt_std.reshape(1, 1, 3), 1e-6)

    transfer = (src_lab - src_mean) * (tgt_std / src_std) + tgt_mean
    transfer = np.clip(transfer, 0, 255).astype(np.uint8)

    out_bgr = cv2.cvtColor(transfer, cv2.COLOR_LAB2BGR)
    return cv2.cvtColor(out_bgr, cv2.COLOR_BGR2RGB)


def image_to_png_bytes(img: np.ndarray) -> bytes:
    rgb = _to_uint8_image(img)
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    ok, encoded = cv2.imencode(".png", bgr)
    if not ok:
        raise RuntimeError("Failed to encode image")
    return encoded.tobytes()
