import re
import spacy

def extraire_education(texte_cv):
    nlp = spacy.load('fr_core_news_lg')

    with open('C:/Users/Lukas/Downloads/Analyseur-CV-main/Analyseur-CV-main/Data/education.txt', 'r', encoding='utf-8') as f:
        mots_cles_education = [mot.strip().lower() for mot in f.readlines() if mot.strip()]

    lignes = [l.strip() for l in texte_cv.split('\n') if l.strip()]
    education = []

    date_pattern = re.compile(r'\b(19|20)\d{2}(?:\s*[-/–]?\s*(?:19|20)?\d{2})?\b')

    mots_ecole = [
        'école', 'université', 'lycée', 'institut', 'centre', 'fac', 'collège',
        'formation', 'scolaire', 'cnam', 'fst', 'greta', 'cned', 'à distance', 'eni'
    ]

    mots_interdits = [
        'alternance', 'recherche', 'stage', 'expérience', 'langue', 'certification',
        'projet', 'compétence', 'durant', 'obtenues', 'obtenus', 'freelance', 'contact',
        'atelier', 'assistant', 'surveillance', 'facteur', 'laposte',
        'service informatique', 'enseignant', 'enseignante'
    ]

    i = 0
    while i < len(lignes):
        bloc = ' '.join(lignes[i:i+3])
        bloc_lower = bloc.lower()

        if not any(m in bloc_lower for m in mots_cles_education):
            i += 1
            continue

        if any(mot_interdit in bloc_lower for mot_interdit in mots_interdits):
            i += 1
            continue

        date_match = date_pattern.search(bloc)
        date = date_match.group(0) if date_match else ''

        # Recherche de l’école
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

        # Nettoyage de l'école si polluée
        if ecole:
            ecole = re.sub(r'\(.*?\)', '', ecole)
            ecole = re.sub(r'-+', '-', ecole)
            ecole = re.sub(r'\b(obtenus?|obtenues?|durant|la formation)\b', '', ecole, flags=re.IGNORECASE)
            ecole = re.sub(r'\s{2,}', ' ', ecole).strip()

        # Si aucune école détectée, spaCy essaie de l'extraire
        if not ecole:
            bloc_nlp = nlp(bloc)
            for ent in bloc_nlp.ents:
                if ent.label_ == 'ORG':
                    ecole = ent.text.strip()
                    break

        # Tentative d'extraction du diplôme
        diplome = ''
        for mot in mots_cles_education:
            match = re.search(rf'\b({mot}[^\n,;]*)', bloc_lower)
            if match:
                diplome = match.group(1).strip()
                break

        # Fallback : bloc complet - date - école
        if not diplome:
            diplome = bloc
            if date:
                diplome = diplome.replace(date, '')
            if ecole:
                diplome = diplome.replace(ecole, '')

        # Nettoyage du diplôme
        diplome = re.sub(r'[:\-–•()]', '', diplome).strip()
        diplome = re.sub(r'\s{2,}', ' ', diplome)

        nb_infos = sum(bool(x and x.lower() != 'inconnu') for x in [date, ecole, diplome])
        if nb_infos >= 2:
            education.append({
                "date": date or "Inconnu",
                "ecole": ecole or "Inconnu",
                "diplome": diplome or "Inconnu"
            })
            i += 3
        else:
            i += 1

    return education
