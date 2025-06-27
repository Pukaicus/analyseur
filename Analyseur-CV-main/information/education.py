import re 
import spacy

def extraire_education(texte_cv):
    nlp = spacy.load('fr_core_news_lg')

    # Charger les mots clés de diplômes depuis fichier externe
    with open('C:/Users/Lukas/Downloads/Analyseur-CV-main/Analyseur-CV-main/Data/education.txt', 'r', encoding='utf-8') as f:
        mots_cles_education = [mot.strip().lower() for mot in f.readlines() if mot.strip()]

    lignes = [l.strip() for l in texte_cv.split('\n') if l.strip()]

    date_pattern = re.compile(r'\b(19|20)\d{2}(?:\s*[-/\u2013]\s*(?:19|20)?\d{2})?\b')

    mots_ecole = [
        'école', 'université', 'lycée', 'institut', 'centre', 'fac', 'collège',
        'formation', 'cnam', 'fst', 'greta', 'cned', 'eni', 'campus'
    ]

    mots_interdits = [
        'stage', 'expérience', 'freelance', 'support', 'logiciel', 'application', 'développement',
        'windev', 'webdev', 'dreamweaver', 'html', 'php', 'ah.com', 'hfsql', 'facturation', 'gestion',
        'fonction', 'fonctionnalité', 'ms-dos', 'linux', 'windows', 'support', 'comptabilité',
        'journal caisse', 'rapport', 'formateur', 'guide', 'tunisienne', 'modules', 'missions',
        'boutiques', 'magasins', 'stations', 'automobiles', 'dossiers maritimes', 'paie', 'import-export',
        'musculation', 'calisthenics', 'course', 'facteur', 'professeur'
    ]

    def est_ligne_vide_ou_vague(texte):
        mots_vides = {'formation', 'formations', 'cours', 'stage', 'stages', 'séminaire', 'atelier', '-', '•', '—'}
        return texte.strip().lower() in mots_vides

    def nettoyer_texte(texte):
        texte = re.sub(r'^[•\-\:\s]+', '', texte)
        texte = re.sub(r'\s{2,}', ' ', texte)
        return texte.strip()

    education = []

    for ligne_brute in lignes:
        ligne = nettoyer_texte(ligne_brute)
        ligne_lower = ligne.lower()

        if est_ligne_vide_ou_vague(ligne) or any(m in ligne_lower for m in mots_interdits):
            continue

        # Extraction date
        date_match = date_pattern.search(ligne)
        date = date_match.group(0) if date_match else "Inconnu"

        # Extraction école : entité ORG spaCy prioritaire
        doc = nlp(ligne)
        ecole = "Inconnu"
        for ent in doc.ents:
            if ent.label_ == "ORG":
                ecole = ent.text.strip()
                break

        # Si pas trouvé, chercher mots-clés école dans la ligne
        if ecole == "Inconnu":
            for mot in mots_ecole:
                if mot in ligne_lower:
                    ecole = ligne.strip()
                    break

        # Extraction diplôme = ligne sans date ni école
        diplome = ligne
        if date != "Inconnu":
            diplome = diplome.replace(date, "")
        if ecole != "Inconnu" and ecole in diplome:
            diplome = diplome.replace(ecole, "")
        diplome = nettoyer_texte(diplome)

        if not diplome:
            diplome = "Inconnu"

        # On ajoute uniquement si au moins 2 infos sont valides
        nb_infos = sum([date != "Inconnu", ecole != "Inconnu", diplome != "Inconnu"])
        if nb_infos >= 2:
            education.append({
                "date": date,
                "ecole": ecole,
                "diplome": diplome
            })

    return education