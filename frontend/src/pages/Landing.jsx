import { useState }        from 'react'
import { useNavigate }     from 'react-router-dom'
import s                   from '../styles/Landing.module.css'
import SearchBar           from '../components/SearchBar.jsx'
import CategoryBubbles     from '../components/CategoryBubbles.jsx'

export default function Landing() {
  const [query, setQuery] = useState('')
  const navigate           = useNavigate()

  function handleSubmit(q) {
    const token = localStorage.getItem('access_token')
    if (!token) {
      // Store the query so Chat can pick it up after login
      sessionStorage.setItem('pending_query', q)
      navigate('/signup')
    } else {
      sessionStorage.setItem('pending_query', q)
      navigate('/chat')
    }
  }

  function handleBubble(q) {
    setQuery(q)
    handleSubmit(q)
  }

  return (
    <div className={s.page}>
      {/* Nav */}
      <nav className={s.nav}>
        <span className={s.logo}>LaptopMatch</span>
        <div className={s.navRight}>
          <button className={s.navLink} onClick={() => navigate('/login')}>
            Sign in
          </button>
          <button className={s.navCta} onClick={() => navigate('/signup')}>
            Get started
          </button>
        </div>
      </nav>

      {/* Hero */}
      <main className={s.hero}>
        <p className={s.eyebrow}>AI-Powered Recommendation</p>
        <h1 className={s.heading}>Find the laptop that's right for you</h1>
        <p className={s.subtitle}>
          Tell us what you need. We'll match you with the best options — with
          plain explanations, not just spec sheets.
        </p>

        {/* Search section */}
        <div className={s.searchSection}>
          <p className={s.startLabel}>Let's start recommending</p>
          <SearchBar
            value={query}
            onChange={setQuery}
            onSubmit={handleSubmit}
          />
          <CategoryBubbles onSelect={handleBubble} />
        </div>
      </main>

      {/* How it works */}
      <section className={s.howSection}>
        <h2 className={s.howTitle}>How it works</h2>
        <div className={s.steps}>
          <div className={s.stepItem}>
            <div className={s.stepNum}>1</div>
            <p className={s.stepText}>
              Describe your needs or pick a category above
            </p>
          </div>
          <div className={s.stepConnector} />
          <div className={s.stepItem}>
            <div className={s.stepNum}>2</div>
            <p className={s.stepText}>
              Our AI scores every laptop against your priorities
            </p>
          </div>
          <div className={s.stepConnector} />
          <div className={s.stepItem}>
            <div className={s.stepNum}>3</div>
            <p className={s.stepText}>
              Get your top picks with clear, human explanations
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className={s.footer}>
        <p className={s.footerText}>
          LaptopMatch · AI-powered laptop recommendations · Built for Hackathon 2025
        </p>
      </footer>
    </div>
  )
}
