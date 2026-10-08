# ORCID OAuth Integration - Work in Progress

## Current Status: 🟡 NEARLY WORKING
- ✅ ORCID authorization page now displays correctly
- ✅ User can authorize the application
- ❌ SSL certificate verification error when exchanging code for token

## Issues Identified and Fixed

### 1. ❌ → ✅ Redirect URI Mismatch
**Problem**: ORCID developer tools had wrong redirect URI
**Solution**: Set to exactly `http://127.0.0.1:5000/orcid/callback`

### 2. ❌ → ✅ Wrong OAuth Scopes
**Problem**: cv-manager was using `/activities/update` and `/read-limited` scopes
**Error**: ORCID immediately redirected without showing auth page
**Solution**: Changed to `/authenticate` scope (per ORCID documentation)

**Code Change Made:**
```python
# OLD (didn't work)
scopes = ['/activities/update', '/read-limited']

# NEW (working)
scopes = ['/authenticate']
```

### 3. ❌ → ✅ HTML5 Pattern Validation Too Strict
**Problem**: ORCID ID validation pattern rejected valid IDs
**Solution**: Fixed regex pattern in `orcid_connect.html` line 47

### 4. ❌ → ✅ Server Restarts Clearing Session
**Problem**: Flask development server restarts cleared OAuth session data
**Solution**: User runs server manually (not background task)

## Current Error: SSL Certificate Verification

**Error Message:**
```
Error processing ORCID authorization: HTTPSConnectionPool(host='orcid.org', port=443):
Max retries exceeded with url: /oauth/token (Caused by SSLError(SSLCertVerificationError(1,
'[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: Basic Constraints of CA cert not marked critical (_ssl.c:1028)')))
```

**Location**: During token exchange in `ORCIDClient.exchange_code_for_token()`
**Cause**: Python requests library can't verify ORCID's SSL certificate (common in some dev environments)

## Technical Details

### Working OAuth Configuration
- **Client ID**: `APP-OOBGO4RH1FWMW0D9`
- **Client Secret**: `0a6339d9-b60d-4ccc-84f1-054ff6113c4f`
- **Redirect URI**: `http://127.0.0.1:5000/orcid/callback`
- **Scope**: `/authenticate`
- **Environment**: Production (not sandbox)

### Flask Configuration Added
```python
app.config.update({
    'SERVER_NAME': '127.0.0.1:5000',  # Force consistent URL generation
})
```

### Debug Logging Added
Two debug sections added to `cv_manager/web/app.py`:

1. **Authorization Debug** (line ~427): Shows generated OAuth URL
2. **Callback Debug** (line ~444): Shows received parameters from ORCID

## Files Modified

### 1. `cv_manager/web/templates/orcid_connect.html`
- **Line 47**: Fixed HTML5 pattern validation regex

### 2. `cv_manager/web/app.py`
- **Line 21**: Added `SERVER_NAME` configuration
- **Line 408**: Changed OAuth scope to `/authenticate`
- **Lines 427-434**: Added authorization debug logging
- **Lines 444-457**: Added callback debug logging

## Current OAuth Flow Status

1. ✅ **User submits ORCID ID** → Form validation passes
2. ✅ **Generate OAuth URL** → Correctly formatted with `/authenticate` scope
3. ✅ **Redirect to ORCID** → User sees authorization page
4. ✅ **User authorizes** → ORCID approves the request
5. ✅ **Callback with code** → Authorization code received successfully
6. ✅ **Session validation** → State parameter and session data intact
7. ❌ **Token exchange** → SSL certificate error when calling ORCID token endpoint

## Next Steps

### Option 1: Fix SSL Certificate Issue (Recommended)
**Quick Fix**: Disable SSL verification for development
```python
# In ORCIDClient.exchange_code_for_token()
response = requests.post(token_endpoint, data=data, headers=headers, verify=False)
```

**Better Fix**: Update SSL certificates or configure requests to use proper CA bundle

### Option 2: Try Sandbox Environment
- Check "Use sandbox environment" on connect page
- Sandbox might have different SSL certificate requirements

### Option 3: Use Different HTTP Library
- Replace `requests` with `urllib3` or `httpx`
- Some libraries handle SSL certificates differently

### Option 4: Update Python/Certificates
- Update Python's CA certificate bundle: `pip install --upgrade certifi`
- Update Python itself if using older version

## Test Commands

### Manual Server Start
```bash
cd /Users/jason.hartford/Developer/Research/test-cv
source ../cv-system/.venv/bin/activate
export ORCID_CLIENT_ID="APP-OOBGO4RH1FWMW0D9"
export ORCID_CLIENT_SECRET="0a6339d9-b60d-4ccc-84f1-054ff6113c4f"
cv-manager serve --host 127.0.0.1 --port 5000
```

### OAuth Flow Test
1. Go to `http://127.0.0.1:5000/orcid/connect`
2. Enter ORCID ID: `0000-0002-4229-2588`
3. Click "Connect to ORCID"
4. Authorize on ORCID page
5. Should return to callback (currently fails at token exchange)

## ORCID API Documentation References

- **OAuth Scopes**: https://info.orcid.org/documentation/api-tutorials/api-tutorial-get-and-authenticated-orcid-id/
- **Redirect URI Requirements**: Must be exact match, HTTPS required for production
- **Example Authorization URL**:
  ```
  https://orcid.org/oauth/authorize?client_id=APP-OOBGO4RH1FWMW0D9&response_type=code&scope=/authenticate&redirect_uri=http://127.0.0.1:5000/orcid/callback
  ```

## Debug Output Examples

### Successful Authorization Debug
```
=== OAUTH AUTHORIZATION DEBUG ===
ORCID ID: 0000-0002-4229-2588
Redirect URI: http://127.0.0.1:5000/orcid/callback
Scopes: ['/authenticate']
Use sandbox: False
State: IfHe_saJdRrFFZjvoY8AM5jrKpTb2l9ps6GOcwBNw
Authorization URL: https://orcid.org/oauth/authorize?client_id=APP-OOBGO4RH1FWMW0D9&response_type=code&scope=%2Fauthenticate&redirect_uri=http%3A%2F%2F127.0.0.1%3A5000%2Forcid%2Fcallback&state=IfHe_saJdRrFFZjvoY8AM5jrKpTb2l9ps6GOcwBNw
=================================
```

### Successful Callback Debug (before SSL error)
```
=== ORCID CALLBACK DEBUG ===
Request URL: http://127.0.0.1:5000/orcid/callback?code=XXXXXX&state=IfHe_saJdRrFFZjvoY8AM5jrKpTb2l9ps6GOcwBNw
Request args: {'code': 'XXXXXX', 'state': 'IfHe_saJdRrFFZjvoY8AM5jrKpTb2l9ps6GOcwBNw'}
Code: XXXXXX
State: IfHe_saJdRrFFZjvoY8AM5jrKpTb2l9ps6GOcwBNw
Error: None
Session keys: ['csrf_token', 'oauth_orcid_id', 'oauth_sandbox', 'oauth_state']
OAuth state in session: IfHe_saJdRrFFZjvoY8AM5jrKpTb2l9ps6GOcwBNw
OAuth ORCID ID in session: 0000-0002-4229-2588
OAuth sandbox in session: False
=============================
```

## Lessons Learned

1. **Always check ORCID documentation** for correct scopes and parameters
2. **Exact redirect URI matching** is critical - even HTTP vs HTTPS matters
3. **Development server restarts** clear session data, breaking OAuth flows
4. **SSL certificate issues** are common in development environments
5. **Debug logging is essential** for OAuth troubleshooting

## Priority: Medium-High
OAuth integration is nearly complete. The SSL certificate issue is a common development environment problem with straightforward solutions. Once resolved, the ORCID integration should work fully.