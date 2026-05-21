import './VisualPanel.css'

const SLIDES = {
  services: {
    title: 'What we build',
    color: 'purple',
    items: [
      { name: 'Product Sprint', duration: '2 weeks', desc: 'Research → validated prototype' },
      { name: 'Design System', duration: '3–6 weeks', desc: 'Full UI/UX + component library' },
      { name: 'Full-Stack Build', duration: '8–20 weeks', desc: 'End-to-end engineering & deploy' },
      { name: 'Ongoing Retainer', duration: 'Monthly', desc: '1 designer + 2 engineers on tap' },
    ],
  },
  pricing: {
    title: 'Pricing',
    color: 'teal',
    items: [
      { name: 'Product Sprint', duration: 'Flat fee', desc: '$8,000 – $12,000' },
      { name: 'Design System', duration: 'Flat fee', desc: '$15,000 – $25,000' },
      { name: 'Full-Stack Build', duration: 'Scoped', desc: '$40,000 – $120,000' },
      { name: 'Retainer', duration: '/month', desc: '$18,000' },
    ],
    note: 'Fixed-price contracts. 50% upfront, 25% midpoint, 25% on delivery.',
  },
  process: {
    title: 'How we work',
    color: 'amber',
    steps: [
      { n: '01', label: 'Discovery call', desc: 'Free · 1 hour · this conversation' },
      { n: '02', label: 'Proposal', desc: 'Scope + fixed price in 3–5 days' },
      { n: '03', label: 'Kickoff', desc: 'Notion, Figma, GitHub, Slack set up on Day 1' },
      { n: '04', label: 'Weekly sprints', desc: 'Friday demo + written update every week' },
      { n: '05', label: 'Handoff', desc: 'Docs, transfer sessions, 60-day bug support' },
    ],
  },
  case_studies: {
    title: 'Past work',
    color: 'coral',
    cases: [
      { client: 'Finmo', tag: 'B2B Payments · SG', result: 'Design overhaul → 40% fewer support tickets · $2M Series A' },
      { client: 'Kinn', tag: 'Health D2C · UK', result: 'MVP in 11 weeks → £500K pre-seed on live demo' },
      { client: 'Parcel', tag: 'Logistics SaaS · IN', result: 'Full rebuild → deploys from 2 weeks to 45 minutes' },
    ],
  },
  team: {
    title: 'The team',
    color: 'blue',
    members: [
      { name: 'Aryan Mehta', role: 'Founder & CEO', bg: 'Ex-Razorpay, ex-Meesho. IIT Bombay.' },
      { name: 'Priya Nair', role: 'Head of Design', bg: 'Ex-Zomato, ex-Swiggy. 9 years.' },
      { name: 'Kiran Rao', role: 'Lead Engineer', bg: 'Full-stack. React + distributed systems.' },
      { name: 'Tarun Gupta', role: 'Senior Engineer', bg: 'Backend. AWS certified.' },
      { name: 'Mei Lin', role: 'Client Success', bg: 'Singapore-based PM.' },
    ],
  },
}

export default function VisualPanel({ activeSlide, onClose }) {
  if (!activeSlide) {
    return (
      <div className="visual-panel empty">
        <div className="empty-hint">
          <span className="empty-icon">✦</span>
          <p>Ask about our services, pricing, process, or team</p>
        </div>
      </div>
    )
  }

  const slide = SLIDES[activeSlide]
  if (!slide) return null

  return (
    <div className={`visual-panel slide slide-${slide.color}`}>
      <div className="slide-header">
        <span className="slide-title">{slide.title}</span>
        <button className="slide-close" onClick={onClose} title="Close">✕</button>
      </div>

      {/* Services & Pricing — card grid */}
      {slide.items && (
        <div className="slide-cards">
          {slide.items.map((item) => (
            <div key={item.name} className="slide-card">
              <div className="card-top">
                <span className="card-name">{item.name}</span>
                <span className="card-duration">{item.duration}</span>
              </div>
              <p className="card-desc">{item.desc}</p>
            </div>
          ))}
          {slide.note && <p className="slide-note">{slide.note}</p>}
        </div>
      )}

      {/* Process — numbered steps */}
      {slide.steps && (
        <div className="slide-steps">
          {slide.steps.map((step) => (
            <div key={step.n} className="slide-step">
              <span className="step-num">{step.n}</span>
              <div>
                <p className="step-label">{step.label}</p>
                <p className="step-desc">{step.desc}</p>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Case studies */}
      {slide.cases && (
        <div className="slide-cases">
          {slide.cases.map((c) => (
            <div key={c.client} className="slide-case">
              <div className="case-top">
                <span className="case-client">{c.client}</span>
                <span className="case-tag">{c.tag}</span>
              </div>
              <p className="case-result">{c.result}</p>
            </div>
          ))}
        </div>
      )}

      {/* Team */}
      {slide.members && (
        <div className="slide-team">
          {slide.members.map((m) => (
            <div key={m.name} className="slide-member">
              <div className="member-avatar">{m.name[0]}</div>
              <div>
                <p className="member-name">{m.name}</p>
                <p className="member-role">{m.role}</p>
                <p className="member-bg">{m.bg}</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
