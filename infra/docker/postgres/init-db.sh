#!/bin/bash
set -e

echo "MathVerse PostgreSQL Initialization Script"
echo "============================================"

# Create additional databases for microservices
echo "Creating databases..."

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    -- Create separate databases for each service (logical separation)
    CREATE DATABASE content_db;
    CREATE DATABASE analytics_db;
    CREATE DATABASE recommendation_db;
    
    -- Grant access to application user
    GRANT ALL PRIVILEGES ON DATABASE content_db TO mathverse_user;
    GRANT ALL PRIVILEGES ON DATABASE analytics_db TO mathverse_user;
    GRANT ALL PRIVILEGES ON DATABASE recommendation_db TO mathverse_user;
    
    -- Connect to each database and create extensions
    \c content_db
    
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    CREATE EXTENSION IF NOT EXISTS "pg_trgm";
    
    \c analytics_db
    
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    CREATE EXTENSION IF NOT EXISTS "pg_trgm";
    
    \c recommendation_db
    
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    CREATE EXTENSION IF NOT EXISTS "pg_trgm";
    
    -- Return to main database
    \c $POSTGRES_DB
    
    -- Create custom types
    DO \$\$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'user_role') THEN
            CREATE TYPE user_role AS ENUM ('student', 'teacher', 'admin', 'creator');
        END IF;
        
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'content_type') THEN
            CREATE TYPE content_type AS ENUM ('video', 'lesson', 'quiz', 'practice', 'interactive', 'animation', 'document', 'assessment', 'game');
        END IF;
        
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'content_status') THEN
            CREATE TYPE content_status AS ENUM ('draft', 'pending_review', 'approved', 'published', 'archived', 'rejected');
        END IF;
        
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'difficulty_level') THEN
            CREATE TYPE difficulty_level AS ENUM ('foundational', 'beginner', 'intermediate', 'advanced', 'expert');
        END IF;
    END
    \$\$;
    
    -- Create search index for full-text search
    CREATE INDEX IF NOT EXISTS idx_content_search ON content_db.content_items USING gin (to_tsvector('english', title || ' ' || COALESCE(description, '')));
    CREATE INDEX IF NOT EXISTS idx_user_email ON users(email);
    CREATE INDEX IF NOT EXISTS idx_course_subject ON courses(subject);
    CREATE INDEX IF NOT EXISTS idx_content_type ON content_db.content_items(content_type);
    
    -- Create composite indexes for common queries
    CREATE INDEX IF NOT EXISTS idx_content_status_type ON content_db.content_items(status, content_type);
    CREATE INDEX IF NOT EXISTS idx_content_difficulty ON content_db.content_items(difficulty);
    CREATE INDEX IF NOT EXISTS idx_user_created_at ON users(created_at DESC);
    CREATE INDEX IF NOT EXISTS idx_enrollment_user_course ON course_enrollments(user_id, course_id);
    CREATE INDEX IF NOT EXISTS idx_progress_user_content ON user_content_progress(user_id, content_id);
EOSQL

echo "Database initialization completed successfully!"
echo ""
echo "Created databases:"
echo "  - $POSTGRES_DB (main database)"
echo "  - content_db (content metadata)"
echo "  - analytics_db (analytics data)"
echo "  - recommendation_db (recommendation data)"
echo ""
echo "Installed extensions:"
echo "  - uuid-ossp"
echo "  - pg_trgm"
echo ""
echo "Custom types created:"
echo "  - user_role"
echo "  - content_type"
echo "  - content_status"
echo "  - difficulty_level"
