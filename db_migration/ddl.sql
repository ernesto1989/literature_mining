-- a) Registro de las consultas realizadas
CREATE TABLE query_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    log_id VARCHAR(8) UNIQUE NOT NULL,
    fecha_consulta DATETIME,
    keywords TEXT,
    start_year INT,
    end_year INT,
    total_resultados INT,
    query_text TEXT
);

-- b) Detalles de los papers (Evitamos duplicados con PRIMARY KEY en eid)
CREATE TABLE query_details (
    eid VARCHAR(50) PRIMARY KEY,
    title TEXT NOT NULL,
    citations INT DEFAULT 0,
    url TEXT
);

-- c) Catálogo de autores (Únicos por author_id)
CREATE TABLE authors (
    author_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

-- d) Relación Muchos-a-Muchos entre Papers y Autores
CREATE TABLE paper_authors (
    eid VARCHAR(50),
    author_id VARCHAR(50),
    PRIMARY KEY (eid, author_id),
    FOREIGN KEY (eid) REFERENCES query_details(eid) ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES authors(author_id) ON DELETE CASCADE
);