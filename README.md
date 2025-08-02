# Customer Purchases Database & Search Performance Analyzer

This project demonstrates the use of a PostgreSQL database to manage customer purchase records and analyze the performance of indexed vs. unindexed searches. It includes SQL scripts for database setup, a Python tool for interactive search and performance comparison, and sample data.

---

## Features

- **Database Setup**: SQL script to create the `customer_purchases` table and indexes.
- **Purchases Data**: CSV file containing captured purchases data.
- **Search Performance Analyzer**: Python tool to:
  - Connect to the database and fetch data.
  - Compare indexed and unindexed search performance.
  - Run binary and sequential search algorithms on in-memory data.
  - Display available data in professional tabular format using PrettyTable.
  - Interactive menu for user-driven exploration.
  - Educational summaries about database performance concepts.

---

## Project Structure

```
.
├── .example.env          # Template for environment variables
├── .gitignore
├── customer_purchases.sql # SQL script for table, indexes, and queries
├── db_operation.py        # Main Python application
├── purchases_data.csv     # Sample data for import
├── requirements.txt       # Python dependencies
├── Screenshots/           # Example screenshots
└── README.md              # Project documentation
```

---

## Getting Started

### 1. Prerequisites

- Python 3.7+
- PostgreSQL server
- Required Python packages: psycopg2-binary, python-dotenv, prettytable

### 2. Setup Database

You can set up the database using either command line tools or a GUI tool like pgAdmin.

#### Option A: Using Command Line
1. **Create the database**:
   ```sh
   createdb customer_purchases
   ```

2. **Run the SQL script** to create the table, import data, and create indexes:
   ```sh
   psql -d customer_purchases -f customer_purchases.sql
   ```

#### Option B: Using pgAdmin (GUI)
1. **Open pgAdmin** and connect to your PostgreSQL server
2. **Create a new database**:
   - Right-click on "Databases" in the left panel
   - Select "Create" → "Database..."
   - Name it `customer_purchases`
   - Click "Save"

3. **Run the SQL script**:
   - Right-click on your new database → "Query Tool"
   - Open the `customer_purchases.sql` file (File → Open)
   - Click the "Execute" button (▶️) to run the script
   - Verify tables and data were created successfully

### 3. Configure Environment Variables

1. **Create your `.env` file** by copying the example:
   ```sh
   cp .example.env .env
   ```

2. **Update `.env`** with your PostgreSQL credentials:
   ```env
   DB_HOST=localhost
   DB_NAME=customer_purchases
   DB_USER=postgres
   DB_PASSWORD=your_password_here
   DB_PORT=5432
   CSV_FILE=purchases_data.csv
   ```


### 4. Install Python Dependencies

```sh
pip install -r requirements.txt
```

**Required packages:**
- `psycopg2-binary` - PostgreSQL adapter for Python
- `python-dotenv` - Load environment variables from .env file
- `prettytable` - Create formatted tables for better data display

### 5. Run the Application

```sh
python db_operation.py
```

---

## Usage

### Interactive Menu Options

1. **Search by Customer ID** (INDEXED) - Fast search using primary key
2. **Search by Product ID** (UNINDEXED) - Slower search without index
3. **Search by Product Category** (INDEXED) - Fast search using secondary index
4. **Search by Customer Name** (UNINDEXED) - Slower search without index
5. **Search by Purchase Date** (INDEXED) - Fast search using secondary index
6. **Search by Amount** (UNINDEXED) - Slower search without index
7. **View Available Data** - Display all records in formatted tables
8. **Run Performance Tests** - Automated comparison of search methods
9. **Show Learning Summary** - Educational content about database performance


---

## Database Schema

The `customer_purchases` table includes:

| Column | Type | Index Status | Description |
|--------|------|--------------|-------------|
| customer_id | VARCHAR(10) | PRIMARY KEY | Unique customer identifier |
| customer_name | VARCHAR(100) | UNINDEXED | Customer full name |
| purchase_date | DATE | INDEXED | Date of purchase |
| product_id | VARCHAR(10) | UNINDEXED | Product identifier |
| product_category | VARCHAR(50) | INDEXED | Product category |
| amount | DECIMAL(10,2) | UNINDEXED | Purchase amount |



