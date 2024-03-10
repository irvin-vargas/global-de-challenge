from flask import Flask, request, jsonify, render_template, redirect, url_for
import mysql.connector
import csv
from io import StringIO
import os

app = Flask(__name__)
app.config['DEBUG'] = True

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# MySQL database setup
DATABASE = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'globant',
}

def create_tables():
    conn = mysql.connector.connect(**DATABASE)
    cursor = conn.cursor()

    # Create tables if they don't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS departments (
            id INT,
            department VARCHAR(255),
            PRIMARY KEY (id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INT,
            job VARCHAR(255),
            PRIMARY KEY (id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hired_employees (
            id INT,
            name VARCHAR(255),
            datetime VARCHAR(255),
            department_id INT NULL,
            job_id INT NULL,
            PRIMARY KEY (id),
            FOREIGN KEY (department_id) REFERENCES departments (id),
            FOREIGN KEY (job_id) REFERENCES jobs (id)
        )
    ''')

    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

# Endpoint to receive and process historical data from CSV files
@app.route('/', methods=['POST'])
def upload_csv():
    # Assuming CSV files are sent as form data with keys: departments, jobs, employees
    departments_csv = request.files['departments']
    jobs_csv = request.files['jobs']
    hired_employees_csv = request.files['hired_employees']

    if departments_csv.filename != '':
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], departments_csv.filename)
        departments_csv.save(file_path)
        process_csv(file_path, 'departments')
    if jobs_csv.filename != '':
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], jobs_csv.filename)
        jobs_csv.save(file_path)
        process_csv(file_path, 'jobs')
    if hired_employees_csv.filename != '':
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], hired_employees_csv.filename)
        hired_employees_csv.save(file_path)
        process_csv(file_path, 'hired_employees')
    
    return redirect(url_for('index'))

def process_csv(file_path, table_name):
    # Read CSV file and insert data into the corresponding table
    with open(file_path, encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file)

        conn = mysql.connector.connect(**DATABASE)
        cursor = conn.cursor()

        # Insert data into the database in batches
        batch_size = 1000
        rows = []
        for row in csv_reader:
            # Transform the empty registers in NULL
            if table_name == 'hired_employees':
                if row[3] == '':
                    row[3] = None
                if row[4] == '':
                    row[4] = None

            #print(row, flush=True)
            rows.append(tuple(row))        
            if len(rows) == batch_size:
                if table_name == 'departments':
                    cursor.executemany(f'INSERT INTO globant.departments (id, department) VALUES (%s, %s)', rows)
                if table_name == 'jobs':
                    cursor.executemany(f'INSERT INTO globant.jobs (id, job) VALUES (%s, %s)', rows)
                if table_name == 'hired_employees':
                    cursor.executemany(f'INSERT INTO globant.hired_employees (id, name, datetime, department_id, job_id) VALUES (%s, %s, %s, %s, %s)', rows)
                rows = []

        # Insert any remaining rows
        if rows:
            if table_name == 'departments':
                cursor.executemany(f'INSERT INTO globant.departments (id, department) VALUES (%s, %s)', rows)
            if table_name == 'jobs':
                cursor.executemany(f'INSERT INTO globant.jobs (id, job) VALUES (%s, %s)', rows)
            if table_name == 'hired_employees':
                cursor.executemany(f'INSERT INTO globant.hired_employees (id, name, datetime, department_id, job_id) VALUES (%s, %s, %s, %s, %s)', rows)

        conn.commit()
        conn.close()

if __name__ == '__main__':
    create_tables()
    app.run(port=5000)