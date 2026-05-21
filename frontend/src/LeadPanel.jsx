import './LeadPanel.css'

const FIELDS = [
  { key: 'name',     label: 'Name',     icon: '👤' },
  { key: 'company',  label: 'Company',  icon: '🏢' },
  { key: 'role',     label: 'Role',     icon: '💼' },
  { key: 'problem',  label: 'Problem',  icon: '🔍' },
  { key: 'solution', label: 'Building', icon: '🛠' },
  { key: 'timeline', label: 'Timeline', icon: '📅' },
  { key: 'budget',   label: 'Budget',   icon: '💰' },
]

export default function LeadPanel({ data, finalized }) {
  const filledCount = FIELDS.filter((f) => data[f.key]).length

  return (
    <div className="lead-panel">
      <div className="lead-header">
        <span className="lead-title">Discovery</span>
        <span className="lead-progress">{filledCount}/{FIELDS.length}</span>
      </div>
      <div className="lead-progress-bar">
        <div
          className="lead-progress-fill"
          style={{ width: `${(filledCount / FIELDS.length) * 100}%` }}
        />
      </div>

      <div className="lead-fields">
        {FIELDS.map((f) => (
          <div key={f.key} className={`lead-field ${data[f.key] ? 'filled' : 'empty'}`}>
            <span className="field-icon">{f.icon}</span>
            <div className="field-content">
              <span className="field-label">{f.label}</span>
              {data[f.key] ? (
                <span className="field-value">{data[f.key]}</span>
              ) : (
                <span className="field-placeholder">Not captured yet</span>
              )}
            </div>
          </div>
        ))}
      </div>

      {data.notes && (
        <div className="lead-notes">
          <span className="field-label">Notes</span>
          <p className="notes-text">{data.notes}</p>
        </div>
      )}

      {finalized && (
        <div className="lead-finalized">
          <span className="finalized-icon">✓</span>
          Lead saved
        </div>
      )}

      {data.summary && (
        <div className="lead-summary">
          <span className="field-label">Summary</span>
          <p className="summary-text">{data.summary}</p>
        </div>
      )}
    </div>
  )
}
