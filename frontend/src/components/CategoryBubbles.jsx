import { useState } from 'react'

const BUBBLES = [
  { label: 'Price',        query: 'Show me the most affordable laptops under ₹50,000' },
  { label: 'RAM',          query: 'I need a laptop with at least 16GB RAM' },
  { label: 'Gaming',       query: 'Best gaming laptop under ₹80,000' },
  { label: 'Lightweight',  query: 'Lightest laptop under 1.5kg for travel' },
  { label: 'Battery life', query: 'Laptop with the longest battery life' },
  { label: 'Editing',      query: 'Video editing laptop with good GPU and display' },
  { label: 'Small size',   query: 'Compact laptop under 13 inches for portability' },
  { label: 'Student',      query: 'Best student laptop under ₹40,000' },
]

const baseStyle = {
  fontSize: '12px',
  padding: '7px 18px',
  background: 'var(--color-surface)',
  border: '1px solid var(--color-border)',
  borderRadius: '30px',
  color: 'var(--color-text-muted)',
  cursor: 'pointer',
  fontFamily: "'DM Sans', sans-serif",
  whiteSpace: 'nowrap',
  transition: 'background 0.15s, border-color 0.15s',
}

export default function CategoryBubbles({ onSelect, small }) {
  const [hovered, setHovered] = useState(null)

  return (
    <div
      style={{
        display: 'flex',
        flexWrap: 'wrap',
        gap: '8px',
        justifyContent: 'center',
        marginTop: '18px',
      }}
    >
      {BUBBLES.map((b) => (
        <button
          key={b.label}
          style={{
            ...baseStyle,
            fontSize: small ? '11px' : '12px',
            padding: small ? '5px 14px' : '7px 18px',
            background: hovered === b.label ? 'var(--color-surface-2)' : 'var(--color-surface)',
            borderColor:
              hovered === b.label
                ? 'rgba(44,44,42,0.28)'
                : 'rgba(44,44,42,0.14)',
          }}
          onMouseEnter={() => setHovered(b.label)}
          onMouseLeave={() => setHovered(null)}
          onClick={() => onSelect(b.query)}
        >
          {b.label}
        </button>
      ))}
    </div>
  )
}
