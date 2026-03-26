import { useState }     from 'react'
import { useNavigate }  from 'react-router-dom'
import s                from '../styles/Auth.module.css'
import { signupUser }   from '../lib/api.js'

export default function Signup() {
  const navigate = useNavigate()
  const [form, setForm]   = useState({ fullName: '', email: '', password: '', confirm: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  function update(field) {
    return (e) => setForm((prev) => ({ ...prev, [field]: e.target.value }))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    if (form.password !== form.confirm) {
      setError('Passwords do not match.')
      return
    }
    if (form.password.length < 6) {
      setError('Password must be at least 6 characters.')
      return
    }
    setLoading(true)
    try {
      const data = await signupUser(form.email, form.password, form.fullName)
      localStorage.setItem('access_token', data.access_token)
      localStorage.setItem('user_email', form.email)
      navigate('/chat')
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not create account. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className={s.page}>
      <div className={s.logoTop} onClick={() => navigate('/')}>
        LaptopMatch
      </div>

      <div className={s.card}>
        <h2 className={s.heading}>Create your account</h2>
        <p className={s.subtext}>
          Find your perfect laptop in seconds.
        </p>

        <form className={s.form} onSubmit={handleSubmit}>
          {error && <p className={s.error}>{error}</p>}

          <input
            className={s.inputField}
            type="text"
            placeholder="Full name"
            value={form.fullName}
            onChange={update('fullName')}
            required
          />
          <input
            className={s.inputField}
            type="email"
            placeholder="Email address"
            value={form.email}
            onChange={update('email')}
            required
            autoComplete="email"
          />
          <input
            className={s.inputField}
            type="password"
            placeholder="Password"
            value={form.password}
            onChange={update('password')}
            required
            autoComplete="new-password"
          />
          <input
            className={s.inputField}
            type="password"
            placeholder="Confirm password"
            value={form.confirm}
            onChange={update('confirm')}
            required
          />

          <button className={s.submitBtn} type="submit" disabled={loading}>
            {loading ? 'Creating account…' : 'Create account'}
          </button>
        </form>

        <div className={s.benefits}>
          {[
            'Save and revisit your recommendation history',
            'Compare up to 3 laptops side-by-side',
            'Get personalized picks every time',
          ].map((b) => (
            <div key={b} className={s.benefitItem}>
              <span className={s.checkmark}>✓</span>
              <span>{b}</span>
            </div>
          ))}
        </div>

        <p className={s.footerLink}>
          Already have an account?{' '}
          <button onClick={() => navigate('/login')}>Sign in →</button>
        </p>
      </div>
    </div>
  )
}
