# Deploy script for FTP/SFTP
# Save this as deploy.sh in the project root and make it executable.
# Edit the variables below with your server credentials before running.

# ==================== CONFIGURATION ====================
FTP_HOST="your.ftp.host"          # e.g., ftp.aliso.com.ar
FTP_USER="your_username"
FTP_PASS="your_password"
# If you use SFTP (SSH), set SFTP=true and provide the SSH key path if needed.
SFTP=false
SSH_KEY="" # path to private key if using key authentication
# Remote directory where the site should be uploaded (relative to FTP root)
REMOTE_DIR="/public_html"  # adjust as needed
# =======================================================

# Archive the site
ZIP_NAME="aliso_site_$(date +%Y%m%d%H%M%S).zip"
zip -r "$ZIP_NAME" . -x "*.git*" "*.idea*" "node_modules/*" "*.zip"

if [ "$SFTP" = true ]; then
  echo "Uploading via SFTP..."
  if [ -n "$SSH_KEY" ]; then
    sftp -i "$SSH_KEY" "$FTP_USER"@"$FTP_HOST":"$REMOTE_DIR" <<< $'put $ZIP_NAME'
  else
    sftp "$FTP_USER"@"$FTP_HOST":"$REMOTE_DIR" <<< $'put $ZIP_NAME'
  fi
else
  echo "Uploading via FTP..."
  # Using curl for simple FTP upload (works for both FTP and FTPS)
  curl -T "$ZIP_NAME" "ftp://$FTP_USER:$FTP_PASS@$FTP_HOST$REMOTE_DIR/"
fi

# Clean up local zip filem "$ZIP_NAME"

echo "Deployment finished."
