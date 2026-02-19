# AllStarLink Transcriber

Real-time audio transcription from AllStarLink 3.0 nodes using OpenAI's Whisper model and a modern React web interface.

## Features

✨ **Real-Time Transcription**
- Live streaming transcription with sub-10-second latency
- Powered by OpenAI's Whisper (small model for best accuracy)
- 10-second audio chunks for optimal balance between latency and accuracy

🎨 **Modern Web Interface**
- Built with React + shadcn/ui + Tailwind CSS
- Live streaming transcript display with auto-scrolling
- Theme support: Light, Dark, and High Contrast modes
- Real-time status indicators
- Confidence scores for each transcribed segment

🔧 **Flexible Configuration**
- Docker-based deployment for easy portability
- All configuration via environment variables
- SQLite database for persistent transcript storage
- Support for multiple AllStarLink nodes

📊 **Production Ready**
- Health checks and automatic restart
- Comprehensive error handling and logging
- WebSocket for real-time client updates
- RESTful API for programmatic access

## Architecture

```
┌─────────────────┐
│  AllStarLink    │
│  3.0 Node       │
└────────┬────────┘
         │ IAX2 Protocol
         ▼
┌─────────────────┐
│  iaxclient      │
│  (audio bridge) │
└────────┬────────┘
         │ Raw PCM Audio
         ▼
┌──────────────────────────┐
│  FastAPI Backend         │
│  ├─ Audio Buffer         │
│  ├─ Whisper Transcriber  │
│  ├─ SQLite Database      │
│  └─ WebSocket Server     │
└────────┬─────────────────┘
         │ WebSocket + REST API
         ▼
┌──────────────────────────┐
│  React Web UI            │
│  ├─ Live Transcript      │
│  ├─ Controls             │
│  └─ Theme Switching      │
└──────────────────────────┘
```

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Access to an AllStarLink 3.0 node (local or remote)
- Basic knowledge of node credentials (host, port, node number)

### Installation (5 minutes)

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/allstarlink-transcriber.git
   cd allstarlink-transcriber
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   ```

3. **Configure your AllStarLink connection**
   ```bash
   nano .env
   ```
   
   Set these values:
   ```
   ALLSTARLINK_NODE=9001
   ALLSTARLINK_HOST=192.168.1.100      # Your node's IP/hostname
   ALLSTARLINK_PORT=4569
   ALLSTARLINK_USER=guest
   ALLSTARLINK_PASSWORD=guest
   ```

4. **Build and start the service**
   ```bash
   docker-compose build
   docker-compose up -d
   ```
   
   **That's it!** The Docker build automatically:
   - Clones and compiles iaxclient from source
   - Builds the React frontend
   - Installs all dependencies
   - Creates the complete image

5. **Access the web interface**
   ```
   http://localhost:8000
   ```

## Configuration

All configuration is managed through environment variables in `.env` or `docker-compose.yml`.

### AllStarLink Connection

| Variable | Default | Description |
|----------|---------|-------------|
| `ALLSTARLINK_NODE` | `9001` | Target node number |
| `ALLSTARLINK_HOST` | `localhost` | Node hostname/IP address |
| `ALLSTARLINK_PORT` | `4569` | IAX2 port |
| `ALLSTARLINK_USER` | `guest` | IAX2 username |
| `ALLSTARLINK_PASSWORD` | `guest` | IAX2 password |

### Whisper Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `WHISPER_MODEL` | `small` | Model size: `tiny`, `base`, or `small` |
| `AUDIO_CHUNK_SECONDS` | `10` | Chunk size: 10, 30, or 60 seconds |

**Model Comparison:**
- `tiny` (~39MB): Fastest, lower accuracy
- `base` (~140MB): Balanced (good for most use cases)
- `small` (~244MB): **Default** - best accuracy on CPU

### UI Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `UI_THEME` | `dark` | Theme: `light`, `dark`, or `high-contrast` |
| `WEB_PORT` | `8000` | Web server port |

### Storage

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_PATH` | `/app/data/transcripts.db` | SQLite database location |
| `FRONTEND_PATH` | `/app/frontend/dist` | Frontend static files path |

## Usage

### Web Interface

**Controls:**
- **Start Recording** - Begin transcription from the AllStarLink node
- **Stop Recording** - Stop active transcription
- **Clear Transcripts** - Clear all transcript history
- **Theme Toggle** - Switch between Light, Dark, and High Contrast modes

**Status Indicators:**
- Green pulsing dot: Connected to backend
- Red dot: Disconnected
- Segment count: Number of transcribed segments

### REST API

#### Get Status
```bash
curl http://localhost:8000/api/status
```

Response:
```json
{
  "is_recording": true,
  "segment_count": 42,
  "allstarlink_node": "9001",
  "allstarlink_host": "localhost",
  "whisper_model": "small",
  "audio_chunk_seconds": 10,
  "timestamp": "2026-02-19T12:34:56.789Z"
}
```

#### Get Transcripts
```bash
curl http://localhost:8000/api/transcripts?limit=10
```

#### Start Recording
```bash
curl -X POST http://localhost:8000/api/start
```

#### Stop Recording
```bash
curl -X POST http://localhost:8000/api/stop
```

#### Clear Transcripts
```bash
curl -X POST http://localhost:8000/api/clear
```

### WebSocket (Real-Time Updates)

Connect to `ws://localhost:8000/ws` for real-time transcript streaming.

**Message Types:**
- `history`: Initial transcript history on connection
- `transcript`: New transcribed segment
- `status`: Connection status changes
- `error`: Error messages
- `cleared`: Transcripts cleared

## Building from Source

### Build Docker Image
```bash
docker-compose build --no-cache
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

### Backend Development
```bash
cd backend
pip install -r requirements.txt
python3 main.py
```

Set environment variables:
```bash
export ALLSTARLINK_NODE=9001
export ALLSTARLINK_HOST=localhost
export WHISPER_MODEL=small
```

## Troubleshooting

### Connection Issues

**"Cannot connect to AllStarLink node"**
- Verify `ALLSTARLINK_HOST` is correct (use IP if hostname doesn't resolve)
- Check firewall allows port `ALLSTARLINK_PORT` (default 4569)
- Verify credentials (`ALLSTARLINK_USER`, `ALLSTARLINK_PASSWORD`)
- Ensure `iaxclient` is properly installed in container

**Test connection:**
```bash
docker-compose exec allstarlink-transcriber \
  iaxclient -c "guest@192.168.1.100:4569/9001"
```

### Transcription Issues

**"No transcripts appearing"**
- Check audio levels on the node
- Verify `WHISPER_MODEL` is properly set
- Check backend logs: `docker-compose logs -f`
- Ensure sufficient disk space for model cache (~500MB for small model)

**"Slow transcription"**
- Reduce `AUDIO_CHUNK_SECONDS` for lower latency (but more CPU usage)
- Use `tiny` or `base` model instead of `small`
- Check CPU usage: `docker stats`
- If using VirtualBox/VM, enable 3D acceleration if available

### Frontend Issues

**"WebSocket connection failed"**
- Verify backend is running: `docker-compose ps`
- Check firewall allows WebSocket connections
- Browser console (F12) shows detailed error messages

**"Theme not applying"**
- Clear browser cache and localStorage
- Try different theme by clicking theme toggle button
- Check `UI_THEME` environment variable

### Log Access

View backend logs:
```bash
docker-compose logs -f allstarlink-transcriber
```

View specific errors:
```bash
docker-compose logs -f | grep -i error
```

## Performance Tuning

### For Lower Latency
```env
AUDIO_CHUNK_SECONDS=10    # Already default
WHISPER_MODEL=tiny        # Fastest transcription
```
Expected latency: 2-5 seconds per segment

### For Better Accuracy
```env
WHISPER_MODEL=small       # Best accuracy (default)
AUDIO_CHUNK_SECONDS=30    # More context for model
```
Expected latency: 5-10 seconds per segment

### For Resource Constrained Systems
```env
WHISPER_MODEL=tiny
AUDIO_CHUNK_SECONDS=30
```

## Scaling

### Multiple Nodes

To monitor multiple nodes, run separate container instances:

```yaml
services:
  transcriber-node-1:
    extends: allstarlink-transcriber
    environment:
      ALLSTARLINK_NODE: 9001
      ALLSTARLINK_HOST: node1.example.com
    ports:
      - "8001:8000"
  
  transcriber-node-2:
    extends: allstarlink-transcriber
    environment:
      ALLSTARLINK_NODE: 9002
      ALLSTARLINK_HOST: node2.example.com
    ports:
      - "8002:8000"
```

## Advanced Configuration

### Custom Themes

Edit `frontend/src/index.css` to create new themes:

```css
[data-theme="custom"] {
  --color-background: #1a1a1a;
  --color-foreground: #ffffff;
  --color-primary: #ff00ff;
  /* ... more colors ... */
}
```

Then add to theme selector in `frontend/src/context/ThemeProvider.jsx`.

### Database Management

Access SQLite database:
```bash
docker-compose exec allstarlink-transcriber sqlite3 /app/data/transcripts.db
```

Query transcripts:
```sql
SELECT timestamp, text, confidence FROM transcripts 
ORDER BY timestamp DESC LIMIT 10;
```

Export transcripts:
```bash
docker-compose exec allstarlink-transcriber \
  sqlite3 /app/data/transcripts.db \
  ".mode csv" \
  ".output /tmp/transcripts.csv" \
  "SELECT * FROM transcripts;"
```

## Development

### Project Structure
```
allstarlink-transcriber/
├── backend/
│   ├── main.py           # FastAPI application
│   └── requirements.txt   # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── App.jsx       # Main component
│   │   ├── components/   # React components
│   │   ├── context/      # Theme provider
│   │   └── index.css     # Global styles
│   ├── index.html        # HTML entry
│   ├── vite.config.js    # Build config
│   └── package.json      # NPM dependencies
├── Dockerfile            # Multi-stage build
├── docker-compose.yml    # Service configuration
├── .env.example          # Configuration template
└── README.md             # This file
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally with `docker-compose up`
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues, questions, or feature requests:
- GitHub Issues: [Report a bug](https://github.com/yourusername/allstarlink-transcriber/issues)
- Email: support@example.com

## Acknowledgments

- [AllStarLink](https://www.allstarlink.org/) - Amateur radio network
- [OpenAI Whisper](https://github.com/openai/whisper) - Speech transcription model
- [React](https://react.dev/) - UI framework
- [shadcn/ui](https://ui.shadcn.com/) - Component library
- [Tailwind CSS](https://tailwindcss.com/) - Utility-first CSS

---

**AllStarLink Transcriber v1.0.0** - Built for the amateur radio community
