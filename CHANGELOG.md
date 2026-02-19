# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-02-19

### Added
- Initial release of AllStarLink Transcriber
- Real-time audio transcription from AllStarLink 3.0 nodes
- iaxclient integration with IAX2 protocol support
- OpenAI Whisper integration (small model for CPU-friendly transcription)
- WebSocket real-time streaming to web frontend
- Modern React web interface with three themes (Light, Dark, High Contrast)
- FastAPI backend with REST API endpoints
- SQLite database support for transcript persistence
- Docker containerization with Alpine Linux base image
- Environment-based configuration system
- Comprehensive documentation and guides
- GitHub Actions CI/CD pipeline
- Contributing guidelines
- Issue and PR templates

### Features
- Real-time audio capture from AllStarLink nodes
- 10-second audio chunk processing for optimal latency
- Live transcript streaming via WebSocket
- Confidence score calculation for transcriptions
- Theme switching at runtime
- Auto-scrolling transcript display
- Connection status monitoring
- Health checks and auto-restart
- Multi-node deployment support
- Production deployment guide with Nginx/SSL

### Performance
- ~600MB Docker image size
- 10-15 second startup time
- 5-10 second transcription latency per 10-second chunk
- 10-15 minute first build, 2-5 minutes for cached builds

### Documentation
- Complete README with features, setup, and API reference
- Quick Start guide for 5-minute deployment
- Production Deployment guide with Nginx/SSL configuration
- Automated Deployment guide explaining all automation
- Contributing guidelines for open source development
- Inline code comments and docstrings

## [Unreleased]

### Planned Features
- PostgreSQL backend option for multi-instance deployment
- GPU acceleration support (CUDA for faster transcription)
- Message queue support (Redis/RabbitMQ) for scaling
- Authentication and authorization layer
- Webhook support for external integrations
- Sentiment analysis on transcriptions
- Speaker identification
- Custom Whisper model support
- Multi-language support
- API rate limiting and throttling
- Advanced search in transcript archive
- Export to various formats (PDF, CSV, JSON)
- Integration with Slack, Discord, email
- Docker Swarm and Kubernetes templates

---

## Version History

### [1.0.0] - 2026-02-19
Initial production release with all core features.

---

## Upgrade Guide

### From v0.x to v1.0.0
Complete rewrite - this is the initial release.

---

## Security

For security vulnerabilities, please email security@example.com instead of using the issue tracker.

---

## Contributors

See [CONTRIBUTORS.md](CONTRIBUTORS.md) for a list of contributors to this project.

---

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.
