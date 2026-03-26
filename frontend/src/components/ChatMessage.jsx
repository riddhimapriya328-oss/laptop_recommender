import LaptopCard from './LaptopCard.jsx'
import s from '../styles/LaptopCard.module.css'

const msgBase = {
  maxWidth: '78%',
  fontSize: '14px',
  lineHeight: '1.65',
  padding: '12px 18px',
}

const userStyle = {
  ...msgBase,
  alignSelf: 'flex-end',
  background: '#2c2c2a',
  color: '#f5f0e8',
  borderRadius: '18px 18px 4px 18px',
  maxWidth: '70%',
}

const aiStyle = {
  ...msgBase,
  alignSelf: 'flex-start',
  background: 'var(--color-surface)',
  border: '1px solid var(--color-border)',
  borderRadius: '4px 18px 18px 18px',
  display: 'flex',
  flexDirection: 'column',
  gap: '8px',
}

// Animated typing indicator
export function TypingIndicator() {
  return (
    <div style={{ ...aiStyle, padding: '14px 18px' }}>
      <div style={{ display: 'flex', gap: '5px', alignItems: 'center' }}>
        {[0, 1, 2].map((i) => (
          <span
            key={i}
            style={{
              width: '6px',
              height: '6px',
              borderRadius: '50%',
              background: 'var(--color-text-muted)',
              display: 'inline-block',
              animation: `pulse 1.2s ease-in-out ${i * 0.2}s infinite`,
            }}
          />
        ))}
      </div>
      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 0.3; }
          50%       { opacity: 1; }
        }
      `}</style>
    </div>
  )
}

export default function ChatMessage({ message }) {
  const { role, text, laptops, explanations, whyNot } = message

  if (role === 'user') {
    return <div style={userStyle}>{text}</div>
  }

  return (
    <div style={aiStyle}>
      {text && <p style={{ margin: 0 }}>{text}</p>}

      {laptops && laptops.length > 0 && (
        <div className={s.cardsRow}>
          {laptops.map((laptop, idx) => (
            <LaptopCard
              key={laptop.id || idx}
              laptop={laptop}
              isBest={idx === 0}
              explanation={explanations?.[laptop.id] || explanations?.[laptop.name]}
              whyNot={whyNot}
            />
          ))}
        </div>
      )}
    </div>
  )
}
