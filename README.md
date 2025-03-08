# Airtasker Automation Bot

A Flask-based web application for automating interactions with Airtasker, including login, task scraping, and commenting.

## Features

- Automated login with captcha solving
- Task scraping based on location
- Automated commenting on tasks
- Browser stealth mode to avoid detection
- Works locally and in cloud environments (GCP)

## Local Development Setup

### Prerequisites

- Python 3.9+
- Chrome browser installed
- Capsolver API key (for captcha solving)

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/Jogenius22/AutomationFlask-Playwright.git
   cd AutomationFlask-Playwright
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:

   ```bash
   cp .env.example .env
   ```

   Edit `.env` file and add your configuration.

5. Run the application:
   ```bash
   python run.py
   ```
   The application will be available at http://localhost:5001

## GCP Deployment

### Using Google App Engine

1. Install the Google Cloud SDK if you haven't already.

2. Make sure you've set the environment variable in your `.env` file:

   ```
   CLOUD_ENV=true
   ```

3. Deploy to App Engine:
   ```bash
   gcloud app deploy
   ```

### Using Google Cloud Run with Docker

1. Build the Docker image:

   ```bash
   gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/airtasker-bot
   ```

2. Deploy to Cloud Run:
   ```bash
   gcloud run deploy airtasker-bot \
     --image gcr.io/YOUR_PROJECT_ID/airtasker-bot \
     --platform managed \
     --allow-unauthenticated \
     --set-env-vars="CLOUD_ENV=true,CAPSOLVER_API_KEY=your-api-key"
   ```

## Project Structure

- `app/`: The main Flask application
  - `automations/`: Contains automation scripts
    - `main.py`: Main automation logic
    - `comments.py`: Comment handling logic
  - `templates/`: HTML templates
  - `static/`: Static assets
- `run.py`: Application entry point
- `Dockerfile`: For containerized deployment
- `app.yaml`: Google App Engine configuration

## Environment Variables

- `SECRET_KEY`: Flask secret key
- `FLASK_APP`: Flask application entry point
- `FLASK_ENV`: Flask environment (development/production)
- `CAPSOLVER_API_KEY`: API key for the Capsolver service
- `CLOUD_ENV`: Set to 'true' when deploying to cloud environments

## Troubleshooting

- **Captcha Issues**: Ensure your Capsolver API key is valid and has sufficient balance
- **Browser Issues**: If the browser doesn't start properly in GCP, check logs for Chrome-related errors
- **Performance Issues**: Increase instance size in app.yaml for better performance

## Switching to Playwright (Future)

This project may be updated to use Playwright instead of Selenium in the future for better reliability in containerized environments. The repository name reflects this potential future direction.

## License

Private - Not for redistribution
