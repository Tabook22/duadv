# Dhofar University Student Management System

A web application for university supervisors to manage student transcripts and study plans.

## ⚠️ Important Notice

This application is for authorized university personnel only. Ensure you have proper authorization from your IT department before accessing student data.

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

3. **Run Application**
   ```bash
   python app.py
   ```

4. **Access Application**
   Open http://localhost:5000 in your browser

## Features

- University system integration
- Student list management
- Transcript viewing
- Study plan tracking
- Secure authentication
- Responsive design

## Configuration

Update the selectors in `app/scraper/selectors.py` based on your university's actual web interface.

## Security

- Always use HTTPS in production
- Keep credentials secure
- Regular security updates
- Audit access logs

## Support

For technical support or questions about this system, contact your IT department.
