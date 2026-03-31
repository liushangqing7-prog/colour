# 图片颜色提取 + 色彩调整网站（React + FastAPI）

这是一个完整的前后端分离项目，专注于：

- 上传 JPEG/PNG 图片并预览
- 主色提取（K-Means / Mean Shift / Histogram）
- 色彩调整（HSV/HSL 的 Hue/Saturation/Value，Lab a/b 微调）
- Reinhard 色彩迁移（目标色板/目标图片）
- 调整前后对比、颜色复制、色板下载、结果图下载

---

## 目录结构

```text
.
├── backend/
│   ├── app/
│   │   ├── color_algorithms.py
│   │   ├── main.py
│   │   └── schemas.py
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── api/client.js
    │   ├── components/ColorSwatches.jsx
    │   ├── components/ImageCompare.jsx
    │   ├── App.jsx
    │   ├── main.jsx
    │   └── index.css
    ├── index.html
    ├── package.json
    ├── postcss.config.js
    ├── tailwind.config.js
    └── vite.config.js
```

---

## 后端（FastAPI）

### 安装

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

### 启动

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### API 接口

- `POST /api/extract-colors`
  - form-data: `file`, `algorithm(kmeans|meanshift|histogram)`, `n_colors`
- `POST /api/adjust-hsv`
  - form-data: `file`, `hue_shift`, `sat_scale`, `value_scale`, `mode(HSV|HSL)`
- `POST /api/adjust-lab`
  - form-data: `file`, `a_shift`, `b_shift`
- `POST /api/reinhard-transfer`
  - form-data: `source_file`, `target_file`

---

## 前端（React + Vite + Tailwind）

### 安装

```bash
cd frontend
npm install
```

### 启动

```bash
npm run dev
```

默认请求后端 `http://localhost:8000`。如需修改：

```bash
# frontend/.env
VITE_API_BASE=http://localhost:8000
```

---

## 算法说明（核心函数）

- `extract_colors_kmeans(img)`：K-Means 聚类提取主色
- `extract_colors_meanshift(img)`：Mean Shift 聚类提取主色
- `extract_colors_histogram(img)`：RGB 直方图峰值分析提色
- `adjust_hue_saturation(img, hue_shift, sat_scale, value_scale)`：HSV/HSL 调整
- `adjust_lab_channels(img, a_shift, b_shift)`：Lab 通道微调
- `reinhard_color_transfer(source_img, target_img)`：Reinhard 色彩迁移

---

## 功能使用流程

1. 上传源图片（可选再上传 Reinhard 目标图片）
2. 在“颜色提取”区域选择算法并提取颜色
3. 在“色彩调整”区域调节 Hue/Saturation/Value 或 Lab a/b
4. 点击对应按钮执行处理，查看前后对比图
5. 点击色块复制颜色值，下载色板，下载调整后结果图

---

## 依赖

- 后端：FastAPI, OpenCV, NumPy, scikit-learn, Pillow
- 前端：React, Vite, Tailwind CSS

