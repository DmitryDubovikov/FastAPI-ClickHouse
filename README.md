# Animal Visit Tracker

## Project Overview

The Animal Visit Tracker is a FastAPI application designed to record animal visits made by visitors. It allows users to add visit records, including visitor ID, animal type, and visit time. The application serves as a demonstration of FastAPI's capabilities. Additionally, it leverages **ClickHouse**, a columnar database management system designed for online analytical processing (OLAP), to efficiently store and query visit records.


## Technologies Used

- **FastAPI**
- **ClickHouse**


## Installation and Run

   ```bash
   git clone https://github.com/yourusername/animal-visit-tracker.git
   cd animal-visit-tracker
   ```

   ```bash
    docker compose build
    docker compose up -d
   ```

The application will be available at [http://localhost:8000](http://localhost:8000).

### Accessing the API Documentation

You can view the interactive API documentation provided by Swagger UI by navigating to:

- [http://localhost:8000/docs](http://localhost:8000/docs)

## API Endpoints

### 1. Record a Visit
- **POST** `/visit/`
  - Records a visit to an animal.

### 2. Animal Popularity Analytics
- **GET** `/analytics/popularity/`
  - Retrieves animal popularity based on visits in the last 24 hours.

### 3. Peak Visit Hours Analytics
- **GET** `/analytics/peak_hours/`
  - Retrieves peak hours for animal visits in the last 24 hours.

### 4. Add Random Visits
- **POST** `/add_random_visits/`
  - Generates and records random animal visits.