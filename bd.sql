-- Crear la base de datos si no existe
CREATE DATABASE IF NOT EXISTS arepas;  
USE arepas;    

-- Crear las tablas si no existen
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    apellido VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    contrasena VARCHAR(200),
    rol TINYINT NOT NULL
);

CREATE TABLE IF NOT EXISTS menu (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(255) NOT NULL,
    descripcion TEXT NULL,
    precio INT NOT NULL,
    imagen VARCHAR(255) NOT NULL,
    categoria TINYINT NOT NULL
);
