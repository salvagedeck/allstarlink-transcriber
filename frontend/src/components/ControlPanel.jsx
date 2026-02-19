import React from 'react'
import { Play, Square, Trash2 } from 'lucide-react'

export default function ControlPanel({ isRecording, onStart, onStop, onClear, isConnected }) {
  return (
    <div className="card flex gap-3 flex-wrap">
      <button
        onClick={onStart}
        disabled={isRecording || !isConnected}
        className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
      >
        <Play size={18} />
        Start Recording
      </button>
      
      <button
        onClick={onStop}
        disabled={!isRecording}
        className="btn-danger disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
      >
        <Square size={18} />
        Stop Recording
      </button>
      
      <button
        onClick={onClear}
        className="btn-secondary flex items-center gap-2"
      >
        <Trash2 size={18} />
        Clear Transcripts
      </button>
    </div>
  )
}
