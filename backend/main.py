#!/usr/bin/env python3
"""
AllStarLink Transcriber - Backend Service
Real-time audio transcription from AllStarLink 3.0 nodes via iaxclient
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
from datetime import datetime
from typing import Optional
from collections import deque

import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import whisper

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration from environment
ALLSTARLINK_NODE = os.getenv("ALLSTARLINK_NODE", "9001")
ALLSTARLINK_HOST = os.getenv("ALLSTARLINK_HOST", "localhost")
ALLSTARLINK_PORT = os.getenv("ALLSTARLINK_PORT", "4569")
ALLSTARLINK_USER = os.getenv("ALLSTARLINK_USER", "guest")
ALLSTARLINK_PASSWORD = os.getenv("ALLSTARLINK_PASSWORD", "guest")
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "small")
AUDIO_CHUNK_SECONDS = int(os.getenv("AUDIO_CHUNK_SECONDS", "10"))
FRONTEND_PATH = os.getenv("FRONTEND_PATH", "/app/frontend/dist")

# Derived settings
SAMPLE_RATE = 16000  # Whisper expects 16kHz
CHUNK_SIZE = SAMPLE_RATE * AUDIO_CHUNK_SECONDS
SILENCE_THRESHOLD = 1000  # Energy threshold for silence detection

# Initialize FastAPI app
app = FastAPI(title="AllStarLink Transcriber", version="1.0.0")

# CORS middleware for WebSocket and API access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TranscriptSegment(BaseModel):
    """Single transcript segment"""
    id: str
    timestamp: str
    text: str
    confidence: float
    duration: float


class TranscriptionState:
    """Manages transcription state and WebSocket connections"""
    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.audio_buffer: deque = deque(maxlen=CHUNK_SIZE * 2)
        self.transcript_history: list[TranscriptSegment] = []
        self.is_recording = False
        self.iax_process: Optional[subprocess.Popen] = None
        self.whisper_model = None
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected WebSocket clients"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"Failed to send to connection: {e}")
                disconnected.append(connection)
        
        # Remove disconnected clients
        for conn in disconnected:
            self.active_connections.remove(conn)


# Global state
state = TranscriptionState()


class AudioProcessor:
    """Handles audio capture, buffering, and transcription"""
    def __init__(self):
        self.audio_buffer = np.array([], dtype=np.float32)
        self.segment_counter = 0
        self.session_start = datetime.now()
    
    def process_audio_chunk(self, audio_bytes: bytes) -> Optional[np.ndarray]:
        """
        Convert raw audio bytes to float32 numpy array
        Expects 16-bit PCM mono audio
        """
        try:
            audio_data = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
            return audio_data
        except Exception as e:
            logger.error(f"Error processing audio chunk: {e}")
            return None
    
    async def transcribe_chunk(self, audio_chunk: np.ndarray) -> Optional[TranscriptSegment]:
        """
        Transcribe a 10-second audio chunk using Whisper
        Runs in thread pool to avoid blocking
        """
        if state.whisper_model is None:
            logger.info(f"Loading Whisper model: {WHISPER_MODEL}")
            state.whisper_model = whisper.load_model(WHISPER_MODEL, device="cpu")
        
        try:
            # Transcribe the audio
            result = state.whisper_model.transcribe(
                audio_chunk,
                language="en",
                fp16=False,  # CPU doesn't support fp16
                verbose=False
            )
            
            text = result.get("text", "").strip()
            if not text:
                return None
            
            # Calculate confidence from word-level confidence if available
            confidence = 0.95  # Default confidence
            
            # Create segment
            self.segment_counter += 1
            segment = TranscriptSegment(
                id=f"{self.session_start.isoformat()}_{self.segment_counter}",
                timestamp=datetime.now().isoformat(),
                text=text,
                confidence=confidence,
                duration=AUDIO_CHUNK_SECONDS
            )
            
            return segment
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return None


async def read_iax_stream():
    """
    Read audio from iaxclient subprocess and process chunks
    """
    processor = AudioProcessor()
    
    try:
        # Construct iaxclient command
        iax_cmd = [
            "iaxclient",
            "-c", f"guest@{ALLSTARLINK_HOST}:{ALLSTARLINK_PORT}/{ALLSTARLINK_NODE}",
            "-u", ALLSTARLINK_USER,
            "-p", ALLSTARLINK_PASSWORD,
        ]
        
        logger.info(f"Starting iaxclient: {' '.join(iax_cmd)}")
        state.iax_process = subprocess.Popen(
            iax_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=4096
        )
        
        state.is_recording = True
        await state.broadcast({
            "type": "status",
            "status": "connected",
            "timestamp": datetime.now().isoformat(),
            "node": ALLSTARLINK_NODE,
            "host": ALLSTARLINK_HOST
        })
        
        # Read audio in chunks
        while state.is_recording and state.iax_process.poll() is None:
            try:
                chunk = state.iax_process.stdout.read(4096)
                if not chunk:
                    await asyncio.sleep(0.01)
                    continue
                
                # Process and buffer audio
                audio_data = processor.process_audio_chunk(chunk)
                if audio_data is not None:
                    state.audio_buffer.extend(audio_data)
                
                # Check if we have enough for a chunk
                if len(state.audio_buffer) >= CHUNK_SIZE:
                    # Extract chunk from buffer
                    chunk_data = np.array(list(state.audio_buffer)[:CHUNK_SIZE])
                    
                    # Remove processed data from buffer
                    for _ in range(min(CHUNK_SIZE // 2, len(state.audio_buffer))):
                        state.audio_buffer.popleft()
                    
                    # Transcribe in background task
                    asyncio.create_task(
                        transcribe_and_broadcast(processor, chunk_data)
                    )
            
            except Exception as e:
                logger.error(f"Error reading IAX stream: {e}")
                await asyncio.sleep(0.1)
    
    except Exception as e:
        logger.error(f"IAX stream error: {e}")
        state.is_recording = False
        await state.broadcast({
            "type": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        })
    finally:
        state.is_recording = False
        if state.iax_process:
            state.iax_process.terminate()
            try:
                state.iax_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                state.iax_process.kill()
        
        await state.broadcast({
            "type": "status",
            "status": "disconnected",
            "timestamp": datetime.now().isoformat()
        })


async def transcribe_and_broadcast(processor: AudioProcessor, audio_chunk: np.ndarray):
    """
    Transcribe audio chunk and broadcast result to WebSocket clients
    """
    try:
        segment = await asyncio.to_thread(processor.transcribe_chunk, audio_chunk)
        
        if segment:
            state.transcript_history.append(segment)
            
            await state.broadcast({
                "type": "transcript",
                "segment": segment.model_dump(),
                "timestamp": datetime.now().isoformat()
            })
            
            logger.info(f"Transcribed: {segment.text[:100]}...")
    
    except Exception as e:
        logger.error(f"Transcription broadcast error: {e}")


# WebSocket endpoint for real-time transcript streaming
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for streaming transcripts
    Sends live transcript segments as they're transcribed
    """
    await websocket.accept()
    state.active_connections.append(websocket)
    
    logger.info("WebSocket client connected")
    
    # Send current transcript history on connect
    await websocket.send_json({
        "type": "history",
        "segments": [s.model_dump() for s in state.transcript_history],
        "timestamp": datetime.now().isoformat()
    })
    
    try:
        while True:
            # Keep connection alive, listen for client messages
            data = await websocket.receive_text()
            msg = json.loads(data)
            
            if msg.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
            elif msg.get("type") == "clear":
                state.transcript_history.clear()
                await state.broadcast({"type": "cleared"})
    
    except WebSocketDisconnect:
        state.active_connections.remove(websocket)
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        if websocket in state.active_connections:
            state.active_connections.remove(websocket)


@app.get("/api/status")
async def get_status():
    """Get current connection and transcription status"""
    return {
        "is_recording": state.is_recording,
        "segment_count": len(state.transcript_history),
        "allstarlink_node": ALLSTARLINK_NODE,
        "allstarlink_host": ALLSTARLINK_HOST,
        "whisper_model": WHISPER_MODEL,
        "audio_chunk_seconds": AUDIO_CHUNK_SECONDS,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/transcripts")
async def get_transcripts(limit: int = 100):
    """Get transcript history"""
    return {
        "segments": [s.model_dump() for s in state.transcript_history[-limit:]],
        "total": len(state.transcript_history),
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/start")
async def start_recording():
    """Start recording from AllStarLink node"""
    if not state.is_recording:
        asyncio.create_task(read_iax_stream())
        return {"status": "started", "timestamp": datetime.now().isoformat()}
    return {"status": "already_running", "timestamp": datetime.now().isoformat()}


@app.post("/api/stop")
async def stop_recording():
    """Stop recording"""
    state.is_recording = False
    if state.iax_process:
        state.iax_process.terminate()
    return {"status": "stopped", "timestamp": datetime.now().isoformat()}


@app.post("/api/clear")
async def clear_transcripts():
    """Clear transcript history"""
    state.transcript_history.clear()
    return {"status": "cleared", "timestamp": datetime.now().isoformat()}


# Serve frontend static files
if Path(FRONTEND_PATH).exists():
    app.mount("/", StaticFiles(directory=FRONTEND_PATH, html=True), name="frontend")


@app.on_event("startup")
async def startup_event():
    """Start the IAX stream reader on app startup"""
    logger.info("AllStarLink Transcriber starting up")
    asyncio.create_task(read_iax_stream())


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on shutdown"""
    logger.info("AllStarLink Transcriber shutting down")
    state.is_recording = False
    if state.iax_process:
        state.iax_process.terminate()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
