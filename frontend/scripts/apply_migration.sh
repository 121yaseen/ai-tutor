#!/bin/bash

# Script to apply email column migration to profiles table
# This script assumes you have psql installed and DATABASE_URL in your .env file

echo "Applying email column migration to profiles table..."

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "Error: DATABASE_URL not found in environment variables"
    echo "Please ensure your .env file contains the DATABASE_URL"
    exit 1
fi

# Apply the migration
echo "Running complete profiles migration..."
psql "$DATABASE_URL" -f scripts/complete_profiles_migration.sql

if [ $? -eq 0 ]; then
    echo "✅ Migration applied successfully!"
    echo "Now regenerating Prisma client..."
    npx prisma generate
    echo "✅ Prisma client regenerated!"
else
    echo "❌ Migration failed!"
    exit 1
fi 