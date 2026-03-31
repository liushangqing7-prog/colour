import { useMemo, useState } from 'react'
import ColorSwatches from './components/ColorSwatches'
import ImageCompare from './components/ImageCompare'
import { adjustHSV, adjustLab, extractColors, reinhardTransfer } from './api/client'

const ALGORITHMS = [
  { value: 'kmeans', label: 'K-Means 聚类' },
  { value: 'meanshift', label: 'Mean Shift 聚类' },
  { value: 'histogram', label: '颜色直方图分析' },
]

export default function App() {
  const [imageFile, setImageFile] = useState(null)
  const [targetFile, setTargetFile] = useState(null)
  const [algorithm, setAlgorithm] = useState('kmeans')
  const [nColors, setNColors] = useState(6)
  const [colors, setColors] = useState([])

  const [hueShift, setHueShift] = useState(0)
  const [satScale, setSatScale] = useState(1)
  const [valueScale, setValueScale] = useState(1)
  const [spaceMode, setSpaceMode] = useState('HSV')

  const [aShift, setAShift] = useState(0)
  const [bShift, setBShift] = useState(0)

  const [adjustedUrl, setAdjustedUrl] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  const previewUrl = useMemo(() => (imageFile ? URL.createObjectURL(imageFile) : ''), [imageFile])

  const runExtract = async () => {
    if (!imageFile) return
    setBusy(true)
    setError('')
    try {
      const res = await extractColors(imageFile, algorithm, nColors)
      setColors(res.colors || [])
    } catch (e) {
      setError(String(e.message || e))
    } finally {
      setBusy(false)
    }
  }

  const runHSV = async () => {
    if (!imageFile) return
    setBusy(true)
    setError('')
    try {
      const res = await adjustHSV(imageFile, { hueShift, satScale, valueScale, mode: spaceMode })
      setAdjustedUrl(`data:image/png;base64,${res.image_base64}`)
    } catch (e) {
      setError(String(e.message || e))
    } finally {
      setBusy(false)
    }
  }

  const runLab = async () => {
    if (!imageFile) return
    setBusy(true)
    setError('')
    try {
      const res = await adjustLab(imageFile, { aShift, bShift })
      setAdjustedUrl(`data:image/png;base64,${res.image_base64}`)
    } catch (e) {
      setError(String(e.message || e))
    } finally {
      setBusy(false)
    }
  }

  const runReinhard = async () => {
    if (!imageFile || !targetFile) return
    setBusy(true)
    setError('')
    try {
      const res = await reinhardTransfer(imageFile, targetFile)
      setAdjustedUrl(`data:image/png;base64,${res.image_base64}`)
    } catch (e) {
      setError(String(e.message || e))
    } finally {
      setBusy(false)
    }
  }

  const downloadAdjusted = () => {
    if (!adjustedUrl) return
    const a = document.createElement('a')
    a.href = adjustedUrl
    a.download = 'adjusted.png'
    a.click()
  }

  return (
    <main className="min-h-screen bg-slate-100 px-4 py-8">
      <div className="mx-auto max-w-6xl space-y-5">
        <header className="rounded-xl bg-white p-6 shadow">
          <h1 className="text-2xl font-bold">图片颜色提取与色彩调整工作台</h1>
          <p className="mt-2 text-sm text-slate-600">支持 K-Means / Mean Shift / Histogram 提色，支持 HSV/HSL、Lab、Reinhard 色彩迁移。</p>
        </header>

        <section className="rounded-xl bg-white p-4 shadow">
          <h2 className="mb-3 text-lg font-semibold">1) 图片上传</h2>
          <div className="grid gap-3 md:grid-cols-2">
            <input type="file" accept="image/png,image/jpeg" onChange={(e) => setImageFile(e.target.files?.[0] || null)} />
            <input type="file" accept="image/png,image/jpeg" onChange={(e) => setTargetFile(e.target.files?.[0] || null)} />
          </div>
          <p className="mt-2 text-xs text-slate-500">左侧：待处理图片；右侧：Reinhard 目标图片（可选，执行色彩迁移时需要）。</p>
        </section>

        <section className="rounded-xl bg-white p-4 shadow">
          <h2 className="mb-3 text-lg font-semibold">2) 颜色提取</h2>
          <div className="grid gap-3 md:grid-cols-4">
            <select value={algorithm} onChange={(e) => setAlgorithm(e.target.value)} className="rounded border p-2">
              {ALGORITHMS.map((a) => (
                <option key={a.value} value={a.value}>
                  {a.label}
                </option>
              ))}
            </select>
            <input
              type="number"
              min={3}
              max={12}
              value={nColors}
              onChange={(e) => setNColors(Number(e.target.value))}
              className="rounded border p-2"
            />
            <button className="rounded bg-indigo-600 px-3 py-2 text-white" onClick={runExtract} disabled={busy || !imageFile}>
              提取颜色
            </button>
          </div>
        </section>

        <section className="rounded-xl bg-white p-4 shadow">
          <h2 className="mb-3 text-lg font-semibold">3) 色彩调整</h2>
          <div className="grid gap-4 lg:grid-cols-2">
            <div className="space-y-3 rounded border p-3">
              <h3 className="font-medium">HSV / HSL 调整</h3>
              <label className="block text-sm">色彩空间</label>
              <select value={spaceMode} onChange={(e) => setSpaceMode(e.target.value)} className="w-full rounded border p-2">
                <option value="HSV">HSV</option>
                <option value="HSL">HSL</option>
              </select>
              <label className="block text-sm">Hue: {hueShift}</label>
              <input type="range" min={-180} max={180} value={hueShift} onChange={(e) => setHueShift(Number(e.target.value))} className="w-full" />
              <label className="block text-sm">Saturation: {satScale.toFixed(2)}</label>
              <input type="range" min={0} max={3} step={0.01} value={satScale} onChange={(e) => setSatScale(Number(e.target.value))} className="w-full" />
              <label className="block text-sm">Value/Brightness: {valueScale.toFixed(2)}</label>
              <input
                type="range"
                min={0}
                max={3}
                step={0.01}
                value={valueScale}
                onChange={(e) => setValueScale(Number(e.target.value))}
                className="w-full"
              />
              <button className="rounded bg-emerald-600 px-3 py-2 text-white" onClick={runHSV} disabled={busy || !imageFile}>
                应用 HSV/HSL
              </button>
            </div>

            <div className="space-y-3 rounded border p-3">
              <h3 className="font-medium">Lab 微调 + Reinhard</h3>
              <label className="block text-sm">a 通道偏移: {aShift}</label>
              <input type="range" min={-128} max={128} value={aShift} onChange={(e) => setAShift(Number(e.target.value))} className="w-full" />
              <label className="block text-sm">b 通道偏移: {bShift}</label>
              <input type="range" min={-128} max={128} value={bShift} onChange={(e) => setBShift(Number(e.target.value))} className="w-full" />
              <div className="flex gap-2">
                <button className="rounded bg-cyan-700 px-3 py-2 text-white" onClick={runLab} disabled={busy || !imageFile}>
                  应用 Lab
                </button>
                <button className="rounded bg-fuchsia-700 px-3 py-2 text-white" onClick={runReinhard} disabled={busy || !imageFile || !targetFile}>
                  Reinhard 迁移
                </button>
                <button className="rounded bg-slate-800 px-3 py-2 text-white" onClick={downloadAdjusted} disabled={!adjustedUrl}>
                  下载结果
                </button>
              </div>
            </div>
          </div>
          {error && <div className="mt-3 rounded bg-red-100 p-2 text-sm text-red-700">{error}</div>}
        </section>

        <ImageCompare beforeUrl={previewUrl} afterUrl={adjustedUrl} />
        <ColorSwatches colors={colors} />
      </div>
    </main>
  )
}
