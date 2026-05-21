import { useState, useEffect, useCallback } from 'react'
import { LiveKitRoom } from '@livekit/components-react'
import '@livekit/components-styles'
import VoiceInterface from './VoiceInterface.jsx'
import './App.css'

const SERVER_URL = 'http://localhost:8000'
const ROOM_NAME = 'maneuver-room'

export default function App() {
  const [connectionDetails, setConnectionDetails] = useState(null)
  const [connecting, setConnecting] = useState(false)
  const [error, setError] = useState(null)

  const handleConnect = useCallback(async () => {
    setConnecting(true)
    setError(null)
    try {
      const res = await fetch(
        `${SERVER_URL}/token?room=${ROOM_NAME}&participant=visitor-${Date.now()}`
      )
      if (!res.ok) throw new Error('Could not get connection token from server')
      const data = await res.json()
      setConnectionDetails(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setConnecting(false)
    }
  }, [])

  const handleDisconnect = useCallback(() => {
    setConnectionDetails(null)
  }, [])

  if (!connectionDetails) {
    return (
      <div className="landing">
        <div className="landing-inner">
          <div className="logo-mark">M</div>
          <h1 className="landing-title">Talk to the founder</h1>
          <p className="landing-sub">
            Skip the contact form. Have a real conversation with Aryan, founder of Maneuver.
            Tell him what you're building — he'll tell you if we can help.
          </p>
          {error && <p className="error-msg">{error}. Make sure the backend server is running.</p>}
          <button
            className="cta-btn"
            onClick={handleConnect}
            disabled={connecting}
          >
            {connecting ? (
              <span className="connecting-dots">
                <span /><span /><span />
              </span>
            ) : (
              <>
                <span className="mic-icon">🎙</span>
                Start talking
              </>
            )}
          </button>
          <p className="landing-hint">Microphone required · Usually 10–15 min</p>
        </div>
      </div>
    )
  }

  return (
    <LiveKitRoom
      token={connectionDetails.token}
      serverUrl={connectionDetails.url}
      connect={true}
      audio={true}
      video={false}
      onDisconnected={handleDisconnect}
      style={{ height: '100dvh' }}
    >
      <VoiceInterface onHangUp={handleDisconnect} />
    </LiveKitRoom>
  )
}
