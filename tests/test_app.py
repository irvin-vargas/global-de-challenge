import pytest
import requests
import os
import mysql.connector

API_URL = "http://127.0.0.1:5000"
RESOURCE_FOLDER = "tests/test_csv"
DATABASE = {
    'user': 'root',
    'password': 'root',
    'host': '192.168.100.7', # Enter your machine IP if you installed MYSQL locally
    'port':'3306',
    'database': 'globant'
}

def test_home():
    response = requests.get(API_URL)
    assert response.status_code == 200

def test_upload_csv():
    # Prepare test CSV files
    departments_csv = open(os.path.join(RESOURCE_FOLDER, "test_departments.csv"), "rb")
    jobs_csv = open(os.path.join(RESOURCE_FOLDER, "test_jobs.csv"), "rb")
    hired_employees_csv = open(os.path.join(RESOURCE_FOLDER, "test_hired_employees.csv"), "rb")

    # Create a dictionary with files to upload
    files = {
        "departments": departments_csv,
        "jobs": jobs_csv,
        "hired_employees": hired_employees_csv
    }

    # Make a POST request to the endpoint
    response = requests.post(API_URL, files=files)
    #print(response.json().get("error"))

    # Check if the status code is 200 and the response content indicates success
    assert response.status_code == 200
    assert response.json().get("message") == "CSV files uploaded successfully"

    # Close the file handles
    departments_csv.close()
    jobs_csv.close()
    hired_employees_csv.close()

    # Delete the files
    delete_file("test_departments.csv")
    delete_file("test_jobs.csv")
    delete_file("test_hired_employees.csv")

    # Delete the test registers of the BD
    conn = mysql.connector.connect(**DATABASE)
    cursor = conn.cursor()
    try:
        cursor.execute("delete from globant.hired_employees WHERE id in (-1,-2)")
        cursor.execute("delete from globant.jobs WHERE id in (-1,-2)")
        cursor.execute("delete from globant.departments WHERE id in (-1,-2)")
        conn.commit()
        #print(f"Test records deleted successfully.")
    except Exception as e:
        print(f"Error deleting test records")
    finally:
        conn.close()

def delete_file(file_name):
    file_path = os.path.join('uploads', file_name)
    try:
        # Check if the file exists before attempting to delete
        if os.path.exists(file_path):
            os.remove(file_path)
            #print(f"File '{file_name}' deleted successfully.")
        else:
            print(f"File '{file_name}' not found in the specified folder.")
    except Exception as e:
        print(f"Error deleting file: {e}")

def test_get_reports_1():
    response = requests.get(f"{API_URL}/reports-1")
    assert response.status_code == 200
    data = response.json()
    #print(data)
    assert isinstance(data, list)

def test_get_reports_2():
    response = requests.get(f"{API_URL}/reports-2")
    assert response.status_code == 200
    data = response.json()
    #print(data)
    assert isinstance(data, list)

if __name__ == "__main__":
    pytest.main(["-v","-s"])