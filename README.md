# edYOU Housing Web App 🏠

A full-stack Flask web application that allows users to post, browse, and favorite college housing listings.

## Features

- 🏡 Post and browse housing listings with images
- 🔍 Filter by location, rent range, and tags
- ❤️ Favorite/unfavorite listings with heart icon (like Zillow)
- 👤 User authentication (register/login/logout)
- 🔒 Secure with CSRF protection and Flask-Login
- 📦 SQLite + SQLAlchemy ORM for database
- 🎨 Styled with Tailwind CSS

## Screenshots

> Add some screenshots or a demo GIF here to show off your UI.

## Setup Instructions

```bash
# 1. Clone the repository
git clone https://github.com/emmanueladima/housing-app.git
cd housing-app

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the Flask application
python run.py

# Now open your browser and visit:
# http://127.0.0.1:5000/
