# Library Management System - Instructions

## Prerequisites

- Node.js (v18 or later)
- Docker and Docker Compose
- npm or yarn
- Python 3.10+ and pip

## Setup and Running the Application

### 1. Clone the repository

```bash
git clone <repository-url>
cd library-management-system
```

### 2. Install frontend dependencies

```bash
npm install
```

### 3. Set up environment variables

Create a `.env.local` file with the following content:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=library_db
JWT_SECRET=your-super-secret-key-change-this-in-production
JWT_EXPIRY=24h
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

### 4. Start the PostgreSQL database

```bash
docker-compose up -d
```

### 5. Initialize the database with sample data

```bash
npm run init-db
```

### 6. Set up Python virtual environment and install backend dependencies

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 7. Initialize backend database tables

```bash
python create_tables.py
```

### 8. Import datasets

Run the import script to load datasets into the database:

```bash
python scripts/import_books_and_users.py
```

Make sure the dataset files are located at:

- `C:\Users\admin\Documents\Summer Project\Datasets\book1-100k.csv`
- `C:\Users\admin\Documents\Summer Project\Datasets\book_borrow_history.csv`

### 9. Start the Flask backend API server

```bash
flask run
```

### 10. Start the Next.js frontend development server

```bash
npm run dev
```

### 11. Access the application

Open your browser and navigate to:

```
http://localhost:8000
```

## Default Users

### Admin

- Username: admin
- Password: admin123

### Students

- Username: student1
- Password: student123
- Username: student2
- Password: student123

## Additional Notes

- The backend uses SQLite for testing but connects to PostgreSQL in production.
- The book recommendation engine and search functionality are integrated into the student portal.
- CSS styles for the student portal are located in `public/student_portal.css`.

## Troubleshooting

- If you encounter database errors, ensure the database tables are created by running `python create_tables.py`.
- For dataset import issues, verify the CSV file paths and contents.

---

