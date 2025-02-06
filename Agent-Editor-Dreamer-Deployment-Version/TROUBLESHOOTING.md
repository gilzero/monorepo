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
