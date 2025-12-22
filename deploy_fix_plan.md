# Deployment Fix Plan - Django 400 Error

## Problem Identified
- Django ALLOWED_HOSTS setting is empty in production
- CSRF_TRUSTED_ORIGINS is also empty
- This causes Django's security middleware to reject all requests with 400 error
- Gunicorn is running correctly but Django blocks requests

## Root Cause
The `fromService` references in render.yaml for ALLOWED_HOSTS and CSRF_TRUSTED_ORIGINS are not working as expected.

## Solution Implementation

### Step 1: Create pre-deploy script
- Create a shell script that properly sets environment variables
- This script will be called before the container starts

### Step 2: Update render.yaml
- Add the pre-deploy script to the build process
- Ensure environment variables are set correctly before app starts

### Step 3: Alternative fix - Direct domain setting
- Update render.yaml to use direct domain values
- Set ALLOWED_HOSTS and CSRF_TRUSTED_ORIGINS with the actual Render URL

## Files to Edit
1. render.yaml - Update environment variable configuration
2. Potentially create a deploy script if needed

## Expected Result
- ALLOWED_HOSTS properly configured with Render domain
- CSRF_TRUSTED_ORIGINS properly configured
- Application accepts requests without 400 errors
- App becomes accessible at the deployed URL
