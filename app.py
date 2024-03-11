from flask import Flask, request, jsonify, render_template
import mysql.connector
import csv
import os
import pandas as pd

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# MySQL database setup
DATABASE = {
    'user': 'root',
    'password': 'root',
    'host': '192.168.100.7', # Enter your machine IP if you installed MYSQL locally
    'port':'3306',
    'database': 'globant'
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
    try:
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
        return jsonify({'message': 'CSV files uploaded successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    #return redirect(url_for('index'))

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

# Endpoint to get the number of employees hired for each job and department in 2021 divided by quarter
@app.route('/reports-1', methods=['GET'])
def get_reports_1():
    conn = mysql.connector.connect(**DATABASE)

    # Query to get the number of employees hired for each job and department in 2021 divided by quarter
    query = '''
        with quarter_1 as (
            select department_id, job_id, count(*) as n_employees
            from globant.hired_employees
            where year(datetime) = 2021 and quarter(datetime) = 1
            group by department_id, job_id
        ), quarter_2 as (
            select department_id, job_id, count(*) as n_employees
            from globant.hired_employees
            where year(datetime) = 2021 and quarter(datetime) = 2
            group by department_id, job_id
        ),  quarter_3 as (
            select department_id, job_id, count(*) as n_employees
            from globant.hired_employees
            where year(datetime) = 2021 and quarter(datetime) = 3
            group by department_id, job_id
        ), quarter_4 as (
            select department_id, job_id, count(*) as n_employees
            from globant.hired_employees
            where year(datetime) = 2021 and quarter(datetime) = 4
            group by department_id, job_id
        )
        select d.department, j.job,
            case when q1.n_employees is null then 0 else q1.n_employees end as q1,
            case when q2.n_employees is null then 0 else q2.n_employees end as q2,
            case when q3.n_employees is null then 0 else q3.n_employees end as q3,
            case when q4.n_employees is null then 0 else q4.n_employees end as q4
        from globant.hired_employees he
        join globant.departments d on d.id = he.department_id
        join globant.jobs j on j.id = he.job_id
        left join quarter_1 q1 on (q1.department_id = he.department_id) and (q1.job_id = he.job_id)
        left join quarter_2 q2 on (q2.department_id = he.department_id) and (q2.job_id = he.job_id)
        left join quarter_3 q3 on (q3.department_id = he.department_id) and (q3.job_id = he.job_id)
        left join quarter_4 q4 on (q4.department_id = he.department_id) and (q4.job_id = he.job_id)
        where year(he.datetime) = 2021
        order by d.department, j.job;
    '''

    # Use pandas to execute the query and format the result
    df = pd.read_sql(query, conn)
    conn.close()

    return jsonify(df.to_dict(orient='records')), 200

# Endpoint to get the list of department IDs, names, and the number of employees hired
# for each department that hired more employees than the mean in 2021
@app.route('/reports-2', methods=['GET'])
def get_reports_2():
    conn = mysql.connector.connect(**DATABASE)

    # Query to get the list of department IDs, names, and the number of employees hired
    # for each department that hired more employees than the mean in 2021
    query = '''
        with employees_by_department as (
            select count(*) as hired
            from globant.hired_employees
            where year(datetime) = 2021
            group by department_id
        )
        select d.id, d.department, count(*) as hired
        from globant.hired_employees he
        join globant.departments d on he.department_id = d.id
        where year(he.datetime) = 2021
        group by d.id, d.department
        having hired > (select avg(hired) from employees_by_department)
        order by hired desc;
    '''

    # Use pandas to execute the query and format the result
    df = pd.read_sql(query, conn)
    conn.close()

    return jsonify(df.to_dict(orient='records')), 200

if __name__ == '__main__':
    create_tables()
    app.run(host="0.0.0.0", port=5000, debug=True)