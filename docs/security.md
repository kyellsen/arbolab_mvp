# Security Notes

Production-relevant security items and hardening tasks.

## Open items

- apps/web/main.py: `secret_key="SUPER_SECRET_KEY_CHANGE_ME"` is OK for
  localhost dev, but production must load the secret via `os.getenv` instead of
  hardcoding.
