import re

def extraire_numero_telephone(texte_cv):
    # Expression régulière élargie pour capter des numéros FR et internationaux
    pattern = re.compile(
        r'(?:(?:\+|00)\d{1,3}|0)[1-9](?:[\s\.-]?\d{2}){4}'
    )

    matches = pattern.finditer(texte_cv)
    for match in matches:
        numero = match.group()
        # Nettoyer le numéro (supprime les espaces, tirets, etc.)
        numero_nettoye = re.sub(r'[^\d+]', '', numero)
        return numero_nettoye  # renvoie le premier trouvé

    return None
