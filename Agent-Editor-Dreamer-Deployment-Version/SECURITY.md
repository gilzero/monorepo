# Security Configuration

## SSL/TLS Configuration
- Using wildcard SSL certificate
- Auto-redirect HTTP to HTTPS
- HSTS enabled
- Certificate location: `/etc/apache2/ssl/dreamer_xyz/`

## File Permissions
- Upload directory: 775 permissions
- Database directory: 775 permissions
- Debug logs: 775 permissions
- Owner: www-data:www-data

## Apache Security Headers
- X-Content-Type-Options: nosniff
- X-Frame-Options: SAMEORIGIN
- X-XSS-Protection: 1; mode=block
- Strict-Transport-Security: max-age=31536000

## Directory Access Control
- Directory listing disabled
- Direct PHP execution disabled
- Access restricted to necessary directories only

## Environment Variables
- Stored in .env file
- Not tracked in git
- Sensitive keys protected

## Regular Security Tasks
1. Check log files for suspicious activity
2. Monitor file permissions
3. Keep system and packages updated
4. Review SSL certificate expiration
5. Monitor uploaded files

## Backup Security
- Regular database backups
- Configuration backups
- Secure backup storage
