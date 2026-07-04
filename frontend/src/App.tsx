import { useState, useEffect, useRef } from 'react'
import './index.css'

type Message = { role: 'agent' | 'user', text: string, options?: string[] }

const ONBOARDING_STEPS = [
  { 
    field: 'name', 
    question: "Welcome! I'm Yono Agent. To get started, what should I call you?",
    options: ["Ramesh Kumar", "Neha Sharma", "Amit Patel"]
  },
  { 
    field: 'age', 
    question: "It's lovely to meet you. Which stage of life are you currently in?",
    options: ["18 - 25", "26 - 35", "36 - 50", "50+"]
  },
  { 
    field: 'profession', 
    question: "Got it. And what do you do for a living?",
    options: ["Student", "Salaried Professional", "Business Owner", "Retired"]
  },
  { 
    field: 'income', 
    question: "Thank you for sharing. Roughly, what is your annual income? This helps me suggest the perfect options.",
    options: ["Below 3 Lakhs", "3 - 8 Lakhs", "8 - 15 Lakhs", "15+ Lakhs"]
  },
  { 
    field: 'goals', 
    question: "Almost done. What is your biggest financial goal right now?",
    options: ["Save for Education", "Buy a Home/Car", "Grow My Wealth", "Secure My Retirement"]
  }
]

function App() {
  const [theme, setTheme] = useState<'light' | 'dark'>('light')
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [username, setUsername] = useState('demo_user_123')
  const [password, setPassword] = useState('password123')
  
  const [activeTab, setActiveTab] = useState('chat')
  const [isApplying, setIsApplying] = useState(false)
  const [applyProduct, setApplyProduct] = useState('')

  const [messages, setMessages] = useState<Message[]>([])
  const [inputValue, setInputValue] = useState('')
  const chatEndRef = useRef<HTMLDivElement>(null)
  
  const [step, setStep] = useState(0)
  const [userData, setUserData] = useState<any>({})
  const [isOnboardingComplete, setIsOnboardingComplete] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  
  const [recommendations, setRecommendations] = useState<string[]>([])
  const [healthData, setHealthData] = useState<any>(null)
  const [goals, setGoals] = useState<any[]>([])

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
  }, [theme])

  const toggleTheme = () => setTheme(prev => prev === 'light' ? 'dark' : 'light')

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoggedIn(true)
    setMessages([
      { role: 'agent', text: ONBOARDING_STEPS[0].question, options: ONBOARDING_STEPS[0].options }
    ])
  }

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleInputSubmit = async (text: string) => {
    if (!text.trim() || isProcessing) return
    setIsProcessing(true)

    setMessages(prev => {
      const newMsgs = [...prev]
      if (newMsgs.length > 0 && newMsgs[newMsgs.length - 1].role === 'agent') {
        delete newMsgs[newMsgs.length - 1].options
      }
      return [...newMsgs, { role: 'user', text }]
    })
    setInputValue('')

    // ONBOARDING MODE
    if (!isOnboardingComplete) {
      const currentStepObj = ONBOARDING_STEPS[step]
      const newData = { ...userData, [currentStepObj.field]: text }
      setUserData(newData)

      const nextStep = step + 1
      if (nextStep < ONBOARDING_STEPS.length) {
        setTimeout(() => {
          setStep(nextStep)
          setMessages(prev => [...prev, { 
            role: 'agent', 
            text: ONBOARDING_STEPS[nextStep].question, 
            options: ONBOARDING_STEPS[nextStep].options 
          }])
          setIsProcessing(false)
        }, 600)
      } else {
        setIsOnboardingComplete(true)
        setTimeout(() => {
          setMessages(prev => [...prev, { 
            role: 'agent', 
            text: `Thank you, ${newData.name?.split(' ')[0] || 'there'}! I've securely saved your profile.\n\nBased on what you shared, I'm pulling together some thoughtful suggestions now. How else can I support your journey today?` 
          }])
          fetchAIResponse([{role: 'user', text: "Generate initial recommendations based on my profile."}], newData)
        }, 1000)
      }
    } 
    // POST-ONBOARDING MODE
    else {
      const newHistory = [...messages, { role: 'user', text }] as Message[]
      await fetchAIResponse(newHistory, userData)
    }
  }

  const fetchAIResponse = async (history: Message[], currentData: any) => {
    try {
      const res = await fetch(`/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages: history, user_data: currentData })
      })
      const data = await res.json()
      
      setMessages(prev => [...prev, { role: 'agent', text: data.reply }])
      
      if (data.salary_update) {
        setUserData((prev: any) => ({ ...prev, monthly_salary: data.salary_update }))
      }
      if (data.recommendations && data.recommendations.length > 0) setRecommendations(data.recommendations)
      if (data.health_update) setHealthData(data.health_update)
      if (data.goal_update) setGoals(prev => [data.goal_update, ...prev.filter(g => g.name !== data.goal_update.name)])
      
      setIsProcessing(false)
    } catch(e) {
      setMessages(prev => [...prev, { role: 'agent', text: "I'm having a little trouble connecting right now. Please try again in a moment." }])
      setIsProcessing(false)
    }
  }

  const handleApplyClick = (productName: string) => {
    setApplyProduct(productName)
    setIsApplying(true)
  }

  if (!isLoggedIn) {
    return (
      <div className="login-wrapper">
        <div className="login-card">
          <div className="login-header">
            <h2>Welcome to SBI</h2>
            <p>Your journey to financial peace of mind starts here.</p>
          </div>
          <form onSubmit={handleLogin}>
            <div className="form-group">
              <label>Your User ID</label>
              <input type="text" value={username} onChange={e => setUsername(e.target.value)} required />
            </div>
            <div className="form-group">
              <label>Your Password</label>
              <input type="password" value={password} onChange={e => setPassword(e.target.value)} required />
            </div>
            <button type="submit" className="btn-primary">Login Securely</button>
          </form>
        </div>
      </div>
    )
  }

  return (
    <div className="dashboard-wrapper">
      <div className="app-container">
        
        {/* Application Modal */}
        {isApplying && (
          <div className="modal-overlay">
            <div className="modal-content fade-in">
              <h2>Set up your {applyProduct}</h2>
              <div className="modal-body">
                <div className="form-group">
                  <label>Applicant Name</label>
                  <input type="text" value={userData.name || ''} readOnly className="readonly-input" />
                </div>
                <div className="form-group">
                  <label>Funding Account</label>
                  <input type="text" value="SBI Savings ending in 4022" readOnly className="readonly-input" />
                </div>
                <p className="modal-info">We'll use your verified profile details to handle the paperwork for you seamlessly.</p>
              </div>
              <div className="modal-actions">
                <button className="btn-secondary" onClick={() => setIsApplying(false)}>Cancel</button>
                <button className="btn-primary" onClick={() => {
                  alert("You're all set! We'll process this shortly.")
                  setIsApplying(false)
                }}>Confirm Details</button>
              </div>
            </div>
          </div>
        )}

        {/* Sidebar */}
        <aside className="sidebar">
          <div className="sidebar-brand">SBI YONO</div>
          <nav className="sidebar-nav">
            <button className={activeTab === 'chat' ? 'active' : ''} onClick={() => setActiveTab('chat')}>Yono Agent</button>
            {isOnboardingComplete && (
              <>
                <button className={activeTab === 'loans' ? 'active' : ''} onClick={() => setActiveTab('loans')}>Life Goals</button>
                <button className={activeTab === 'plans' ? 'active' : ''} onClick={() => setActiveTab('plans')}>Future Planning</button>
                <button className={activeTab === 'accounts' ? 'active' : ''} onClick={() => setActiveTab('accounts')}>Connected Accounts</button>
              </>
            )}
          </nav>
          <div className="sidebar-footer">
            <button className="btn-secondary" onClick={toggleTheme}>{theme === 'light' ? 'Dark Mode' : 'Light Mode'}</button>
            <button className="btn-logout" onClick={() => window.location.reload()}>Sign Out</button>
          </div>
        </aside>

        <main className="dash-content">
          {/* Main Chat Interface */}
          {activeTab === 'chat' && (
            <div className="chat-layout">
              <div className="chat-section">
                <div className="chat-header">
                  <div className="agent-avatar-bg">AI</div>
                  <div>
                    <h3>Yono Agent</h3>
                    {isOnboardingComplete && <p className="agent-status">Online and ready to assist</p>}
                  </div>
                </div>
                <div className="chat-history">
                  {messages.map((m, i) => (
                    <div key={i} className={`message-bubble ${m.role}`}>
                      <div className="bubble-content">{m.text}</div>
                      {m.options && (
                        <div className="quick-options">
                          {m.options.map(opt => (
                            <button key={opt} onClick={() => handleInputSubmit(opt)} className="btn-quick-opt" disabled={isProcessing}>
                              {opt}
                            </button>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                  {isProcessing && <div className="message-bubble agent fade-in"><div className="bubble-content" style={{opacity: 0.7}}>Thinking...</div></div>}
                  <div ref={chatEndRef} />
                </div>
                <form className="chat-input" onSubmit={e => { e.preventDefault(); handleInputSubmit(inputValue) }}>
                  <input 
                    type="text" 
                    placeholder={isOnboardingComplete ? "Share an update or ask a question..." : "Type your answer..."} 
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    disabled={isProcessing}
                  />
                  <button type="submit" className="btn-primary" disabled={isProcessing}>Send</button>
                </form>
              </div>
              
              {/* Dynamic Info Panel (Right Side) */}
              {isOnboardingComplete && (
                <div className="info-section fade-in">
                  
                  {/* Financial Health Coach Card */}
                  {healthData && (
                    <div className="health-card fade-in">
                      <h4 style={{margin: '0 0 0.5rem 0', color: 'var(--text-main)'}}>Financial Health Coach</h4>
                      <div className="health-score">{healthData.score}<small style={{fontSize:'1rem', color:'var(--text-muted)'}}>/100</small></div>
                      <p style={{margin: '0.5rem 0', fontSize: '0.9rem', fontWeight: 700}}>Savings Rate: {healthData.savings_rate}</p>
                      <div className="health-tip">{healthData.tip}</div>
                    </div>
                  )}

                  {/* Active Goal Planners */}
                  {goals.map((g, i) => (
                    <div key={i} className="goal-card fade-in">
                      <h4 style={{margin: '0 0 0.5rem 0'}}>Goal: {g.name}</h4>
                      {g.target_amount && (
                        <p style={{margin: '0 0 0.25rem 0', fontSize: '0.9rem'}}>
                          Target: ₹{g.target_amount.toLocaleString('en-IN')}
                        </p>
                      )}
                      {g.status === 'awaiting_salary' ? (
                        <p style={{margin: '0', color: 'var(--text-muted)', fontSize: '0.9rem'}}>
                          Waiting for your monthly salary to build a savings plan...
                        </p>
                      ) : g.plans ? (
                        <>
                          <p style={{margin: '0 0 0.75rem 0', fontSize: '0.85rem', color: 'var(--text-muted)'}}>
                            Three savings options for you:
                          </p>
                          {g.plans.map((plan: any, j: number) => (
                            <div key={j} className="plan-option">
                              <strong>{plan.title}</strong>
                              <span>₹{plan.monthly_savings.toLocaleString('en-IN')}/mo · {plan.months} months · by {plan.target_date}</span>
                            </div>
                          ))}
                        </>
                      ) : (
                        <>
                          <p style={{margin: '0 0 0.25rem 0'}}>Timeline: {g.months} months</p>
                          <p style={{margin: '0', fontWeight: 700}}>₹{g.monthly_savings?.toLocaleString('en-IN')} / month required</p>
                        </>
                      )}
                      {g.status === 'active' && (
                        <div className="progress-bar-bg" style={{marginTop: '0.75rem'}}>
                          <div className="progress-bar-fill" style={{width: `${g.progress || 0}%`}}></div>
                        </div>
                      )}
                    </div>
                  ))}

                  <h3>Curated for you</h3>
                  <div className="recs-list">
                    {recommendations.length > 0 ? recommendations.map((rec, i) => (
                      <div className="product-card" key={i}>
                        <div><h4>{rec}</h4></div>
                        <button className="btn-apply" onClick={() => handleApplyClick(rec)}>Review Option</button>
                      </div>
                    )) : (
                      <p style={{color: 'var(--text-muted)'}}>Gathering the best options...</p>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Static Tabs */}
          {activeTab === 'loans' && (
            <div className="tab-view fade-in">
              <h2>Achieve your life goals</h2>
              <div className="grid-cards">
                {['SBI Auto Loan', 'Education Support', 'Dream Home Loan', 'Personal Support'].map(loan => (
                  <div key={loan} className="product-card">
                    <div><h3>{loan}</h3><p>Transparent terms and guidance through the entire process.</p></div>
                    <button className="btn-apply" onClick={() => handleApplyClick(loan)}>Learn more</button>
                  </div>
                ))}
              </div>
            </div>
          )}
          {activeTab === 'plans' && (
            <div className="tab-view fade-in">
              <h2>Planning for tomorrow</h2>
              <div className="grid-cards">
                {['Child Education Fund', 'Family Health Shield', 'Retirement Nest Egg', 'Gentle Tax Saver'].map(plan => (
                  <div key={plan} className="product-card">
                    <div><h3>{plan}</h3><p>Watch your wealth grow steadily over time.</p></div>
                    <button className="btn-apply" onClick={() => handleApplyClick(plan)}>Explore options</button>
                  </div>
                ))}
              </div>
            </div>
          )}
          {activeTab === 'accounts' && (
            <div className="tab-view fade-in">
              <h2>Your Connected Accounts</h2>
              <div className="account-list">
                <div className="account-item"><div className="account-item-icon">S</div><div><strong>SBI Salary Account</strong><p className="subtitle">Your primary foundation</p></div></div>
                <div className="account-item"><div className="account-item-icon">G</div><div><strong>Google Pay (UPI)</strong><p className="subtitle">Ready for daily sharing</p></div></div>
              </div>
              <button className="btn-secondary" style={{marginTop: '3rem', width: 'auto'}}>Connect another account</button>
            </div>
          )}
        </main>
      </div>
    </div>
  )
}

export default App
