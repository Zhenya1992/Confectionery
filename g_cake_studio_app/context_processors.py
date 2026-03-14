from django.conf import settings


def social_auth_context(request):
    """Контекст для социальной аутентификации"""

    telegram_token = getattr(settings, "TELEGRAM_BOT_TOKEN", None)
    telegram_name = getattr(settings, "TELEGRAM_BOT_NAME", None)

    yandex_key = getattr(settings, "SOCIAL_AUTH_YANDEX_OAUTH2_KEY", None)
    google_key = getattr(settings, "SOCIAL_AUTH_GOOGLE_OAUTH2_KEY", None)

    return {
        "has_telegram_auth": bool(telegram_token and telegram_name),
        "has_yandex_auth": bool(yandex_key),
        "has_google_auth": bool(google_key),
        "TELEGRAM_BOT_NAME": telegram_name,
    }