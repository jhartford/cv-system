# ORCID OAuth 2.0 Setup Guide

This guide explains how to set up OAuth 2.0 integration with ORCID to enable two-way synchronization between your CV Manager and ORCID profile.

## Overview

OAuth 2.0 integration allows CV Manager to:
- **Read** your ORCID profile and publications
- **Write** new publications to your ORCID profile
- **Update** existing publications in your ORCID profile
- **Sync** your CV publications with ORCID bidirectionally

## Prerequisites

1. **ORCID Account**: You need an active ORCID profile
2. **ORCID Member API Access**: Required for write permissions
3. **OAuth Application**: Register your CV Manager instance with ORCID

## Step 1: Register for ORCID Member API Access

### For Individual Researchers
1. Contact your institution's library or research office
2. Many institutions have ORCID Member API access for their researchers
3. Ask if they can create OAuth credentials for your CV Manager instance

### For Institutions
1. Visit [ORCID Developer Tools](https://orcid.org/developer-tools)
2. Apply for ORCID Member API access
3. Review pricing and membership options
4. Complete the membership application process

### For Testing (Sandbox)
1. Visit [ORCID Sandbox](https://sandbox.orcid.org)
2. Create a test ORCID profile
3. Request sandbox API credentials for development/testing

## Step 2: Create OAuth Application

Once you have Member API access:

1. **Log into ORCID Developer Console**
   - Production: `https://orcid.org/developer-tools`
   - Sandbox: `https://sandbox.orcid.org/developer-tools`

2. **Create New Application**
   - Click "Create Application" or "Register Application"
   - Fill in application details:
     - **Name**: CV Manager
     - **Description**: Academic CV management and ORCID synchronization
     - **Website**: Your institution or personal website
     - **Logo**: Optional CV Manager or institution logo

3. **Configure OAuth Settings**
   - **Redirect URIs**: Add both web and CLI callback URLs:
     ```
     http://localhost:5000/orcid/callback     # For web interface
     http://localhost:8080/oauth/callback     # For CLI interface
     ```
   - **Requested Scopes**:
     - `/read-limited` - Read ORCID profile and works
     - `/activities/update` - Add, edit, and delete works
   - **Grant Types**: Authorization Code
   - **Client Type**: Confidential

4. **Save Application**
   - Note down the generated **Client ID** and **Client Secret**
   - Keep these credentials secure and private

## Step 3: Configure CV Manager

### Environment Variables

Set the OAuth credentials in your environment:

```bash
# For production ORCID
export ORCID_CLIENT_ID="your-client-id-here"
export ORCID_CLIENT_SECRET="your-client-secret-here"

# For development/testing (if using sandbox)
export ORCID_SANDBOX_CLIENT_ID="your-sandbox-client-id"
export ORCID_SANDBOX_CLIENT_SECRET="your-sandbox-client-secret"
```

### Configuration File (Alternative)

Or create a configuration file:

```yaml
# ~/.cv-manager/config.yaml
orcid:
  client_id: "your-client-id-here"
  client_secret: "your-client-secret-here"
  sandbox:
    client_id: "your-sandbox-client-id"
    client_secret: "your-sandbox-client-secret"
```

## Step 4: Connect Your ORCID Profile

### Using Web Interface

1. **Start CV Manager Web Server**
   ```bash
   cv-manager serve
   ```

2. **Navigate to ORCID Connect**
   - Go to `http://localhost:5000/orcid/connect`
   - Enter your ORCID ID
   - Choose sandbox mode if testing
   - Click "Connect to ORCID"

3. **Authorize Application**
   - You'll be redirected to ORCID's authorization page
   - Review the requested permissions:
     - Read your ORCID profile
     - Add/edit works in your profile
   - Click "Authorize" to grant permissions

4. **Complete Connection**
   - You'll be redirected back to CV Manager
   - Your ORCID profile is now connected and ready for sync

### Using CLI Interface

1. **Connect to ORCID**
   ```bash
   cv-manager orcid-connect 0000-0000-0000-0000
   ```

2. **Follow OAuth Flow**
   - Your browser will open to ORCID's authorization page
   - Review and approve the permissions
   - Copy the authorization code from the callback URL
   - Paste it in the CLI when prompted

3. **Verify Connection**
   ```bash
   cv-manager orcid-status
   ```

## Step 5: Sync Publications

### Web Interface Sync

1. **Navigate to Sync Page**
   - Go to `http://localhost:5000/orcid/sync`
   - Select your connected ORCID profile

2. **Choose Sync Options**
   - **Dry Run**: Preview changes without posting (recommended first)
   - **Sandbox**: Use sandbox environment if testing

3. **Review and Sync**
   - Click "Start Sync" to begin
   - Review the results and any errors
   - Run again without dry run to actually post publications

### CLI Sync

1. **Dry Run (Recommended)**
   ```bash
   cv-manager orcid-sync 0000-0000-0000-0000 --dry-run
   ```

2. **Actual Sync**
   ```bash
   cv-manager orcid-sync 0000-0000-0000-0000
   ```

3. **Force Sync (No Confirmation)**
   ```bash
   cv-manager orcid-sync 0000-0000-0000-0000 --force
   ```

## Security Considerations

### Access Token Storage

- **Web Interface**: Tokens stored in browser session (temporary)
- **CLI Interface**: Tokens stored in `~/.cv-manager/orcid_tokens.yaml` (file permissions: 600)
- **Production**: Consider using secure credential storage systems

### Token Expiration

- Access tokens typically expire after 20 years for ORCID
- Refresh tokens can be used to get new access tokens
- CV Manager will handle token refresh automatically when implemented

### Revoking Access

To revoke CV Manager's access to your ORCID profile:

1. **Log into ORCID**
   - Go to your ORCID account settings
   - Navigate to "Trusted Organizations" or "Applications"

2. **Revoke Access**
   - Find "CV Manager" in the list
   - Click "Revoke Access" or "Remove"

3. **Clean Up Local Tokens**
   ```bash
   rm ~/.cv-manager/orcid_tokens.yaml  # CLI tokens
   # Web tokens are automatically cleared when browser session ends
   ```

## Troubleshooting

### Common Issues

1. **"ORCID OAuth credentials not configured"**
   - Ensure environment variables are set: `ORCID_CLIENT_ID`, `ORCID_CLIENT_SECRET`
   - Check variable names are exactly correct
   - Verify credentials are from the correct environment (production vs sandbox)

2. **"Invalid redirect URI"**
   - Verify redirect URIs in your ORCID application settings match exactly
   - Web: `http://localhost:5000/orcid/callback`
   - CLI: `http://localhost:8080/oauth/callback`
   - Check for trailing slashes or typos

3. **"Insufficient privileges"**
   - Ensure your ORCID application has `/activities/update` scope
   - Verify you have ORCID Member API access (not just Public API)
   - Check that you authorized the correct scopes during OAuth

4. **"No publications found"**
   - Verify your publications.yaml file exists and has publications
   - Check publication format matches expected structure
   - Run `cv-manager validate` to check data integrity

5. **"SSL Certificate Error"**
   - CV Manager includes SSL error handling for ORCID API
   - If issues persist, check your network connection
   - Consider using sandbox environment for testing

### Debug Mode

Enable verbose logging:

```bash
export CV_MANAGER_DEBUG=1
cv-manager orcid-sync 0000-0000-0000-0000 --dry-run
```

### Getting Help

1. Check error messages carefully - they usually indicate the specific issue
2. Verify ORCID application configuration matches requirements
3. Test with sandbox environment first
4. Ensure OAuth credentials are from the correct ORCID environment

## API Limits and Best Practices

### ORCID API Limits

- **Rate Limiting**: ORCID APIs have rate limits per application
- **Bulk Operations**: Sync large publication lists gradually
- **Duplicate Prevention**: CV Manager automatically checks for duplicates

### Best Practices

1. **Start with Dry Run**: Always test sync with `--dry-run` first
2. **Use Sandbox for Testing**: Develop and test with sandbox environment
3. **Backup Data**: Keep backups of your publications.yaml file
4. **Regular Sync**: Sync incrementally rather than all at once
5. **Monitor Quotas**: Be aware of your API usage limits

## Example Workflows

### Initial Setup Workflow

```bash
# 1. Set OAuth credentials
export ORCID_CLIENT_ID="your-client-id"
export ORCID_CLIENT_SECRET="your-client-secret"

# 2. Connect ORCID profile
cv-manager orcid-connect 0000-0000-0000-0000

# 3. Check connection
cv-manager orcid-status

# 4. Test sync with dry run
cv-manager orcid-sync 0000-0000-0000-0000 --dry-run

# 5. Actual sync
cv-manager orcid-sync 0000-0000-0000-0000
```

### Regular Sync Workflow

```bash
# 1. Add new publications to publications.yaml
# 2. Validate data
cv-manager validate

# 3. Sync new publications
cv-manager orcid-sync 0000-0000-0000-0000 --dry-run
cv-manager orcid-sync 0000-0000-0000-0000

# 4. Import any changes from ORCID
cv-manager import-orcid 0000-0000-0000-0000 --merge
```

## Advanced Configuration

### Custom Redirect URIs

For production deployment, configure custom redirect URIs:

```bash
# Set custom base URL
export CV_MANAGER_BASE_URL="https://your-domain.com"

# Update ORCID application redirect URIs:
# https://your-domain.com/orcid/callback
```

### Multiple ORCID Profiles

CV Manager supports multiple connected ORCID profiles:

```bash
# Connect multiple profiles
cv-manager orcid-connect 0000-0000-0000-0001
cv-manager orcid-connect 0000-0000-0000-0002

# Check all connections
cv-manager orcid-status

# Sync specific profile
cv-manager orcid-sync 0000-0000-0000-0001
```

This completes the ORCID OAuth 2.0 setup. You now have full bidirectional synchronization between your CV Manager and ORCID profile!