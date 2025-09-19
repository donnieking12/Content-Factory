# Supabase Setup Guide

## Prerequisites

1. Create a Supabase account at https://supabase.com/
2. Create a new Supabase project

## Setting up Supabase

### 1. Create a New Project

1. Log in to your Supabase account
2. Click "New Project"
3. Enter a name for your project
4. Select a region closest to you
5. Set a database password (make sure to save this)
6. Click "Create new project"

### 2. Get Your Connection Details

After your project is created, navigate to:
- Project Settings → Database
- Copy the following information:
  - `SUPABASE_URL`: The API URL (starts with https://)
  - `SUPABASE_KEY`: The anon/public key (not the service role key for security)

### 3. Update Your Environment Variables

Update your [.env](file:///c%3A/Users/Mimi/content-factory-ai/.env) file with the real values:

```env
# Database settings (Supabase)
SUPABASE_URL=your_actual_supabase_url_here
SUPABASE_KEY=your_actual_supabase_key_here
```

### 4. Create Database Tables

Run the setup script to create the necessary tables:

```bash
python setup_db.py
```

This will create the following tables:
- `products`
- `videos`
- `social_media_posts`

### 5. Verify Connection

You can verify your connection by running:

```bash
python db_test.py
```

If successful, you should see a message confirming the database connection is working.

## Troubleshooting

If you encounter connection issues:

1. Check that your Supabase URL and key are correct
2. Ensure your Supabase project is not paused
3. Verify your network connection
4. Check that you're using the anon/public key, not the service role key