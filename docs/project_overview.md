# Project Overview

## Purpose
This project provides a FastAPI-based integration with DTech's External Sales API, allowing for seamless sales process management and call recording uploads. It's designed to be secure, scalable, and easy to maintain.

## Technical Stack
- **Backend**: FastAPI (Python 3.11+)
- **Authentication**: AWS Signature V4 + Appwrite
- **Database**: Appwrite
- **Session Management**: Redis/In-memory
- **Container**: Docker
- **Frontend**: HTML + CSS (Tailwind-like custom styles)

## Key Components

### 1. DTech Integration
- AWS Signature V4 authentication
- Sales process management
- Call recording handling
- Real-time status updates

### 2. Data Storage
- Sales processes tracking
- Recording metadata
- User sessions
- Audit logs

### 3. Security
- Secure session management
- AWS request signing
- Input validation
- CORS protection

### 4. User Interface
- Modern, responsive design
- Real-time progress tracking
- Form validation
- Error feedback

## Development Guidelines

### Code Style
- Follow PEP 8
- Use type hints
- Document all functions
- Keep functions small and focused

### Testing
- Write unit tests for new features
- Maintain 80%+ coverage
- Test error conditions
- Mock external services

### Security
- Never commit credentials
- Validate all inputs
- Use HTTPS in production
- Follow security best practices

### Deployment
- Use Docker for consistency
- Maintain separate prod/dev configs
- Monitor logs and metrics
- Regular security updates
