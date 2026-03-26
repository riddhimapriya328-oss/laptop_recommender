import { useRef } from 'react'

const styles = {
  wrapper: {
    display: 'flex',
    alignItems: 'center',
    background: '#fff',
    border: '1px solid rgba(44,44,42,0.14)',
    borderRadius: '60px',
    padding: '8px 8px 8px 22px',
    width: '100%',
    maxWidth: '560px',
    gap: '8px',
  },
  input: {
    flex: 1,
    border: 'none',
    outline: 'none',
    background: 'transparent',
    fontSize: '14px',
    color: '#2c2c2a',
    fontFamily: "'DM Sans', sans-serif",
  },
  btn: {
    width: '38px',
    height: '38px',
    borderRadius: '50%',
    background: '#2c2c2a',
    border: 'none',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    flexShrink: 0,
    transition: 'opacity 0.15s',
  },
}

export default function SearchBar({ value, onChange, onSubmit, placeholder }) {
  const inputRef = useRef(null)

  function handleKey(e) {
    if (e.key === 'Enter' && value.trim()) onSubmit(value.trim())
  }

  return (
    <div style={styles.wrapper} onClick={() => inputRef.current?.focus()}>
      <input
        ref={inputRef}
        style={styles.input}
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={handleKey}
        placeholder={placeholder || 'e.g. coding laptop under ₹70,000 with good battery...'}
      />
      <button
        style={styles.btn}
        onClick={() => value.trim() && onSubmit(value.trim())}
        aria-label="Search"
      >
        <svg width="14" height="14" viewBox="0 0 24 24" fill="#f5f0e8">
          <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
        </svg>
      </button>
    </div>
  )
}
