# Quick Start Guide

Get AllStarLink Transcriber running in 5 minutes - completely automated.

## Step 1: Clone and Setup

```bash
git clone <repo-url> allstarlink-transcriber
cd allstarlink-transcriber
cp .env.example .env
```

## Step 2: Configure AllStarLink Connection

Edit `.env` with your node details:

```bash
nano .env
```

**Critical settings:**
```
ALLSTARLINK_NODE=9001              # Your node number
ALLSTARLINK_HOST=192.168.1.100     # Node IP or hostname
ALLSTARLINK_PORT=4569              # Usually 4569
ALLSTARLINK_USER=guest             # Your username
ALLSTARLINK_PASSWORD=guest         # Your password
```

## Step 3: Build and Deploy

```bash
# Build the image (automatically compiles iaxclient from source)
docker-compose build

# Start the service
docker-compose up -d
```

The Docker build automatically handles everything:
- ✅ Clones iaxclient from GitHub
- ✅ Compiles iaxclient with audio support
- ✅ Builds React frontend
- ✅ Installs all dependencies
- ✅ Downloads Whisper model
- ✅ Creates optimized Alpine image

**Build time**: 10-15 minutes (first time only)

Check progress:
```bash
docker-compose logs -f
```

## Step 4: Open Web Interface

```
http://localhost:8000
```

Click "Start Recording" to begin transcription.

## Verification

Check service is running:
```bash
docker-compose ps
```

Should show:
```
NAME                     STATUS
allstarlink-transcriber  Up X seconds
```

Test API endpoint:
```bash
curl http://localhost:8000/api/status
```

## Troubleshooting

### Build fails
```bash
docker-compose build --progress=plain
```

### Service won't start
```bash
docker-compose logs -f
```

### Can't connect to node
- Verify IP/hostname: `ping ALLSTARLINK_HOST`
- Check credentials in `.env`
- Ensure firewall allows port 4569

### No transcripts appearing
- Check audio levels on the node
- Wait 10+ seconds (Whisper needs time to process)
- View logs: `docker-compose logs -f`

## Done!

No additional steps needed. Your AllStarLink Transcriber is fully operational.

## Next Steps

- Read [README.md](README.md) for complete documentation
- See [AUTOMATED_DEPLOYMENT.md](AUTOMATED_DEPLOYMENT.md) for automation details
- Check [DEPLOYMENT.md](DEPLOYMENT.md) for production setup
- Review [API Documentation](#rest-api) in README for programmatic access
