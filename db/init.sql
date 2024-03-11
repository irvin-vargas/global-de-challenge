CREATE DATABASE IF NOT EXISTS globant;
USE globant;

CREATE TABLE IF NOT EXISTS departments (
    id INT,
    department VARCHAR(255),
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS jobs (
    id INT,
    job VARCHAR(255),
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS hired_employees (
    id INT,
    name VARCHAR(255),
    datetime VARCHAR(255),
    department_id INT NULL,
    job_id INT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (department_id) REFERENCES departments (id),
    FOREIGN KEY (job_id) REFERENCES jobs (id)
);