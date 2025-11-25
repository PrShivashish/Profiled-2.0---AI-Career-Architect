-- Tabel untuk menyimpan hasil scraping LinkedIn
CREATE TABLE IF NOT EXISTS linkedin_jobs (
    id SERIAL PRIMARY KEY,
    title TEXT,
    company TEXT,
    location TEXT,
    url TEXT UNIQUE,
    description TEXT,
    skills_required TEXT,
    loaded_at TIMESTAMP DEFAULT NOW()
);