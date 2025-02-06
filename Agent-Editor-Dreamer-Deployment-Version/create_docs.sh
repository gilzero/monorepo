#!/bin/bash

cd /home/ubuntu/gilzero.dev/EditorDocAIAgentV1 && \
cat > MAINTENANCE.md << 'EOL'
# System Maintenance Guide

## Regular Maintenance Tasks

### Log Rotation
\`\`\`bash
# Check log sizes
sudo du -h /var/log/apache2/agenteditor_dreamer_xyz*

# Manually rotate logs if needed
sudo logrotate -f /etc/logrotate.d/apache2
\`\`\`

### Database Maintenance
\`\`\`bash
# Backup SQLite database
cd /home/ubuntu/gilzero.dev/EditorDocAIAgentV1/instance
cp dreamer_document_ai.db dreamer_document_ai.db.backup
\`\`\`

### Cleanup Tasks
\`\`\`bash
# Clean old uploads (files older than 7 days)
find /home/ubuntu/gilzero.dev/EditorDocAIAgentV1/uploads -type f -mtime +7 -delete

# Clean debug logs
find /home/ubuntu/gilzero.dev/EditorDocAIAgentV1/debug -type f -mtime +7 -delete
\`\`\`

### SSL Certificate
- Check expiration: \`openssl x509 -enddate -noout -in /etc/apache2/ssl/dreamer_xyz/dreamer_combined.crt\`
- Renewal process through your certificate provider

### System Updates
\`\`\`bash
# Update system packages
sudo apt update
sudo apt upgrade

# Update Python packages
source /home/ubuntu/gilzero.dev/EditorDocAIAgentV1/venv/bin/activate
pip list --outdated
pip install --upgrade -r requirements.txt
\`\`\`

## Monitoring

### Apache Status
\`\`\`bash
# Check Apache status
sudo systemctl status apache2

# Check Apache memory usage
ps -ylC apache2 --sort:rss
\`\`\`

### Disk Usage
\`\`\`bash
# Check disk space
df -h

# Check directory sizes
du -sh /home/ubuntu/gilzero.dev/EditorDocAIAgentV1/*
\`\`\`

## Backup Procedures

### Configuration Backup
\`\`\`bash
# Backup Apache config
sudo cp /etc/apache2/sites-available/agenteditor.dreamer.xyz.conf /backup/

# Backup application files
tar -czf /backup/agenteditor_$(date +%Y%m%d).tar.gz /home/ubuntu/gilzero.dev/EditorDocAIAgentV1
\`\`\`

### Database Backup
\`\`\`bash
# Backup SQLite database
cd /home/ubuntu/gilzero.dev/EditorDocAIAgentV1/instance
sqlite3 dreamer_document_ai.db ".backup 'backup.db'"
\`\`\`

## Troubleshooting

### Common Issues

1. **Application Not Responding**
\`\`\`bash
# Check Apache logs
sudo tail -f /var/log/apache2/agenteditor_dreamer_xyz_ssl_error.log

# Restart Apache
sudo systemctl restart apache2
\`\`\`

2. **Upload Issues**
\`\`\`bash
# Check directory permissions
ls -la /home/ubuntu/gilzero.dev/EditorDocAIAgentV1/uploads

# Fix permissions if needed
sudo chown -R www-data:www-data uploads
sudo chmod -R 775 uploads
\`\`\`

3. **Database Issues**
\`\`\`bash
# Check SQLite database
sqlite3 instance/dreamer_document_ai.db ".tables"
\`\`\`
EOL

cat > SECURITY.md << 'EOL'
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
EOL

cat > TROUBLESHOOTING.md << 'EOL'
# Troubleshooting Guide

## Common Issues and Solutions

### 1. File Upload Fails
**Symptoms:**
- "Failed to save file" error
- Upload process stops midway

**Solutions:**
\`\`\`bash
# Check permissions
ls -la /home/ubuntu/gilzero.dev/EditorDocAIAgentV1/uploads

# Fix permissions
sudo chown -R www-data:www-data uploads
sudo chmod -R 775 uploads

# Check logs
sudo tail -f /var/log/apache2/agenteditor_dreamer_xyz_ssl_error.log
\`\`\`

### 2. Apache Won't Start
**Symptoms:**
- Service fails to start
- 503 Service Unavailable

**Solutions:**
\`\`\`bash
# Check config syntax
sudo apache2ctl configtest

# Check error logs
sudo tail -f /var/log/apache2/error.log

# Check process status
sudo systemctl status apache2
\`\`\`

### 3. Database Issues
**Symptoms:**
- Database errors in logs
- Application not saving data

**Solutions:**
\`\`\`bash
# Check database permissions
ls -la instance/dreamer_document_ai.db

# Check database integrity
sqlite3 instance/dreamer_document_ai.db "PRAGMA integrity_check;"

# Backup and restore if needed
sqlite3 instance/dreamer_document_ai.db ".backup 'backup.db'"
\`\`\`

### 4. SSL/HTTPS Issues
**Symptoms:**
- SSL certificate errors
- Mixed content warnings

**Solutions:**
\`\`\`bash
# Check certificate
openssl x509 -enddate -noout -in /etc/apache2/ssl/dreamer_xyz/dreamer_combined.crt

# Check Apache SSL configuration
apache2ctl -M | grep ssl
\`\`\`

## Debug Mode

### Enable Debug Mode
1. Edit wsgi.py
2. Check debug logs
3. Monitor Apache error logs

### Log Locations
- Apache error log: `/var/log/apache2/agenteditor_dreamer_xyz_ssl_error.log`
- Application debug: `/home/ubuntu/gilzero.dev/EditorDocAIAgentV1/debug/`
- System log: `journalctl -u apache2.service`
EOL

echo "Documentation files created successfully!"
