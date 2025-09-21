-- Supabase Security Setup: Enable Row-Level Security (RLS)
-- Run this in Supabase Dashboard > SQL Editor

-- =====================================================
-- ENABLE ROW-LEVEL SECURITY ON ALL TABLES
-- =====================================================

-- Enable RLS on users table
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Enable RLS on projects table  
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;

-- Enable RLS on jobs table
ALTER TABLE jobs ENABLE ROW LEVEL SECURITY;

-- Enable RLS on applications table
ALTER TABLE applications ENABLE ROW LEVEL SECURITY;

-- =====================================================
-- USERS TABLE POLICIES
-- =====================================================

-- Users can only see and update their own profile
CREATE POLICY "Users can view own profile" ON users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON users
    FOR UPDATE USING (auth.uid() = id);

-- Allow user registration (insert new users)
CREATE POLICY "Enable insert for authentication" ON users
    FOR INSERT WITH CHECK (auth.uid() = id);

-- =====================================================
-- PROJECTS TABLE POLICIES  
-- =====================================================

-- Users can only see their own projects
CREATE POLICY "Users can view own projects" ON projects
    FOR SELECT USING (auth.uid() = user_id);

-- Users can create their own projects
CREATE POLICY "Users can insert own projects" ON projects
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Users can update their own projects
CREATE POLICY "Users can update own projects" ON projects
    FOR UPDATE USING (auth.uid() = user_id);

-- Users can delete their own projects
CREATE POLICY "Users can delete own projects" ON projects
    FOR DELETE USING (auth.uid() = user_id);

-- =====================================================
-- APPLICATIONS TABLE POLICIES
-- =====================================================

-- Users can only see their own applications
CREATE POLICY "Users can view own applications" ON applications
    FOR SELECT USING (auth.uid() = user_id);

-- Users can create their own applications
CREATE POLICY "Users can insert own applications" ON applications
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Users can update their own applications
CREATE POLICY "Users can update own applications" ON applications
    FOR UPDATE USING (auth.uid() = user_id);

-- Users can delete their own applications
CREATE POLICY "Users can delete own applications" ON applications
    FOR DELETE USING (auth.uid() = user_id);

-- =====================================================
-- JOBS TABLE POLICIES (PUBLIC READ, ADMIN WRITE)
-- =====================================================

-- All authenticated users can read jobs (public job listings)
CREATE POLICY "Authenticated users can view jobs" ON jobs
    FOR SELECT USING (auth.role() = 'authenticated');

-- Only service role can insert/update/delete jobs (for API job fetching)
CREATE POLICY "Service role can manage jobs" ON jobs
    FOR ALL USING (auth.role() = 'service_role');

-- =====================================================
-- VERIFY SECURITY SETUP
-- =====================================================

-- Check that RLS is enabled on all tables
SELECT 
    schemaname,
    tablename,
    rowsecurity as rls_enabled
FROM pg_tables 
WHERE schemaname = 'public' 
    AND tablename IN ('users', 'projects', 'jobs', 'applications');

-- List all policies created
SELECT 
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd,
    qual,
    with_check
FROM pg_policies 
WHERE schemaname = 'public'
ORDER BY tablename, policyname;