const API_BASE = import.meta.env.VITE_API_BASE ?? 'http://localhost:8000'

async function postForm(path, formData) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    body: formData,
  })

  if (!res.ok) {
    const message = await res.text()
    throw new Error(message || 'Request failed')
  }

  return res.json()
}

export function extractColors(file, algorithm, nColors) {
  const form = new FormData()
  form.append('file', file)
  form.append('algorithm', algorithm)
  form.append('n_colors', String(nColors))
  return postForm('/api/extract-colors', form)
}

export function adjustHSV(file, { hueShift, satScale, valueScale, mode }) {
  const form = new FormData()
  form.append('file', file)
  form.append('hue_shift', String(hueShift))
  form.append('sat_scale', String(satScale))
  form.append('value_scale', String(valueScale))
  form.append('mode', mode)
  return postForm('/api/adjust-hsv', form)
}

export function adjustLab(file, { aShift, bShift }) {
  const form = new FormData()
  form.append('file', file)
  form.append('a_shift', String(aShift))
  form.append('b_shift', String(bShift))
  return postForm('/api/adjust-lab', form)
}

export function reinhardTransfer(sourceFile, targetFile) {
  const form = new FormData()
  form.append('source_file', sourceFile)
  form.append('target_file', targetFile)
  return postForm('/api/reinhard-transfer', form)
}
