import { useState, useEffect, useCallback, useRef } from 'react'
import {
  useLocalParticipant,
  useRoomContext,
  useConnectionState,
  RoomAudioRenderer,
  useVoiceAssistant,
} from '@livekit/components-react'
import { RoomEvent, DataPacket_Kind } from 'livekit-client'
import LeadPanel from './LeadPanel.jsx'
import VisualPanel from './VisualPanel.jsx'
import AgentOrb from './AgentOrb.jsx'
import TranscriptPanel from './TranscriptPanel.jsx'
import './VoiceInterface.css'

export default function VoiceInterface({ onHangUp }) {
  const room = useRoomContext()
  const { localParticipant } = useLocalParticipant()
  const connectionState = useConnectionState()
  const { state: agentState } = useVoiceAssistant()

  const [leadData, setLeadData] = useState({})
  const [activeSlide, setActiveSlide] = useState(null)
  const [transcript, setTranscript] = useState([])
  const [isMuted, setIsMuted] = useState(false)
  const [callDuration, setCallDuration] = useState(0)
  const [leadFinalized, setLeadFinalized] = useState(false)
  const startTimeRef = useRef(Date.now())

  // Call duration timer
  useEffect(() => {
    const timer = setInterval(() => {
      setCallDuration(Math.floor((Date.now() - startTimeRef.current) / 1000))
    }, 1000)
    return () => clearInterval(timer)
  }, [])

  // Listen for data messages from agent (RPC channel)
  useEffect(() => {
    const handleData = (payload, participant, _kind, topic) => {
      if (topic !== 'agent_rpc') return
      try {
        const { method, payload: data } = JSON.parse(new TextDecoder().decode(payload))
        handleAgentRPC(method, data)
      } catch (e) {
        console.warn('Failed to parse RPC message', e)
      }
    }

    room.on(RoomEvent.DataReceived, handleData)
    return () => room.off(RoomEvent.DataReceived, handleData)
  }, [room])

  // Listen for transcription events
  useEffect(() => {
    const handleTranscription = (segments, participant) => {
      const isAgent = participant?.identity?.startsWith('agent') ?? false
      segments.forEach((seg) => {
        if (seg.final) {
          setTranscript((prev) => [
            ...prev.slice(-40), // keep last 40 entries
            {
              id: seg.id,
              text: seg.text,
              speaker: isAgent ? 'aryan' : 'you',
              timestamp: Date.now(),
            },
          ])
        }
      })
    }

    room.on(RoomEvent.TranscriptionReceived, handleTranscription)
    return () => room.off(RoomEvent.TranscriptionReceived, handleTranscription)
  }, [room])

  const handleAgentRPC = useCallback((method, data) => {
    switch (method) {
      case 'update_lead_field':
        setLeadData((prev) => ({ ...prev, [data.field]: data.value }))
        break
      case 'show_slide':
        setActiveSlide(data.slide)
        break
      case 'agent_state':
        // state is already surfaced by useVoiceAssistant
        break
      case 'lead_finalized':
        setLeadData(data.lead || {})
        setLeadFinalized(true)
        break
      default:
        break
    }
  }, [])

  const toggleMute = useCallback(async () => {
    await localParticipant.setMicrophoneEnabled(isMuted)
    setIsMuted(!isMuted)
  }, [localParticipant, isMuted])

  const formatDuration = (s) => {
    const m = Math.floor(s / 60)
    const sec = s % 60
    return `${m}:${sec.toString().padStart(2, '0')}`
  }

  const displayState = agentState ?? 'connecting'

  return (
    <div className="voice-interface">
      <RoomAudioRenderer />

      {/* Top bar */}
      <div className="top-bar">
        <div className="logo-sm">Maneuver</div>
        <div className="call-info">
          <span className={`state-badge state-${displayState}`}>
            {displayState === 'listening' ? 'Listening' :
             displayState === 'thinking' ? 'Thinking' :
             displayState === 'speaking' ? 'Speaking' : 'Connecting'}
          </span>
          <span className="duration">{formatDuration(callDuration)}</span>
        </div>
        <button className="hang-up-btn" onClick={onHangUp} title="End call">
          End call
        </button>
      </div>

      {/* Main layout */}
      <div className="main-layout">
        {/* Left: lead tracker */}
        <div className="left-panel">
          <LeadPanel data={leadData} finalized={leadFinalized} />
        </div>

        {/* Center: agent orb + transcript */}
        <div className="center-panel">
          <AgentOrb state={displayState} />
          <div className="founder-id">
            <div className="founder-avatar">H</div>
            <div>
              <p className="founder-name">Husain Topiwala</p>
              <p className="founder-role">Founder, Maneuver</p>
            </div>
          </div>
          <div className="controls">
            <button
              className={`mute-btn ${isMuted ? 'muted' : ''}`}
              onClick={toggleMute}
              title={isMuted ? 'Unmute' : 'Mute'}
            >
              {isMuted ? '🔇 Muted' : '🎙 Mic on'}
            </button>
          </div>
          <TranscriptPanel entries={transcript} />
        </div>

        {/* Right: visual slides */}
        <div className="right-panel">
          <VisualPanel activeSlide={activeSlide} onClose={() => setActiveSlide(null)} />
        </div>
      </div>
    </div>
  )
}
