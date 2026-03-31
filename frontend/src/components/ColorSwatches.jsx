export default function ColorSwatches({ colors }) {
  const copyHex = async (hex) => {
    try {
      await navigator.clipboard.writeText(hex)
      alert(`Copied ${hex}`)
    } catch {
      alert('Clipboard copy failed')
    }
  }

  const downloadPalette = () => {
    const content = colors.map((c) => `${c.hex}, ${c.ratio.toFixed(3)}`).join('\n')
    const blob = new Blob([content], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'palette.txt'
    a.click()
    URL.revokeObjectURL(url)
  }

  if (!colors.length) return null

  return (
    <div className="rounded-xl bg-white p-4 shadow">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-lg font-semibold">提取颜色</h3>
        <button className="rounded bg-slate-800 px-3 py-1 text-sm text-white" onClick={downloadPalette}>
          下载色板
        </button>
      </div>
      <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
        {colors.map((c, idx) => (
          <button
            key={`${c.hex}-${idx}`}
            className="overflow-hidden rounded-lg border text-left"
            onClick={() => copyHex(c.hex)}
            title="点击复制颜色值"
          >
            <div style={{ backgroundColor: c.hex }} className="h-16 w-full" />
            <div className="p-2 text-xs">
              <div className="font-medium">{c.hex}</div>
              <div className="text-slate-600">{(c.ratio * 100).toFixed(1)}%</div>
            </div>
          </button>
        ))}
      </div>
    </div>
  )
}
