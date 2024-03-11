# global-de-challenge
Coding Challenge, use of APIs and endpoints for queries

# Flask Application

This is a Flask application that provides APIs for uploading CSV files and inserting data into a MySQL database.

## Features

- **Upload CSV files and insert into MYSQL database**: The `/` endpoint accepts 3 CSV files ('hired_employees.csv', 'departments.csv' and 'jobs.csv'), reads the data, and inserts it into their respective MySQL table.
- **Reports Endpoints**: The application includes some endpoints (`/reports-1`, and `/reports-2`) that execute SQL queries on the MySQL database to retrieve some metrics related to the 'hired_employees', 'departments', and 'jobs' tables.

## Installation

1. Clone this repository.
2. Install the required Python packages: `pip install -r requirements.txt`
3. Run the Flask application: `python app/app.py`

## Testing

Automated tests for the `upload` and `reports` endpoints are included in the `tests/test_app.py` file. You can run the tests using pytest: `python app/tests/test_app.py`

The tests include:

- Uploading CSV files for 'departments', 'jobs', and 'hired_employees' and batch inserting data into 'departments', 'jobs', and 'hired_employees'.
- Retrieving metrics in JSON format.
- Retrieving metrics in CSV format.
