# Web Application

This directory contains the Flask web application for the Healthcare Data QA platform.

## Components

### Main Application (`app.py`)
- Flask application setup
- Route definitions
- Database connections
- API endpoints
- Error handling

### Dashboard (`dashboard.py`)
- Data visualization
- Quality metrics display
- Interactive charts
- Real-time updates

### Templates
Located in `templates/` directory:
- `base.html`: Base template with common layout
- `index.html`: Main dashboard view
- `tables.html`: Database tables overview
- `quality.html`: Quality check results
- `api_docs.html`: API documentation
- `error.html`: Error page template

## Features

### Data Visualization
- Interactive charts using Chart.js
- Table distribution visualization
- Quality metrics trends
- Regional data analysis

### Quality Check Interface
- Run quality checks
- View check results
- Track issues
- Export reports

### Database Management
- Table overview
- Record counts
- Schema information
- Data previews

### API Documentation
- Interactive API documentation
- Request/response examples
- Authentication details
- Error codes

## Configuration

Application settings in `.env`:
```
WEB_HOST=localhost
WEB_PORT=5001
DEBUG=True
```

## Running the Application

1. Start the Flask server:
```bash
python3 src/web/app.py
```

2. Access the application:
- Main dashboard: http://localhost:5001
- Quality checks: http://localhost:5001/quality
- API docs: http://localhost:5001/api-docs

## Development

### Adding New Routes
1. Define route in `app.py`
2. Create template in `templates/`
3. Add navigation link in `base.html`
4. Update documentation

### Template Structure
- Use `base.html` for common elements
- Extend with `{% extends "base.html" %}`
- Override blocks as needed
- Keep logic in route handlers