# Smallville City Hall AI Assistant

## Overview

This is a Flask-based web application that serves as an AI assistant for Smallville City Hall. The application provides a user-friendly interface where citizens can ask questions about city services, permits, regulations, and general information. The system integrates with the Nuclia API to provide intelligent responses to user queries.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Technology**: Vanilla JavaScript with Bootstrap 5 for styling
- **Structure**: Single-page application with client-side JavaScript handling user interactions
- **UI Framework**: Bootstrap 5 for responsive design and Font Awesome for icons
- **Approach**: Server-side rendered HTML templates with client-side dynamic behavior

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Structure**: Simple MVC pattern with route handlers and template rendering
- **API Design**: RESTful endpoint for question processing
- **Session Management**: Flask sessions with configurable secret key

### External Service Integration
- **Nuclia API**: Primary AI service for processing user questions and generating responses
- **Configuration**: Environment-based API key and base URL configuration
- **Request Handling**: Synchronous HTTP requests using the `requests` library

## Key Components

### Application Structure
```
app.py          # Main Flask application with routes and API integration
main.py         # Application entry point
templates/      # HTML templates (Jinja2)
static/         # Static assets (CSS, JavaScript)
```

### Core Routes
- `GET /`: Serves the main application interface
- `POST /api/ask`: Handles question submissions to the Nuclia API

### Frontend Components
- **CityHallAssistant Class**: JavaScript class managing user interactions
- **Search Interface**: Input form with submit handling and validation
- **Response Display**: Dynamic content rendering for AI responses
- **Error Handling**: User-friendly error messages and retry functionality

## Data Flow

1. **User Input**: User submits a question through the web interface
2. **Client Validation**: JavaScript validates input before submission
3. **API Request**: Frontend sends POST request to `/api/ask` endpoint
4. **External API Call**: Flask backend forwards question to Nuclia API
5. **Response Processing**: Backend processes Nuclia API response
6. **Client Update**: Frontend receives response and updates UI accordingly

## External Dependencies

### Third-Party Services
- **Nuclia API**: AI-powered question answering service
  - Requires API key authentication
  - Provides context and metadata with responses
  - Configurable base URL for different environments

### Frontend Libraries
- **Bootstrap 5**: CSS framework for responsive design
- **Font Awesome**: Icon library for UI elements

### Python Packages
- **Flask**: Web framework
- **Flask-CORS**: Cross-origin resource sharing support
- **requests**: HTTP client for external API calls

## Deployment Strategy

### Replit Deployment
- Use the built-in "Deploy" button for easy Replit deployment
- Environment variables are automatically configured

### Render.com Deployment
- **Configuration**: Uses `render.yaml` for service configuration
- **Dependencies**: Listed in `render_requirements.txt`
- **Build Command**: `pip install -r render_requirements.txt`
- **Start Command**: `gunicorn --bind 0.0.0.0:$PORT main:app`
- **Port Configuration**: Uses dynamic `PORT` environment variable from Render

### Environment Configuration
- **Session Secret**: Configurable via `SESSION_SECRET` environment variable
- **Nuclia API Key**: Required via `NUCLIA_API_KEY` environment variable
- **Nuclia Base URL**: Configurable via `NUCLIA_BASE_URL` environment variable

### Runtime Settings
- **Host**: Configured to bind to all interfaces (0.0.0.0)
- **Port**: Dynamic port from environment (Heroku) or defaults to 5000
- **Debug Mode**: Disabled for production deployment

### Security Considerations
- CORS enabled for cross-origin requests
- Environment-based secret management
- Input validation on both client and server sides

### Scalability Notes
- Simple single-threaded Flask application
- Synchronous API calls to external services
- No database persistence required
- Stateless design suitable for horizontal scaling