-- Initial database schema migration
-- Created: 2025-12-04

CREATE TABLE IF NOT EXISTS stores (
  id SERIAL PRIMARY KEY,
  name TEXT,
  address TEXT,
  created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS cameras (
  id SERIAL PRIMARY KEY,
  store_id INTEGER REFERENCES stores(id),
  name TEXT,
  rtsp_url TEXT,
  location TEXT,
  created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE IF NOT EXISTS employees (
  id SERIAL PRIMARY KEY,
  emp_code TEXT UNIQUE NOT NULL,
  name TEXT,
  role TEXT,
  created_at TIMESTAMP DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_employees_emp_code ON employees(emp_code);

CREATE TABLE IF NOT EXISTS face_embeddings (
  id SERIAL PRIMARY KEY,
  employee_id INTEGER REFERENCES employees(id) ON DELETE CASCADE,
  embedding FLOAT8[],
  created_at TIMESTAMP DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_face_embeddings_employee_id ON face_embeddings(employee_id);

CREATE TABLE IF NOT EXISTS schedules (
  id SERIAL PRIMARY KEY,
  employee_id INTEGER REFERENCES employees(id) ON DELETE CASCADE,
  date DATE,
  shift_start TIMESTAMP,
  shift_end TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_schedules_employee_id ON schedules(employee_id);
CREATE INDEX IF NOT EXISTS idx_schedules_date ON schedules(date);

CREATE TABLE IF NOT EXISTS attendance_logs (
  id SERIAL PRIMARY KEY,
  employee_id INTEGER REFERENCES employees(id) ON DELETE CASCADE,
  timestamp TIMESTAMP DEFAULT now(),
  camera_id INTEGER REFERENCES cameras(id),
  confidence FLOAT,
  snapshot_url TEXT
);

CREATE INDEX IF NOT EXISTS idx_attendance_logs_employee_id ON attendance_logs(employee_id);
CREATE INDEX IF NOT EXISTS idx_attendance_logs_timestamp ON attendance_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_attendance_logs_camera_id ON attendance_logs(camera_id);

CREATE TABLE IF NOT EXISTS environment_logs (
  id SERIAL PRIMARY KEY,
  camera_id INTEGER REFERENCES cameras(id) ON DELETE CASCADE,
  timestamp TIMESTAMP DEFAULT now(),
  people_count INTEGER,
  brightness FLOAT
);

CREATE INDEX IF NOT EXISTS idx_environment_logs_camera_id ON environment_logs(camera_id);
CREATE INDEX IF NOT EXISTS idx_environment_logs_timestamp ON environment_logs(timestamp);

