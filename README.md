# Universal Auto-ETL Analytics Platform

This project provides an automated Extract, Transform, and Load (ETL) data pipeline coupled with a real-time responsive web dashboard. It accepts generic CSV datasets, dynamically infers schema structures, calculates multidimensional metrics, and serves the results through a FastAPI backend to a React frontend.

## Architecture

* Backend: Python 3.10, FastAPI, Pandas, Great Expectations.
* Frontend: Node.js, React, Vite, Recharts, Vanilla CSS (Glassmorphism).
* Pipeline: Automated data parsing, type-inference, cleaning, and dual-axis aggregation (Entity totals and Time-Series progression).

## Local Execution

### Prerequisites
* Python 3.10+
* Node.js 18+

### Initialization
1. Create and activate a virtual environment in the project root:
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate

2. Install backend dependencies:
   pip install -r requirements.txt

3. Install frontend dependencies:
   cd frontend
   npm install

### Running the Services
To run both the backend and frontend simultaneously on Windows, execute the provided batch script:
   .\run_dashboard.bat

Alternatively, run them separately:
* Backend: `cd api && uvicorn main:app --reload`
* Frontend: `cd frontend && npm run dev`

Access the application via http://localhost:5173.

## Docker Deployment

A multi-stage Dockerfile is included to containerize and serve both the Python backend API and the compiled React frontend simultaneously.

1. Build the Docker image:
   docker build -t auto-etl-platform .

2. Run the Docker container:
   docker run -d -p 8000:8000 -p 5173:5173 --name etl-dashboard auto-etl-platform

3. Access the deployed application bounds remotely via port 5173 or locally at http://localhost:5173.

## Power BI Integration

The platform provides a direct sync endpoint for Power BI:
1. In Power BI Desktop, go to **Get Data** -> **Web**.
2. Paste the following URL: `http://localhost:8000/api/pbi` (or click the Link icon in the dashboard header).
3. Power BI will automatically detect the schema and allow you to build custom reports that update whenever the ETL pipeline runs.

