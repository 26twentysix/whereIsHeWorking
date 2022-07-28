import src.app.util.settings as settings


def request_maker(method: str, params: str) -> str:
    return settings.base_url + method + '?' + params + '&access_token=' + \
           settings.access_token + '&v=' + settings.api_ver
