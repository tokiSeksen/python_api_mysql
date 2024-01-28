CREATE TABLE IF NOT EXISTS users (
                                     id INT AUTO_INCREMENT PRIMARY KEY,
                                     username VARCHAR(50) UNIQUE NOT NULL,
                                     password VARCHAR(225) NOT NULL,
                                     subscription_type VARCHAR(50) NOT NULL,
                                     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS links (
                                     id INT AUTO_INCREMENT PRIMARY KEY,
                                     username VARCHAR(50),
                                     destination_url VARCHAR(255) NOT NULL,
                                     title VARCHAR(255),
                                     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                     CONSTRAINT fk_user FOREIGN KEY (username) REFERENCES users(username)
);