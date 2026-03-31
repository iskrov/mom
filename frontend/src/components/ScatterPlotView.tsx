import { useEffect, useMemo, useRef, useState, type MouseEvent } from 'react'

import type { TrackResult } from '../types'

interface ScatterPlotViewProps {
  rows: TrackResult[]
  selectedTrackId: number | null
  onSelectTrack: (track: TrackResult) => void
}

const WIDTH = 960
const HEIGHT = 460
const MARGIN = { top: 24, right: 20, bottom: 48, left: 72 }
const X_TICKS = 6
const Y_TICKS = 6

function compact(n: number): string {
  return Intl.NumberFormat('en-US', { notation: 'compact', maximumFractionDigits: 1 }).format(n)
}

function formatPlaysAxis(n: number): string {
  return Intl.NumberFormat('en-US', { notation: 'compact', maximumFractionDigits: 1 })
    .format(n)
    .replace('K', 'k')
}

function formatLikesAxis(n: number): string {
  return Intl.NumberFormat('en-US', { notation: 'compact', maximumFractionDigits: 1 })
    .format(n)
    .replace('K', 'k')
}

function niceStep(maxValue: number, ticks: number): number {
  const raw = Math.max(1, maxValue) / Math.max(1, ticks)
  const magnitude = 10 ** Math.floor(Math.log10(raw))
  const normalized = raw / magnitude
  const multiplier = normalized <= 1 ? 1 : normalized <= 2 ? 2 : normalized <= 5 ? 5 : 10
  return multiplier * magnitude
}

function niceUpper(maxValue: number, ticks: number): number {
  const step = niceStep(maxValue, ticks)
  return Math.max(step * ticks, step)
}

export function ScatterPlotView({ rows, selectedTrackId, onSelectTrack }: ScatterPlotViewProps) {
  const svgRef = useRef<SVGSVGElement | null>(null)
  const dragStartRef = useRef<{
    x: number
    y: number
    xDomain: [number, number]
    yDomain: [number, number]
  } | null>(null)
  const [isDragging, setIsDragging] = useState(false)
  const points = useMemo(
    () => rows.filter((row) => !row.is_reference_original && row.plays >= 0 && row.likes >= 0),
    [rows],
  )

  const xMax = useMemo(() => Math.max(1, ...points.map((p) => p.plays)), [points])
  const yMax = useMemo(() => Math.max(1, ...points.map((p) => p.likes)), [points])
  const baseXMax = useMemo(() => niceUpper(xMax, X_TICKS), [xMax])
  const baseYMax = useMemo(() => niceUpper(yMax, Y_TICKS), [yMax])
  const xZoomOutMax = useMemo(() => Math.max(baseXMax, baseXMax * 8), [baseXMax])
  const yZoomOutMax = useMemo(() => Math.max(baseYMax, baseYMax * 8), [baseYMax])
  const xZoomOutMin = useMemo(() => -Math.max(baseXMax, baseXMax * 2), [baseXMax])
  const yZoomOutMin = useMemo(() => -Math.max(baseYMax, baseYMax * 2), [baseYMax])
  const [xDomain, setXDomain] = useState<[number, number]>([0, baseXMax])
  const [yDomain, setYDomain] = useState<[number, number]>([0, baseYMax])

  useEffect(() => {
    setXDomain([0, baseXMax])
    setYDomain([0, baseYMax])
  }, [baseXMax, baseYMax])

  const innerWidth = WIDTH - MARGIN.left - MARGIN.right
  const innerHeight = HEIGHT - MARGIN.top - MARGIN.bottom

  const xScale = (value: number) =>
    MARGIN.left + ((value - xDomain[0]) / Math.max(1, xDomain[1] - xDomain[0])) * innerWidth
  const yScale = (value: number) =>
    HEIGHT - MARGIN.bottom - ((value - yDomain[0]) / Math.max(1, yDomain[1] - yDomain[0])) * innerHeight

  const handleWheelZoom = (event: WheelEvent) => {
    const svg = svgRef.current
    if (!svg) return
    const rect = svg.getBoundingClientRect()
    const svgX = ((event.clientX - rect.left) / rect.width) * WIDTH
    const svgY = ((event.clientY - rect.top) / rect.height) * HEIGHT
    if (
      svgX < MARGIN.left ||
      svgX > WIDTH - MARGIN.right ||
      svgY < MARGIN.top ||
      svgY > HEIGHT - MARGIN.bottom
    ) {
      return
    }
    event.preventDefault()

    const zoomFactor = event.deltaY > 0 ? 1.1 : 0.9
    const currentXSpan = xDomain[1] - xDomain[0]
    const currentYSpan = yDomain[1] - yDomain[0]
    const nextXSpan = Math.min(xZoomOutMax, Math.max(baseXMax * 0.02, currentXSpan * zoomFactor))
    const nextYSpan = Math.min(yZoomOutMax, Math.max(baseYMax * 0.02, currentYSpan * zoomFactor))

    const xPct = (svgX - MARGIN.left) / innerWidth
    const yPct = 1 - (svgY - MARGIN.top) / innerHeight
    const xAnchor = xDomain[0] + xPct * currentXSpan
    const yAnchor = yDomain[0] + yPct * currentYSpan

    let nextXMin = xAnchor - xPct * nextXSpan
    let nextXMax = nextXMin + nextXSpan
    if (nextXMin < xZoomOutMin) {
      nextXMin = xZoomOutMin
      nextXMax = xZoomOutMin + nextXSpan
    }
    if (nextXMax > xZoomOutMax) {
      nextXMax = xZoomOutMax
      nextXMin = xZoomOutMax - nextXSpan
    }

    let nextYMin = yAnchor - yPct * nextYSpan
    let nextYMax = nextYMin + nextYSpan
    if (nextYMin < yZoomOutMin) {
      nextYMin = yZoomOutMin
      nextYMax = yZoomOutMin + nextYSpan
    }
    if (nextYMax > yZoomOutMax) {
      nextYMax = yZoomOutMax
      nextYMin = yZoomOutMax - nextYSpan
    }

    setXDomain([nextXMin, nextXMax])
    setYDomain([nextYMin, nextYMax])
  }

  const handleMouseDown = (event: MouseEvent<SVGSVGElement>) => {
    if (event.button !== 0) return
    const rect = event.currentTarget.getBoundingClientRect()
    const svgX = ((event.clientX - rect.left) / rect.width) * WIDTH
    const svgY = ((event.clientY - rect.top) / rect.height) * HEIGHT
    if (
      svgX < MARGIN.left ||
      svgX > WIDTH - MARGIN.right ||
      svgY < MARGIN.top ||
      svgY > HEIGHT - MARGIN.bottom
    ) {
      return
    }
    dragStartRef.current = {
      x: svgX,
      y: svgY,
      xDomain: [...xDomain] as [number, number],
      yDomain: [...yDomain] as [number, number],
    }
    setIsDragging(true)
  }

  const handleMouseMove = (event: MouseEvent<SVGSVGElement>) => {
    if (!dragStartRef.current || !isDragging) return
    const rect = event.currentTarget.getBoundingClientRect()
    const svgX = ((event.clientX - rect.left) / rect.width) * WIDTH
    const svgY = ((event.clientY - rect.top) / rect.height) * HEIGHT

    const dx = svgX - dragStartRef.current.x
    const dy = svgY - dragStartRef.current.y

    const xSpan = dragStartRef.current.xDomain[1] - dragStartRef.current.xDomain[0]
    const ySpan = dragStartRef.current.yDomain[1] - dragStartRef.current.yDomain[0]
    const xDeltaValue = (dx / innerWidth) * xSpan
    const yDeltaValue = (dy / innerHeight) * ySpan

    let nextXMin = dragStartRef.current.xDomain[0] - xDeltaValue
    let nextXMax = dragStartRef.current.xDomain[1] - xDeltaValue
    if (nextXMin < xZoomOutMin) {
      nextXMin = xZoomOutMin
      nextXMax = xZoomOutMin + xSpan
    }
    if (nextXMax > xZoomOutMax) {
      nextXMax = xZoomOutMax
      nextXMin = xZoomOutMax - xSpan
    }

    let nextYMin = dragStartRef.current.yDomain[0] + yDeltaValue
    let nextYMax = dragStartRef.current.yDomain[1] + yDeltaValue
    if (nextYMin < yZoomOutMin) {
      nextYMin = yZoomOutMin
      nextYMax = yZoomOutMin + ySpan
    }
    if (nextYMax > yZoomOutMax) {
      nextYMax = yZoomOutMax
      nextYMin = yZoomOutMax - ySpan
    }

    setXDomain([nextXMin, nextXMax])
    setYDomain([nextYMin, nextYMax])
  }

  const stopDragging = () => {
    dragStartRef.current = null
    setIsDragging(false)
  }

  useEffect(() => {
    const svg = svgRef.current
    if (!svg) return
    const listener = (event: WheelEvent) => handleWheelZoom(event)
    svg.addEventListener('wheel', listener, { passive: false })
    return () => svg.removeEventListener('wheel', listener)
  }, [xDomain, yDomain, baseXMax, baseYMax, xZoomOutMax, yZoomOutMax, xZoomOutMin, yZoomOutMin])

  if (!points.length) {
    return (
      <section className="scatter-wrap">
        <div className="scatter-header">
          <h3>Graph: Streams vs Likes</h3>
          <div className="metric-meta">Run a search to populate points.</div>
        </div>
      </section>
    )
  }

  return (
    <section className="scatter-wrap">
      <div className="scatter-header">
        <h3>Graph: Streams vs Likes</h3>
        <div className="scatter-controls">
          <div className="metric-meta">Scroll to zoom. Click a point to open track details.</div>
          <button
            className="btn-action"
            type="button"
            onClick={() => {
              setXDomain([0, baseXMax])
              setYDomain([0, baseYMax])
            }}
          >
            Reset Zoom
          </button>
        </div>
      </div>
      <svg
        ref={svgRef}
        className={`scatter-svg ${isDragging ? 'dragging' : ''}`}
        viewBox={`0 0 ${WIDTH} ${HEIGHT}`}
        role="img"
        aria-label="Scatter plot of streams vs likes"
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={stopDragging}
        onMouseLeave={stopDragging}
      >
        {Array.from({ length: Y_TICKS + 1 }).map((_, i) => {
          const value = yDomain[0] + ((yDomain[1] - yDomain[0]) / Y_TICKS) * i
          const y = yScale(value)
          return (
            <g key={`y-${i}`}>
              <line x1={MARGIN.left} y1={y} x2={WIDTH - MARGIN.right} y2={y} className="scatter-gridline" />
              <text x={MARGIN.left - 8} y={y + 4} className="scatter-label scatter-label-left">
                {formatLikesAxis(value)}
              </text>
            </g>
          )
        })}

        {Array.from({ length: X_TICKS + 1 }).map((_, i) => {
          const value = xDomain[0] + ((xDomain[1] - xDomain[0]) / X_TICKS) * i
          const x = xScale(value)
          return (
            <g key={`x-${i}`}>
              <line x1={x} y1={MARGIN.top} x2={x} y2={HEIGHT - MARGIN.bottom} className="scatter-gridline" />
              <text x={x} y={HEIGHT - MARGIN.bottom + 18} className="scatter-label scatter-label-bottom">
                {formatPlaysAxis(value)}
              </text>
            </g>
          )
        })}

        {yDomain[0] <= 0 && yDomain[1] >= 0 && (
          <g>
            <line
              x1={MARGIN.left}
              y1={yScale(0)}
              x2={WIDTH - MARGIN.right}
              y2={yScale(0)}
              className="scatter-zero-line"
            />
            <text x={MARGIN.left - 8} y={yScale(0) - 4} className="scatter-label scatter-label-left">
              0
            </text>
          </g>
        )}

        <text x={WIDTH / 2} y={HEIGHT - 10} className="scatter-axis-title">
          plays
        </text>
        <text x={18} y={HEIGHT / 2} transform={`rotate(-90 18 ${HEIGHT / 2})`} className="scatter-axis-title">
          likes
        </text>

        {points.map((row) => {
          const selected = row.track_id === selectedTrackId
          return (
            <circle
              key={row.track_id}
              cx={xScale(row.plays)}
              cy={yScale(row.likes)}
              r={selected ? 6 : 4}
              className={`scatter-point ${selected ? 'selected' : ''}`}
              onClick={() => onSelectTrack(row)}
            >
              <title>{`${row.title} | ${compact(row.plays)} plays | ${compact(row.likes)} likes`}</title>
            </circle>
          )
        })}
      </svg>
    </section>
  )
}
