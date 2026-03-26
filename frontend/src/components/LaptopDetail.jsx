import s from '../styles/LaptopCard.module.css'
import ScoreBar from './ScoreBar.jsx'

function fmt(n) {
  if (!n && n !== 0) return '—'
  return `₹${Number(n).toLocaleString('en-IN')}`
}

function valueColor(score) {
  if (score >= 75) return 'var(--color-success)'
  if (score >= 50) return 'var(--color-warn)'
  return 'var(--color-text-muted)'
}

export default function LaptopDetail({ laptop, explanation, whyNot, onClose }) {
  if (!laptop) return null

  const vs = Math.round(laptop.value_score || 0)

  return (
    <div className={s.overlay} onClick={onClose}>
      <div className={s.panel} onClick={(e) => e.stopPropagation()}>
        <button className={s.panelClose} onClick={onClose} aria-label="Close">
          ✕
        </button>

        <div>
          <p className={s.panelName}>{laptop.name}</p>
          <div className={s.panelPriceRow}>
            <span className={s.panelBrand}>{laptop.brand}</span>
            <span className={s.panelPrice}>{fmt(laptop.price_inr)}</span>
          </div>
        </div>

        {/* Score bars */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          <ScoreBar label="Performance" value={laptop.performance_score} large />
          <ScoreBar label="Battery"     value={laptop.battery_score}     large />
          <ScoreBar label="Gaming"      value={laptop.gaming_score}       large />
        </div>

        {/* Full specs table */}
        <div>
          <p className={s.sectionLabel}>Full Specifications</p>
          <table className={s.specsTable}>
            <tbody>
              {[
                ['CPU',      laptop.cpu],
                ['GPU',      laptop.gpu || 'Integrated'],
                ['RAM',      laptop.ram_gb ? `${laptop.ram_gb} GB` : '—'],
                ['Storage',  laptop.storage_gb ? `${laptop.storage_gb} GB` : '—'],
                ['Battery',  laptop.battery_hrs ? `~${laptop.battery_hrs}h` : '—'],
                ['Weight',   laptop.weight_kg ? `${laptop.weight_kg} kg` : '—'],
                ['Display',  laptop.display_in ? `${laptop.display_in}" ${laptop.display_type || ''}` : '—'],
                ['OS',       laptop.os || '—'],
              ].map(([k, v]) => (
                <tr key={k}>
                  <td>{k}</td>
                  <td>{v}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Explanation */}
        {explanation && (
          <div>
            <p className={s.sectionLabel}>Why we picked this for you</p>
            <p className={s.explanationText}>{explanation}</p>
          </div>
        )}

        {/* Why not */}
        {whyNot && (
          <div>
            <p className={s.sectionLabel}>Why we skipped the others</p>
            <p className={s.whyNotText}>{whyNot}</p>
          </div>
        )}

        {/* Value score */}
        <div>
          <p className={s.sectionLabel}>Value for money</p>
          <div className={s.valueScoreLarge}>
            <span className={s.valueNum} style={{ color: valueColor(vs) }}>
              {vs}
            </span>
            <span className={s.valueDenom}>/ 100</span>
          </div>
        </div>

        {/* Action buttons */}
        <div className={s.panelButtons}>
          {laptop.source_url ? (
            <a
              href={laptop.source_url}
              target="_blank"
              rel="noreferrer"
              className={s.panelBtn}
              style={{ textDecoration: 'none' }}
            >
              View listing →
            </a>
          ) : (
            <a
              href={`https://www.flipkart.com/search?q=${encodeURIComponent(laptop.name)}`}
              target="_blank"
              rel="noreferrer"
              className={s.panelBtn}
              style={{ textDecoration: 'none' }}
            >
              View on Flipkart →
            </a>
          )}
          <button className={s.panelBtn}>Save to compare</button>
        </div>
      </div>
    </div>
  )
}
