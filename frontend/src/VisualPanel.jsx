import './VisualPanel.css'

const SLIDES = {
  services: {
    title: 'What we do',
    color: 'purple',
    items: [
      { name: 'Intelligent Workflows', duration: 'Automation', desc: 'Connect your tools — 40% less manual work, 10x faster iteration' },
      { name: 'Voice AI', duration: '24/7', desc: 'Arabic & English voice agents integrated with your CRM and booking systems' },
      { name: 'Self-Learning AI Agents', duration: 'Always on', desc: 'Handle enquiries, route requests, free your team for higher-value work' },
      { name: 'Bespoke Applications', duration: 'Custom build', desc: 'One purpose-built system replacing your scattered tools — your IP' },
      { name: 'Systems Integration', duration: 'Connect', desc: 'Link AI to your existing CRM, email, and databases into one system' },
    ],
  },
  pricing: {
    title: 'How we price',
    color: 'teal',
    items: [
      { name: 'Discovery Call', duration: 'Free', desc: '30 minutes — honest assessment of whether AI moves the needle for you' },
      { name: 'Project Engagements', duration: 'Fixed scope', desc: 'Quoted after scoping — no hourly billing, no surprise invoices' },
      { name: 'Ongoing Partnership', duration: 'Retainer', desc: 'For companies that want continued iteration and a standing senior team' },
    ],
    note: 'Pricing discussed honestly on the discovery call — we don\'t publish rates because every engagement is different.',
  },
  process: {
    title: 'How we work',
    color: 'amber',
    steps: [
      { n: '01', label: 'Understand', desc: 'We listen first — what\'s working, what\'s not, where the pressure is. No assumptions.' },
      { n: '02', label: 'Design & Build', desc: 'Highest-impact opportunities identified, then built into things your team will actually use.' },
      { n: '03', label: 'Launch & Evolve', desc: 'We deploy, refine, and stay. The best systems improve over time.' },
    ],
  },
  case_studies: {
    title: 'Past work',
    color: 'coral',
    cases: [
      { client: 'Freight Brokerage', tag: 'Logistics · UAE', result: 'Automated dispatch & tracking → 3+ hrs/day recovered per dispatcher · deployed in 4 weeks' },
      { client: 'Hospitality Group', tag: 'Hospitality · Dubai', result: 'AI concierge across WhatsApp, Airbnb & Booking.com → 80% of comms automated · 24/7' },
      { client: 'Industrial Supplier', tag: 'Supply Chain · UAE', result: 'Unified WhatsApp + Voice AI → 60%+ reduction in manual data entry · 3 channels into 1' },
    ],
  },
  team: {
    title: 'Who builds this',
    color: 'blue',
    members: [
      { name: 'Husain Topiwala', role: 'Founder', bg: 'JP Morgan · Vanguard · Deloitte · Think41 (founding team) · SleevesUp India (0→35 people)' },
      { name: 'Senior team', role: 'Implementation', bg: 'Deep expertise in AI engineering, cloud infrastructure, and enterprise systems. No juniors.' },
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
