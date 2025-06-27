import re

def extraire_education(texte_cv):
    lignes = [l.strip() for l in texte_cv.split('\n') if l.strip()]
    date_pattern = re.compile(r'\b(?:\d{1,2}[/\-])?(19|20)\d{2}(?:\s*[-/\u2013]\s*(?:\d{1,2}[/\-])?(?:19|20)?\d{2})?\b')

    mots_ecole = ['école', 'université', 'lycée', 'institut', 'centre', 'fac', 'collège',
                 'formation', 'cnam', 'fst', 'greta', 'cned', 'eni', 'campus', 'upec', 'univ', 'iut']

    mots_interdits = [
        'stage', 'expérience', 'freelance', 'support', 'logiciel', 'application', 'développement',
        'windev', 'webdev', 'dreamweaver', 'html', 'php', 'ah.com', 'hfsql', 'facturation', 'gestion',
        'fonction', 'fonctionnalité', 'ms-dos', 'linux', 'windows', 'support', 'comptabilité',
        'journal caisse', 'rapport', 'formateur', 'guide', 'tunisienne', 'modules', 'missions',
        'boutiques', 'magasins', 'stations', 'automobiles', 'dossiers maritimes', 'paie', 'import-export',
        'musculation', 'calisthenics', 'course', 'facteur', 'professeur'
    ]

    mots_cles_valides = [
       'diplôme', 'certificat', 'formation', 'licence', 'master', 'bts',
       'baccalauréat', 'cap', 'bac', 'ingénieur', 'brevet', 'doctorat',
       'formation initiale', 'formation scolaire', 'obtention',
       'formations', 'concepteur', 'maîtrise',
       'technicien', 'apprentissage', 'qualification',
       'certification', 'diplômé', 'habilitation', 'stage diplômant',
       'cours', 'enseignement', 'universitaire', 'préparation',
       'parcours', 'spécialisation', 'éducation', 'grade', 'niveau',
       'programme', 'diplômante', 'atelier', 'seminaire', 'webinaire',
       'cycle', 'doctorat', 'mastère', 'DEA', 'DESS',
       'formation continue', 'formation professionnelle', 'module',
       'diplôme universitaire', 'diplôme d’état', 'certificat professionnel',
       'licence bilingue', 'licence langues', 'langues appliquées', 'LLCE', 'DEUG'
    ]

    def nettoyer(texte):
        texte = re.sub(r'^[•\-\:\s]+', '', texte)
        texte = re.sub(r'[:\-–•()]+', '', texte)
        texte = re.sub(r'\s{2,}', ' ', texte)
        return texte.strip()

    education = []
    i = 0
    n = len(lignes)

    while i < n:
        ligne = nettoyer(lignes[i])
        date_match = date_pattern.search(ligne)
        if date_match:
            date = date_match.group(0)

            # Diplôme supposé : ligne suivante si elle n'est pas une date
            diplome = "Inconnu"
            ecole = "Inconnu"
            if i+1 < n:
                next_line = nettoyer(lignes[i+1])
                if not date_pattern.search(next_line):
                    diplome = next_line
                    i += 1
                else:
                    diplome = "Inconnu"

            # École supposée : chercher mot clé école dans la ligne d'après le diplôme
            if i+1 < n:
                next_line = nettoyer(lignes[i+1])
                if any(mot in next_line.lower() for mot in mots_ecole):
                    ecole = next_line
                    i += 1

            texte_valide = f"{diplome} {ecole}".lower()
            if any(m in texte_valide for m in mots_cles_valides) and not any(m in texte_valide for m in mots_interdits):
                education.append({
                    "date": date,
                    "diplome": diplome,
                    "ecole": ecole
                })
                print(f"Formation détectée : {date} | {diplome} | {ecole}")

            i += 1  # avancer après le bloc traité
        else:
            i += 1  # pas de date, on continue

    return education
