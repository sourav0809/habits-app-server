# Habits Tracker API

This is the backend API for the Habits Tracker application, built with FastAPI and MongoDB.

## Getting Started

1. Set up your virtual environment and install dependencies:
   ```bash
   make install
   ```

2. Configure environment variables:
   - Copy `.env.example` to `.env`
   - Fill in your MongoDB connection string (`MONGODB_URL`), secret key (`JWT_SECRET`), and other configuration details.

3. Run the development server:
   ```bash
   make dev
   ```

The API runs on `http://127.0.0.1:8000` by default. You can view the automatically generated interactive API documentation (Swagger UI) at `http://127.0.0.1:8000/docs`.
