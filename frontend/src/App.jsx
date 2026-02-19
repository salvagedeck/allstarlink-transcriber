import React, { useState, useEffect, useRef } from 'react'
import { Play, Square, Trash2, Settings, Moon, Sun } from 'lucide-react'
import TranscriptDisplay from './components/TranscriptDisplay'
import ControlPanel from './components/ControlPanel'
import ThemeProvider from './context/ThemeProvider'
import { useTheme } from './context/ThemeProvider'

function AppContent() {
  const [isConnected, setIsConnected] = useState(false)
  const [isRecording, setIsRecording] = useState(false)
  const [transcripts, setTranscripts] = useState([])
  const [status, setStatus] = useState(null)
  const [error, setError] = useState(null)
  const wsRef = useRef(null)
  const { theme, toggleTheme } = useTheme()

  // WebSocket connection
  useEffect(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${protocol}//${window.location.host}/ws`
    
    const ws = new WebSocket(wsUrl)
    
    ws.onopen = () => {
      console.log('WebSocket connected')
      setIsConnected(true)
      setError(null)
    }
    
    ws.onmessage = (event) => {
      const message = JSON.parse(event.data)
      
      if (message.type === 'history') {
        setTranscripts(message.segments || [])
      } else if (message.type === 'transcript') {
        setTranscripts(prev => [...prev, message.segment])
      } else if (message.type === 'status') {
        setStatus(message)
        if (message.status === 'connected') {
          setIsRecording(true)
        } else if (message.status === 'disconnected') {
          setIsRecording(false)
        }
      } else if (message.type === 'error') {
        setError(message.error)
      } else if (message.type === 'cleared') {
        setTranscripts([])
      }
    }
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      setError('WebSocket connection error')
    }
    
    ws.onclose = () => {
      console.log('WebSocket disconnected')
      setIsConnected(false)
      setIsRecording(false)
      setTimeout(() => {
        // Attempt reconnection
      }, 3000)
    }
    
    wsRef.current = ws
    
    // Fetch initial status
    fetchStatus()
    
    return () => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.close()
      }
    }
  }, [])

  const fetchStatus = async () => {
    try {
      const response = await fetch('/api/status')
      const data = await response.json()
      setStatus(data)
      setIsRecording(data.is_recording)
    } catch (err) {
      console.error('Failed to fetch status:', err)
    }
  }

  const handleStart = async () => {
    try {
      const response = await fetch('/api/start', { method: 'POST' })
      const data = await response.json()
      setIsRecording(true)
      setError(null)
    } catch (err) {
      setError('Failed to start recording: ' + err.message)
    }
  }

  const handleStop = async () => {
    try {
      const response = await fetch('/api/stop', { method: 'POST' })
      const data = await response.json()
      setIsRecording(false)
      setError(null)
    } catch (err) {
      setError('Failed to stop recording: ' + err.message)
    }
  }

  const handleClear = async () => {
    try {
      const response = await fetch('/api/clear', { method: 'POST' })
      setTranscripts([])
      setError(null)
    } catch (err) {
      setError('Failed to clear transcripts: ' + err.message)
    }
  }

  return (
    <div className="min-h-screen bg-background text-foreground transition-colors duration-200">
      {/* Header */}
      <header className="border-b border-border bg-secondary shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-primary flex items-center gap-2">
              <span className="text-2xl">📡</span>
              AllStarLink Transcriber
            </h1>
            <p className="text-sm text-muted-foreground mt-1">Real-time audio transcription from AllStarLink 3.0</p>
          </div>
          <button
            onClick={toggleTheme}
            className="p-2 rounded-lg hover:bg-primary/10 transition-colors"
            title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
          >
            {theme === 'dark' ? <Sun size={24} /> : <Moon size={24} />}
          </button>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Status Bar */}
        <div className="mb-6 p-4 rounded-lg border border-border bg-secondary">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></div>
              <div>
                <p className="font-semibold text-foreground">
                  {isConnected ? 'Connected' : 'Disconnected'}
                </p>
                <p className="text-xs text-muted-foreground">
                  {status && `Node: ${status.allstarlink_node} | Model: ${status.whisper_model}`}
                </p>
              </div>
            </div>
            <div className="text-sm font-mono text-muted-foreground">
              Segments: {transcripts.length}
            </div>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-6 p-4 rounded-lg bg-red-500/10 border border-red-500/20 text-red-700 dark:text-red-400">
            <p className="font-semibold">Error</p>
            <p className="text-sm">{error}</p>
          </div>
        )}

        {/* Control Panel */}
        <ControlPanel
          isRecording={isRecording}
          onStart={handleStart}
          onStop={handleStop}
          onClear={handleClear}
          isConnected={isConnected}
        />

        {/* Transcript Display */}
        <div className="mt-8">
          <h2 className="text-xl font-semibold text-primary mb-4">Live Transcription</h2>
          <TranscriptDisplay transcripts={transcripts} />
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-border bg-secondary mt-16 py-4">
        <div className="max-w-7xl mx-auto px-4 text-center text-sm text-muted-foreground">
          <p>AllStarLink Transcriber v1.0.0 | Real-time transcription powered by OpenAI Whisper</p>
        </div>
      </footer>
    </div>
  )
}

function App() {
  return (
    <ThemeProvider>
      <AppContent />
    </ThemeProvider>
  )
}

export default App
