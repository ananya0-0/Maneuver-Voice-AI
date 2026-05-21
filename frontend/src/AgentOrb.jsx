import './AgentOrb.css'

export default function AgentOrb({ state }) {
  return (
    <div className={`orb-wrapper orb-${state}`}>
      <div className="orb-ring orb-ring-3" />
      <div className="orb-ring orb-ring-2" />
      <div className="orb-ring orb-ring-1" />
      <div className="orb-core">
        <div className="orb-bars">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="orb-bar" style={{ animationDelay: `${i * 0.1}s` }} />
          ))}
        </div>
      </div>
    </div>
  )
}
