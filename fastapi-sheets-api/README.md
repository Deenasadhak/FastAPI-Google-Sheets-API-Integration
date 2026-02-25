# FastAPI Google Sheets Integration

A production-ready REST API that performs CRUD operations on a Google Spreadsheet using FastAPI and the Google Sheets API via a Service Account.

## Features
- **FastAPI** web framework with Uvicorn.
- **RESTful Endpoints** capable of fetching all rows, appending a row, updating a specific row, and clearing a row.
- **Pydantic** input validation for strict data types and constraints.
- **Google Service Account** authentication avoiding physical user login flow.
- **Global exception handlers** converting application faults into structured JSON without leaking tracebacks.
- **Standardized Response Format** for both successes and errors.
- **Frontend Dashboard** served seamlessly at the root `/` endpoint to interact with Google Sheets data without tools like Postman.

## Folder Structure
```
fastapi-sheets-api/
├── app/
│   ├── main.py                # App entry point, middleware, routes
│   ├── config.py              # Environment variables & Pydantic settings
│   ├── schemas.py             # Pydantic models for data validation 
│   ├── services/
│   │   └── sheets_service.py  # Google Sheets API interaction 
│   ├── routers/
│   │   └── sheets_router.py   # API endpoints definition
│   ├── core/
│   │   └── logging_config.py  # Logger initialization
│   ├── static/
│   │   └── index.html         # Frontend Dashboard UI
│   └── utils/
│       └── helpers.py         # Standardized JSON response formatting
├── .env                       # Local environment variables
├── requirements.txt           # Project dependencies
├── README.md                  # Setup & Usage (This file)
└── walkthrough.md             # Developer explanation of the codebase
```

## Setup Instructions

### 1. Google Cloud Platform Setup 
You need a Service Account and the Google Sheets API enabled.

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project or select an existing one.
3. In the left sidebar, navigate to **APIs & Services > Library**.
4. Search for **Google Sheets API** and click **Enable**.
5. Go to **APIs & Services > Credentials**.
6. Click **Create Credentials > Service Account**.
7. Provide a name and description, then click Create.
8. No specific roles are necessary for Sheets, but you can assign "Editor" to be safe. Click Done.
9. Click heavily on your newly created Service Account email in the credentials list.
10. Navigate to the **Keys** tab -> **Add Key > Create new key**.
11. Select **JSON** and click Create. The `credentials.json` file will download. **DO NOT commit this file to Git**.

### 2. Share Spreadsheet with Service Account
1. Create a new Google Spreadsheet (e.g. at [sheets.new](https://sheets.new)).
2. Under "Share", paste the email address of your newly created Service Account (e.g., `account@project.iam.gserviceaccount.com`).
3. Grant it **Editor** permissions.
4. From your spreadsheet URL `https://docs.google.com/spreadsheets/d/your_spreadsheet_id/edit`, copy the `your_spreadsheet_id` portion. 

### 3. Local Installation
1. Clone the repository and navigate into it.
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Place the downloaded `credentials.json` directly inside the root `fastapi-sheets-api` folder.
5. Create a `.env` file in the root folder with the following keys:
   ```env
   GOOGLE_CREDENTIALS_FILE=credentials.json
   SPREADSHEET_ID=your_spreadsheet_id_here
   ```

### 4. Running Locally
Start the server using uvicorn:
```bash
uvicorn app.main:app --reload
```
The API will be available at `http://127.0.0.1:8000`.

### 5. Swagger UI Testing
FastAPI auto-generates Swagger documentation. Once running, visit:
- **Swagger Docs:** `http://127.0.0.1:8000/docs`
- **ReDoc (alternative view):** `http://127.0.0.1:8000/redoc`

Here you can visually test GET, POST, PUT, DELETE operations.

### 6. Frontend UI Dashboard
Visit `http://127.0.0.1:8000` directly in your browser to access the sleek "SheetSync" frontend interface, which will allow you to read, append, update, and clear rows visually.

---

## Deployment on Render.com

Render natively supports deploying from a Git repository via Web Services.

1. Push your code to a private GitHub/GitLab repository. Do NOT commit the `credentials.json` or `.env` files.
2. Go to [Render Dashboard](https://dashboard.render.com/) and create a new **Web Service**.
3. Connect your repository.
4. Set the necessary environment configurations:
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. In the **Environment Variables** section on Render, add:
   - `SPREADSHEET_ID` = `your_spreadsheet_id`
   - For `GOOGLE_CREDENTIALS_FILE`: 
     - Option A: Create a Secret File on Render named `credentials.json`, paste your JSON contents into it, and point the `GOOGLE_CREDENTIALS_FILE` Environment Variable to its path (often `/etc/secrets/credentials.json`).
6. Click **Deploy**. Your service will be live!
