# =============================================================================
# KONFIGURACJA APLIKACJI - SZABLON
# =============================================================================
# INSTRUKCJA:
# 1. Skopiuj ten plik jako .env (cp .env.example .env)
# 2. Wypełnij wartości zgodnie z Twoim środowiskiem
# 3. NIE commituj pliku .env do git!

# Nazwa aplikacji
APP_NAME=Webhook Debugger

# Wersja API
APP_VERSION=0.1.0

# Port serwera
PORT=8000

# Bazowy URL
# Development: http://localhost:8000
# Production: https://api.yourdomain.com
BASE_URL=http://localhost:8000

# CORS - dozwolone domeny (oddzielone przecinkami, bez spacji)
# Development: localhost:3000,localhost:5173
# Production: https://yourdomain.com
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173

# =============================================================================
# PRZYSZŁE ZMIENNE (na później)
# =============================================================================
# DATABASE_URL=postgresql://user:password@localhost:5432/webhook_db
# REDIS_URL=redis://localhost:6379
# ANTHROPIC_API_KEY=your_api_key_here