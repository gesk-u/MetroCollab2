-- ===================================
-- MetroCollab Database Schema
-- ===================================
-- Database: Collab_DB
-- Description: Student team matching system database structure

-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS Collab_DB;
USE Collab_DB;

-- ===================================
-- Users Table
-- ===================================
-- Stores both students and teachers
CREATE TABLE users
(
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_firstname VARCHAR(40) NOT NULL,
    user_lastname VARCHAR(40) NOT NULL,
    user_type TINYINT(1) NOT NULL  -- 0 = student, 1 = teacher
);

-- ===================================
-- Teacher Group Table
-- ===================================
-- Stores teacher's group configuration
CREATE TABLE teacher_group
(
    id INT AUTO_INCREMENT PRIMARY KEY,
    teacher_id INT NOT NULL,
    total_students INT NOT NULL,
    min_students_per_group INT NOT NULL,
    max_students_per_group INT NOT NULL,
    group_code TEXT UNIQUE,
    FOREIGN KEY (teacher_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ===================================
-- Student Group Table
-- ===================================
-- Links students to groups and stores their assigned group number
CREATE TABLE student_group
(
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    group_code VARCHAR(10), 
    group_number INT NULL,   
    FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_student_group (student_id, group_code)  -- Prevent duplicate entries
);

-- ===================================
-- Skills Table
-- ===================================
-- Library of all skills
CREATE TABLE skills
(
    id INT AUTO_INCREMENT PRIMARY KEY,
    name TEXT NOT NULL
);

-- ===================================
-- Interests Table
-- ===================================
-- Library of all interests
CREATE TABLE interests
(
    id INT AUTO_INCREMENT PRIMARY KEY,
    name TEXT NOT NULL
);

-- ===================================
-- Student Skills Table
-- ===================================
-- Many-to-many relationship between students and skills
CREATE TABLE student_skills
(
    user_id INT NOT NULL,
    skill_id INT NOT NULL,
    PRIMARY KEY (user_id, skill_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE
);

-- ===================================
-- Student Interests Table
-- ===================================
-- Many-to-many relationship between students and interests
CREATE TABLE student_interests
(
    user_id INT NOT NULL,
    interest_id INT NOT NULL,
    PRIMARY KEY (user_id, interest_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (interest_id) REFERENCES interests(id) ON DELETE CASCADE
);

-- ===================================
-- Student Form Table
-- ===================================
-- Stores student form submissions with JSON data for clustering algorithm
CREATE TABLE student_form
(
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    email VARCHAR(255),
    skills JSON CHECK (JSON_VALID(skills)),           
    interests JSON CHECK (JSON_VALID(interests)),    
    availability JSON CHECK (JSON_VALID(availability)),
    hours_per_week JSON CHECK (JSON_VALID(hours_per_week)),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX(student_id),
    FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE
);
