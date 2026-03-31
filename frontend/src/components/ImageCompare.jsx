export default function ImageCompare({ beforeUrl, afterUrl }) {
  if (!beforeUrl) return null

  return (
    <div className="grid gap-4 md:grid-cols-2">
      <div className="rounded-xl bg-white p-4 shadow">
        <h3 className="mb-2 text-lg font-semibold">调整前</h3>
        <img src={beforeUrl} alt="before" className="max-h-[420px] w-full rounded object-contain" />
      </div>
      <div className="rounded-xl bg-white p-4 shadow">
        <h3 className="mb-2 text-lg font-semibold">调整后</h3>
        {afterUrl ? (
          <img src={afterUrl} alt="after" className="max-h-[420px] w-full rounded object-contain" />
        ) : (
          <div className="flex h-[240px] items-center justify-center rounded bg-slate-100 text-slate-500">尚未调整</div>
        )}
      </div>
    </div>
  )
}
