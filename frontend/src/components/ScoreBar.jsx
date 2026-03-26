import s from '../styles/LaptopCard.module.css'

export default function ScoreBar({ label, value, large }) {
  const pct = Math.round(Math.min(100, Math.max(0, value || 0)))

  return (
    <div className={s.scoreBarWrapper}>
      <span className={s.scoreLabel}>{label}</span>
      <div
        className={s.scoreTrack}
        style={{ height: large ? '6px' : '4px' }}
      >
        <div className={s.scoreFill} style={{ width: `${pct}%` }} />
      </div>
      <span className={s.scorePct}>{pct}%</span>
    </div>
  )
}
