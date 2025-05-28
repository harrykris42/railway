CREATE DATABASE IF NOT EXISTS railway;
USE railway;

CREATE TABLE IF NOT EXISTS user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS train (
    id INT AUTO_INCREMENT PRIMARY KEY,
    train_name VARCHAR(100) NOT NULL,
    from_station VARCHAR(100) NOT NULL,
    to_station VARCHAR(100) NOT NULL,
    total_seats INT NOT NULL,
    available_seats INT NOT NULL,
    date DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS booking (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    train_id INT NOT NULL,
    seats_booked INT NOT NULL,
    booked_on DATETIME DEFAULT CURRENT_TIMESTAMP,
    travel_date DATE NOT NULL,
    ticket_id VARCHAR(10) NOT NULL UNIQUE,
    FOREIGN KEY (user_id) REFERENCES user(id),
    FOREIGN KEY (train_id) REFERENCES train(id)
);

-- Insert default admin user (bcrypt-hashed password for 'admin')
INSERT IGNORE INTO user (name, password, is_admin)
VALUES (
  'admin',
  '$2b$12$Yq/tiPLqzI53rTBm44x0o.HCSN1RUv1Eq68Z1xfifnwDz2bdVh.BW',
  TRUE
);
