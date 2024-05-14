def absolute(request):
    urls = {
        "ABSOLUTE_ROOT": request.build_absolute_uri("/")[:-1].strip("/"),
        "FULL_URL_WITH_QUERY_STRING": request.build_absolute_uri(),
        "FULL_URL": request.build_absolute_uri("?"),
    }

    return urls


def gebruikersnaam(gebruiker):
    if gebruiker.first_name or gebruiker.last_name:
        first_name = gebruiker.first_name if gebruiker.first_name else ""
        last_name = gebruiker.last_name if gebruiker.last_name else ""
        return f"{first_name} {last_name}".strip()
    return gebruiker.email


def truncate_tekst(text, length=200):
    if len(text) > length:
        return f"{text[:length]}..."
    return text
