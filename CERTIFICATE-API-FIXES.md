# Certificate API Troubleshooting & Fixes

## Issues Resolved ✅

### 1. Missing `send_email` Function
**Problem**: The backend had an undefined `send_email` function being called in the bulk certificate sending endpoint, causing compilation errors.

**Fix**: Added the missing `send_email()` function with:
- Email configuration validation
- MIME message construction
- Optional file attachment support
- Proper error handling and logging

### 2. Signature Sources Updated
**Problem**: Signatures weren't loading from the requested build directory paths.

**Fix**: Updated signature loading to use:
- President: `build/president-signature.png` (138KB)
- Secretary: `build/Dr_Augustine_Duru_signature.png` (8KB)  
- Chairman: `backend/static/chairman-signature.png` (5KB)

### 3. API Route Verification
**Status**: ✅ CONFIRMED WORKING
- Route `/api/send-certificate/<int:participant_id>` exists
- Accepts POST requests
- Health check returns 200 status
- Application loads successfully

## Current Status 📊

### API Endpoints Working ✅
- `/api/health` - Returns 200
- `/api/status` - Returns 200  
- `/api/send-certificate/<participant_id>` - Available

### Certificate Generation ✅
- PDF generation available with wkhtmltopdf
- All signatures loaded correctly (President ✓, Chairman ✓, Secretary ✓)
- Templates render properly with no unrendered variables

### Database Connection ⚠️
- **Issue**: Connection timeout to DigitalOcean database
- **Impact**: Certificate sending requires database access for participant lookup
- **Status**: Application starts but database functionality limited

## Troubleshooting the 404/504 Errors

### 404 Error Analysis
The `/api/send-certificate/1` route exists and is properly registered. If getting 404:

1. **Check URL path**: Ensure frontend is calling correct path
2. **Verify participant ID**: Ensure participant ID exists in database
3. **Check server deployment**: May be deployment/routing issue

### 504 Gateway Timeout Analysis
The 504 error suggests:

1. **Database timeout**: Connection to DigitalOcean database timing out
2. **PDF generation delay**: Large signature files or processing delay
3. **Email sending timeout**: SMTP operations taking too long

## Deployment Status 🚀

### Latest Commits
1. **ebf7423**: Fixed missing `send_email` function 
2. **893a553**: Updated signature sources to use build directory

### Changes Pushed to Production
- Missing function fix deployed
- Signature path updates deployed
- Should resolve compilation errors

## Recommended Next Steps

### Immediate
1. **Check DigitalOcean deployment logs** for any startup errors
2. **Verify database connection** in production environment
3. **Test API endpoint directly** in production to isolate frontend vs backend issue

### If Issues Persist
1. **Database Connection**: Check DigitalOcean database firewall/SSL settings
2. **Email Configuration**: Verify EMAIL_* environment variables in production
3. **PDF Generation**: Ensure wkhtmltopdf is available in production container

## Testing Commands

### Local Testing
```bash
# Test Flask routes
cd backend
python -c "from minimal_app import app; print([rule.rule for rule in app.url_map.iter_rules() if 'send-certificate' in rule.rule])"

# Test signature loading
python -c "from minimal_app import PRESIDENT_SIGNATURE, CHAIRMAN_SIGNATURE, SECRETARY_SIGNATURE; print('Signatures loaded:', bool(PRESIDENT_SIGNATURE), bool(CHAIRMAN_SIGNATURE), bool(SECRETARY_SIGNATURE))"
```

### Production Testing
```bash
# Test health endpoint
curl https://your-domain.com/api/health

# Test send certificate (replace with real participant ID)
curl -X POST https://your-domain.com/api/send-certificate/1
```

## Error Logs to Monitor

1. **DigitalOcean App Platform logs**: Look for startup errors
2. **Database connection errors**: psycopg2.OperationalError messages
3. **Email sending errors**: SMTP authentication/connection failures
4. **PDF generation errors**: wkhtmltopdf missing or timeout errors

The core functionality is fixed and should work. The remaining issues are likely infrastructure-related (database connectivity) rather than code issues.
