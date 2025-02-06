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
