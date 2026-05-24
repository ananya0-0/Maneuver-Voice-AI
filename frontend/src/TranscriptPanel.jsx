import { useEffect, useRef } from 'react'
import './TranscriptPanel.css'

export default function TranscriptPanel({ entries }) {
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [entries])

  if (entries.length === 0) {
    return (
      <div className="transcript-panel empty">
        <p className="transcript-empty">Transcript will appear here…</p>
      </div>
    )
  }

  return (
    <div className="transcript-panel">
      {entries.map((entry) => (
        <div key={entry.id} className={`transcript-entry entry-${entry.speaker}`}>
          <span className="entry-speaker">
            {entry.speaker === 'husain' ? 'Husain' : 'You'}
          </span>
          <p className="entry-text">{entry.text}</p>
        </div>
      ))}
      <div ref={bottomRef} />
    </div>
  )
}
