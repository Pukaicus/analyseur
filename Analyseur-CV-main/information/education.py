import re
import spacy

def extraire_education(texte_cv):
    nlp = spacy.load('fr_core_news_lg')

    with open('C:/Users/Lukas/Downloads/Analyseur-CV-main/Analyseur-CV-main/Data/education.txt', 'r', encoding='utf-8') as f:
        mots_cles_education = [mot.strip().lower() for mot in f.readlines() if mot.strip()]

    lignes = [l.strip() for l in texte_cv.split('\n') if l.strip()]
    education = []

    date_pattern = re.compile(r'\b(19|20)\d{2}(?:\s*[-/–]\s*(?:19|20)?\d{2})?\b')
    mots_ecole = ['école', 'université', 'lycée', 'institut', 'centre', 'fac', 'college', 'formation', 'scolaire']
    mots_interdits = ['anglais', 'allemand', 'bilingue', 'relation client', 'freelance', 'facteur', 'conseiller', 'vendeur', '@', 'gmail', 'hotmail', 'langue', 'certification']

    i = 0
    while i < len(lignes):
        bloc = ' '.join(lignes[i:i+3])  # Regroupe 3 lignes
        bloc_lower = bloc.lower()

        # Vérifie que c’est bien une ligne liée à une formation
        if not any(m in bloc_lower for m in mots_cles_education):
            i += 1
            continue

        # Filtrage des fausses formations
        if any(bad in bloc_lower for bad in mots_interdits):
            i += 1
            continue

        # Recherche date
        date_match = date_pattern.search(bloc)
        date = date_match.group(0) if date_match else ''

        # Recherche école dans bloc
        ecole = ''
        for mot in mots_ecole:
            for j in range(3):
                if i + j < len(lignes):
                    ligne_candidate = lignes[i + j]
                    if mot in ligne_candidate.lower():
                        ecole = ligne_candidate.strip()
                        break
            if ecole:
                break

        # Diplôme = bloc - date - ecole
        diplome = bloc
        if date:
            diplome = diplome.replace(date, '')
        if ecole:
            diplome = diplome.replace(ecole, '')

        # Nettoyage
        diplome = re.sub(r'[:\-–•]', '', diplome).strip()

        # Validation stricte
        if sum(bool(val) for val in [date, ecole, diplome]) >= 2:
            education.append({
                "date": date or "Inconnu",
                "ecole": ecole or "Inconnu",
                "diplome": diplome or "Inconnu"
            })
            i += 3  # on saute les lignes utilisées
        else:
            i += 1

    return education
