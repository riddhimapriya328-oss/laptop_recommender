import { useState } from 'react'
import s from '../styles/LaptopCard.module.css'
import ScoreBar    from './ScoreBar.jsx'
import LaptopDetail from './LaptopDetail.jsx'

function fmt(n) {
  if (!n && n !== 0) return '—'
  return `₹${Number(n).toLocaleString('en-IN')}`
}

export default function LaptopCard({ laptop, isBest, explanation, whyNot }) {
  const [open, setOpen] = useState(false)

  const chips = [
    laptop.cpu        && laptop.cpu.split(' ').slice(0, 3).join(' '),
    laptop.ram_gb     && `${laptop.ram_gb}GB RAM`,
    laptop.gpu        && laptop.gpu !== 'Integrated' && laptop.gpu.split(' ').slice(0, 2).join(' '),
    laptop.storage_gb && `${laptop.storage_gb}GB`,
  ].filter(Boolean)

  const vs = Math.round(laptop.value_score || 0)

  return (
    <>
      <div className={s.card}>
        {/* Header */}
        <div className={s.cardHeader}>
          <div className={s.cardTitles}>
            <p className={s.laptopName}>{laptop.name}</p>
            <p className={s.laptopBrand}>{laptop.brand}</p>
          </div>
          {isBest && <span className={s.bestBadge}>Best pick</span>}
        </div>

        {/* Price */}
        <p className={s.price}>{fmt(laptop.price_inr)}</p>

        {/* Scores */}
        <div className={s.scores}>
          <ScoreBar label="Performance" value={laptop.performance_score} />
          <ScoreBar label="Battery"     value={laptop.battery_score} />
          <ScoreBar label="Gaming"      value={laptop.gaming_score} />
        </div>

        {/* Spec chips */}
        <div className={s.chips}>
          {chips.map((c) => (
            <span key={c} className={s.chip}>{c}</span>
          ))}
        </div>

        {/* Value score */}
        <p className={s.valueScore}>Value score: {vs} / 100</p>

        {/* Explanation excerpt */}
        {explanation && (
          <p className={s.excerpt}>{explanation}</p>
        )}

        {/* Detail link */}
        <button className={s.detailLink} onClick={() => setOpen(true)}>
          See full details →
        </button>
      </div>

      {open && (
        <LaptopDetail
          laptop={laptop}
          explanation={explanation}
          whyNot={whyNot}
          onClose={() => setOpen(false)}
        />
      )}
    </>
  )
}
