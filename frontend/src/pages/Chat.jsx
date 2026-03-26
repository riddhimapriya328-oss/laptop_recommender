import { useState, useEffect, useRef } from 'react'
import { useNavigate }                  from 'react-router-dom'
import s                                from '../styles/Chat.module.css'
import SearchBar                        from '../components/SearchBar.jsx'
import CategoryBubbles                  from '../components/CategoryBubbles.jsx'
import ChatMessage, { TypingIndicator } from '../components/ChatMessage.jsx'
import {
  analyzeQuery,
  getRecommendations,
  getExplanations,
  fetchHistory,
  saveHistory,
} from '../lib/api.js'

function fmtDate(iso) {
  const d = new Date(iso)
  return d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })
}

export default function Chat() {
  const navigate    = useNavigate()
  const bottomRef   = useRef(null)
  const [query, setQuery]         = useState('')
  const [messages, setMessages]   = useState([])
  const [loading, setLoading]     = useState(false)
  const [history, setHistory]     = useState([])
  const userEmail = localStorage.getItem('user_email') || ''

  // Load history and pick up any pending query from landing page
  useEffect(() => {
    fetchHistory()
      .then((d) => setHistory(d.history || []))
      .catch(() => {})

    const pending = sessionStorage.getItem('pending_query')
    if (pending) {
      sessionStorage.removeItem('pending_query')
      handleSend(pending)
    }
  }, []) // eslint-disable-line

  // Scroll to bottom on new message
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  function addMessage(msg) {
    setMessages((prev) => [...prev, msg])
  }

  async function handleSend(q) {
    if (!q.trim() || loading) return
    setQuery('')
    addMessage({ role: 'user', text: q })
    setLoading(true)

    try {
      // Agent 1 — parse query
      const intent = await analyzeQuery(q)

      // Agent 2 — score & rank
      const { recommendations } = await getRecommendations(intent)

      if (!recommendations || recommendations.length === 0) {
        addMessage({
          role: 'ai',
          text: "I couldn't find laptops matching your criteria. Try adjusting your budget or requirements.",
        })
        setLoading(false)
        return
      }

      // Agent 3 — explain
      const { explanations, why_not } = await getExplanations(
        recommendations,
        q,
        intent
      )

      addMessage({
        role: 'ai',
        text: `Here are the top ${recommendations.length} laptop${recommendations.length > 1 ? 's' : ''} for you:`,
        laptops: recommendations,
        explanations,
        whyNot: why_not,
      })

      // Persist to Supabase
      saveHistory(q, intent, recommendations).catch(() => {})

      // Refresh sidebar history
      fetchHistory()
        .then((d) => setHistory(d.history || []))
        .catch(() => {})
    } catch (err) {
      addMessage({
        role: 'ai',
        text: 'Something went wrong. Please check your connection and try again.',
      })
    } finally {
      setLoading(false)
    }
  }

  function handleBubble(q) {
    setQuery(q)
    handleSend(q)
  }

  function handleNewChat() {
    setMessages([])
    setQuery('')
  }

  function handleSignOut() {
    localStorage.removeItem('access_token')
    localStorage.removeItem('user_email')
    navigate('/')
  }

  const initials = userEmail.slice(0, 2).toUpperCase() || 'U'

  return (
    <div className={s.page}>
      {/* Top nav */}
      <nav className={s.nav}>
        <span className={s.logo} onClick={() => navigate('/')}>
          LaptopMatch
        </span>
        <div className={s.navRight}>
          <button className={s.newChatBtn} onClick={handleNewChat}>
            + New chat
          </button>
          <div
            className={s.userAvatar}
            title={userEmail}
            onClick={handleSignOut}
          >
            {initials}
          </div>
        </div>
      </nav>

      <div className={s.body}>
        {/* Sidebar */}
        <aside className={s.sidebar}>
          <div className={s.sideSection}>
            <p className={s.sideLabel}>Recent searches</p>
            {history.length === 0 ? (
              <p className={s.emptyHistory}>
                Your past searches will appear here
              </p>
            ) : (
              history.map((item) => (
                <div
                  key={item.id}
                  className={s.historyItem}
                  onClick={() => handleSend(item.query_text)}
                >
                  <p className={s.historyText}>{item.query_text}</p>
                  <p className={s.historyDate}>{fmtDate(item.created_at)}</p>
                </div>
              ))
            )}
          </div>

          <div className={s.sideSection}>
            <p className={s.sideLabel}>Quick filters</p>
            <CategoryBubbles onSelect={handleBubble} small />
          </div>
        </aside>

        {/* Main area */}
        <main className={s.main}>
          {messages.length === 0 && !loading ? (
            /* Empty state */
            <div className={s.emptyState}>
              <h2 className={s.emptyHeading}>Let's start recommending</h2>
              <p className={s.emptySubtext}>
                Describe what you're looking for below.
              </p>
              <CategoryBubbles onSelect={handleBubble} />
            </div>
          ) : (
            /* Message thread */
            <div className={s.messages}>
              {messages.map((msg, i) => (
                <ChatMessage key={i} message={msg} />
              ))}
              {loading && <TypingIndicator />}
              <div ref={bottomRef} />
            </div>
          )}

          {/* Input bar */}
          <div className={s.inputBar}>
            <SearchBar
              value={query}
              onChange={setQuery}
              onSubmit={handleSend}
              placeholder="Ask a follow-up or start a new search…"
            />
          </div>
        </main>
      </div>
    </div>
  )
}
