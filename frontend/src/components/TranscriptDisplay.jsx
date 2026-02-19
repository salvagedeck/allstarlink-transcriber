import React, { useEffect, useRef } from 'react'

export default function TranscriptDisplay({ transcripts }) {
  const containerRef = useRef(null)

  useEffect(() => {
    // Auto-scroll to bottom when new transcripts arrive
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight
    }
  }, [transcripts])

  if (transcripts.length === 0) {
    return (
      <div className="card text-center py-12">
        <p className="text-muted-foreground">
          No transcripts yet. Start recording to see live transcription.
        </p>
      </div>
    )
  }

  return (
    <div
      ref={containerRef}
      className="card max-h-96 overflow-y-auto space-y-3 bg-gradient-to-b from-secondary to-background"
    >
      {transcripts.map((segment, index) => (
        <div
          key={segment.id}
          className="p-3 rounded-lg bg-background border border-border hover:border-primary/50 transition-colors"
        >
          <div className="flex justify-between items-start gap-2 mb-2">
            <div className="flex items-center gap-2">
              <span className="text-xs font-mono text-muted-foreground">
                #{index + 1}
              </span>
              <span className="text-xs text-muted-foreground">
                {new Date(segment.timestamp).toLocaleTimeString()}
              </span>
            </div>
            <span className="text-xs px-2 py-1 rounded bg-primary/10 text-primary font-medium">
              {(segment.confidence * 100).toFixed(0)}%
            </span>
          </div>
          
          <p className="text-foreground leading-relaxed text-sm md:text-base">
            {segment.text}
          </p>
          
          <div className="mt-2 text-xs text-muted-foreground flex items-center gap-2">
            <span className="font-mono">{segment.duration.toFixed(1)}s</span>
          </div>
        </div>
      ))}
    </div>
  )
}
