# configure heroku environment
heroku config:set \
SECRET_KEY="XXX" \
TWILIO_ID="XXX" \
TWILIO_TOKEN="XXX" \
AWS_ACCESS_KEY_ID="XXX" \
AWS_SECRET_ACCESS_KEY="XXX" \
EMAIL_HOST_USER="XXX" \
EMAIL_HOST_PASSWORD="XXX" \
EMAIL_HOST="email-smtp.us-east-1.amazonaws.com" \
SECURE_SSL_REDIRECT="1" \
ALLOWED_HOSTS=".herokuapp.com"\