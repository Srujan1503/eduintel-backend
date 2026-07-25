-- EduIntel AI Backend Schema
-- Source of truth for database structure
-- Generated: 2026-07-25

-- ============================================================================
-- ROLES TABLE
-- ============================================================================
CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR NOT NULL UNIQUE,
    description TEXT,
    permissions JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- SCHOOLS TABLE (Tenants)
-- ============================================================================
CREATE TABLE schools (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR NOT NULL,
    type VARCHAR NOT NULL,  -- 'school' | 'college' | 'coaching_institute' | 'franchise'
    subscription_tier VARCHAR NOT NULL DEFAULT 'starter',
    address VARCHAR,
    city VARCHAR,
    state VARCHAR,
    country VARCHAR DEFAULT 'India',
    website VARCHAR,
    phone VARCHAR,
    logo_url VARCHAR,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- ============================================================================
-- PROFILES TABLE (User accounts linked to Supabase auth.users)
-- ============================================================================
CREATE TABLE profiles (
    id UUID PRIMARY KEY,  -- Same as auth.users.id
    school_id UUID REFERENCES schools(id) ON DELETE SET NULL,
    role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    full_name VARCHAR NOT NULL,
    avatar_url VARCHAR,
    phone VARCHAR,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- CAMPAIGNS TABLE (Marketing campaigns per school)
-- ============================================================================
CREATE TABLE campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school_id UUID NOT NULL REFERENCES schools(id),
    name VARCHAR NOT NULL,
    channel VARCHAR,
    start_date DATE,
    end_date DATE,
    budget NUMERIC DEFAULT 0,
    spend NUMERIC DEFAULT 0,
    conversions INTEGER DEFAULT 0,
    meta JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- ============================================================================
-- COMPETITORS TABLE (Competitor intelligence per school)
-- ============================================================================
CREATE TABLE competitors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    school_id UUID REFERENCES schools(id) ON DELETE CASCADE,
    name VARCHAR NOT NULL,
    domain VARCHAR,
    meta JSONB,
    threat_score FLOAT DEFAULT 0.0,
    first_seen TIMESTAMP WITH TIME ZONE,
    last_seen TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- ============================================================================
-- INDEXES
-- ============================================================================
CREATE INDEX idx_profiles_school_id ON profiles(school_id);
CREATE INDEX idx_profiles_role_id ON profiles(role_id);
CREATE INDEX idx_campaigns_school_id ON campaigns(school_id);
CREATE INDEX idx_campaigns_deleted_at ON campaigns(deleted_at);
CREATE INDEX idx_competitors_school_id ON competitors(school_id);
CREATE INDEX idx_competitors_deleted_at ON competitors(deleted_at);
CREATE INDEX idx_competitors_threat_score ON competitors(threat_score DESC);
CREATE INDEX idx_schools_deleted_at ON schools(deleted_at);
