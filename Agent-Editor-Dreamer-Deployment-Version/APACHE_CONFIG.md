# Apache Configuration Documentation

## Complete Virtual Host Configuration

```apache
<VirtualHost *:80>
    ServerName agenteditor.dreamer.xyz
    DocumentRoot /home/ubuntu/gilzero.dev/EditorDocAIAgentV1
    # Redirect all HTTP traffic to HTTPS
    RewriteEngine On
    RewriteCond %{HTTPS} off
    RewriteRule ^(.*)$ https://agenteditor.dreamer.xyz$1 [L,R=301]
    ErrorLog ${APACHE_LOG_DIR}/agenteditor_dreamer_xyz_error.log
    CustomLog ${APACHE_LOG_DIR}/agenteditor_dreamer_xyz_access.log combined
</VirtualHost>

<IfModule mod_ssl.c>
    <VirtualHost *:443>
        ServerName agenteditor.dreamer.xyz
        DocumentRoot /home/ubuntu/gilzero.dev/EditorDocAIAgentV1

        # WSGI configuration
        WSGIDaemonProcess agenteditor \
            python-home=/home/ubuntu/gilzero.dev/EditorDocAIAgentV1/venv \
            python-path=/home/ubuntu/gilzero.dev/EditorDocAIAgentV1 \
            lang='C.UTF-8' \
            locale='C.UTF-8' \
            python-eggs=/tmp
        WSGIProcessGroup agenteditor
        WSGIApplicationGroup %{GLOBAL}
        WSGIScriptAlias / /home/ubuntu/gilzero.dev/EditorDocAIAgentV1/wsgi.py

        # Environment Settings
        SetEnv LANG C.UTF-8
        SetEnv LC_ALL C.UTF-8
        SetEnv PYTHONIOENCODING utf-8

        <Directory /home/ubuntu/gilzero.dev/EditorDocAIAgentV1>
            AllowOverride All
            Require all granted
            Options -Indexes +FollowSymLinks
        </Directory>

        # Static files configuration
        Alias /static/ /home/ubuntu/gilzero.dev/EditorDocAIAgentV1/static/
        <Directory /home/ubuntu/gilzero.dev/EditorDocAIAgentV1/static>
            Require all granted
            Options -Indexes
        </Directory>

        # Upload directory configuration
        Alias /uploads/ /home/ubuntu/gilzero.dev/EditorDocAIAgentV1/uploads/
        <Directory /home/ubuntu/gilzero.dev/EditorDocAIAgentV1/uploads>
            Require all granted
            Options -Indexes
        </Directory>

        # SSL Configuration
        SSLEngine on
        SSLCertificateFile /etc/apache2/ssl/dreamer_xyz/dreamer_combined.crt
        SSLCertificateKeyFile /etc/apache2/ssl/dreamer_xyz/star_dreamer_xyz.key

        # Security headers
        Header set X-Content-Type-Options "nosniff"
        Header set X-Frame-Options "SAMEORIGIN"
        Header set X-XSS-Protection "1; mode=block"
        Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains"

        # Logging
        ErrorLog ${APACHE_LOG_DIR}/agenteditor_dreamer_xyz_ssl_error.log
        CustomLog ${APACHE_LOG_DIR}/agenteditor_dreamer_xyz_ssl_access.log combined
    </VirtualHost>
</IfModule>
```

## Configuration Breakdown

### HTTP to HTTPS Redirect (Port 80)
```apache
<VirtualHost *:80>
    ServerName agenteditor.dreamer.xyz
    RewriteEngine On
    RewriteCond %{HTTPS} off
    RewriteRule ^(.*)$ https://agenteditor.dreamer.xyz$1 [L,R=301]
</VirtualHost>
```
This section handles redirecting all HTTP traffic to HTTPS. The `[L,R=301]` flags indicate:
- `L`: Last rule to process
- `R=301`: Permanent redirect

### WSGI Configuration
```apache
WSGIDaemonProcess agenteditor \
    python-home=/home/ubuntu/gilzero.dev/EditorDocAIAgentV1/venv \
    python-path=/home/ubuntu/gilzero.dev/EditorDocAIAgentV1 \
    lang='C.UTF-8' \
    locale='C.UTF-8' \
    python-eggs=/tmp
WSGIProcessGroup agenteditor
WSGIApplicationGroup %{GLOBAL}
WSGIScriptAlias / /home/ubuntu/gilzero.dev/EditorDocAIAgentV1/wsgi.py
```
- `WSGIDaemonProcess`: Creates a daemon process group for the application
- `python-home`: Points to virtual environment
- `python-path`: Application directory
- `lang` and `locale`: UTF-8 encoding settings
- `WSGIScriptAlias`: Maps URL path to WSGI application

### Environment Variables
```apache
SetEnv LANG C.UTF-8
SetEnv LC_ALL C.UTF-8
SetEnv PYTHONIOENCODING utf-8
```
These ensure proper UTF-8 encoding throughout the application.

### Directory Configurations
```apache
<Directory /home/ubuntu/gilzero.dev/EditorDocAIAgentV1>
    AllowOverride All
    Require all granted
    Options -Indexes +FollowSymLinks
</Directory>
```
- `AllowOverride All`: Allows .htaccess files
- `Require all granted`: Permits access
- `Options -Indexes +FollowSymLinks`: Disables directory listing, enables symlinks

### Static Files
```apache
Alias /static/ /home/ubuntu/gilzero.dev/EditorDocAIAgentV1/static/
<Directory /home/ubuntu/gilzero.dev/EditorDocAIAgentV1/static>
    Require all granted
    Options -Indexes
</Directory>
```
Maps `/static/` URL path to static files directory.

### Upload Directory
```apache
Alias /uploads/ /home/ubuntu/gilzero.dev/EditorDocAIAgentV1/uploads/
<Directory /home/ubuntu/gilzero.dev/EditorDocAIAgentV1/uploads>
    Require all granted
    Options -Indexes
</Directory>
```
Maps `/uploads/` URL path to uploads directory.

### SSL Configuration
```apache
SSLEngine on
SSLCertificateFile /etc/apache2/ssl/dreamer_xyz/dreamer_combined.crt
SSLCertificateKeyFile /etc/apache2/ssl/dreamer_xyz/star_dreamer_xyz.key
```
Configures SSL using wildcard certificate.

### Security Headers
```apache
Header set X-Content-Type-Options "nosniff"
Header set X-Frame-Options "SAMEORIGIN"
Header set X-XSS-Protection "1; mode=block"
Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains"
```
- Prevents MIME-type sniffing
- Controls frame embedding
- Enables XSS protection
- Enforces HTTPS

### Logging
```apache
ErrorLog ${APACHE_LOG_DIR}/agenteditor_dreamer_xyz_ssl_error.log
CustomLog ${APACHE_LOG_DIR}/agenteditor_dreamer_xyz_ssl_access.log combined
```
Configures separate log files for error and access logs.

## Required Apache Modules
- mod_ssl
- mod_wsgi
- mod_rewrite
- mod_headers

## Testing the Configuration
```bash
# Test syntax
sudo apache2ctl configtest

# Review logs
sudo tail -f /var/log/apache2/agenteditor_dreamer_xyz_ssl_error.log
sudo tail -f /var/log/apache2/agenteditor_dreamer_xyz_ssl_access.log
