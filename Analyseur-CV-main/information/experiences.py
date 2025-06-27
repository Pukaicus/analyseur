import re
import spacy

def extraire_experiences(texte_cv):
    nlp = spacy.load("fr_core_news_lg")
    lignes = [l.strip() for l in texte_cv.splitlines() if l.strip()]
    experiences = []

    date_pattern = re.compile(r'\b(?:\d{4})(?:\s*[-/–]\s*(?:\d{4}|\d{2}))?\b', re.IGNORECASE)
    postes_connus = [
        "développeur", "ingénieur", "technicien", "analyste", "chef de projet",
        "formateur", "enseignant", "commercial", "consultant", "assistant",
        "facteur", "conseiller", "vendeur", "stagiaire", "freelance", "professeur",
        "stage", "alternance", "alternant"
    ]
    mots_entreprise = ["sarl", "sas", "groupe", "entreprise", "société", "agence", "banque", "poste", "edf", "bnp", "orange"]
    mots_interdits = ["compétence", "langue", "formation", "éducation", "diplôme"]

    i = 0
    while i < len(lignes):
        ligne = lignes[i]
        ligne_lower = ligne.lower()

        if any(poste in ligne_lower for poste in postes_connus) and re.search(date_pattern, ligne_lower):
            date = re.search(date_pattern, ligne_lower).group(0)

            poste = next((p.title() for p in postes_connus if p in ligne_lower), "Inconnu")

            entreprise = ''
            if any(m in ligne_lower for m in mots_entreprise):
                entreprise = ligne
            elif i + 1 < len(lignes):
                ligne_suivante = lignes[i + 1].lower()
                if any(m in ligne_suivante for m in mots_entreprise):
                    entreprise = lignes[i + 1]

            description = ligne
            j = 1
            while i + j < len(lignes) and j <= 3:
                ligne_suivante = lignes[i + j]
                if any(m in ligne_suivante.lower() for m in mots_interdits) or re.search(date_pattern, ligne_suivante):
                    break
                if len(ligne_suivante.split()) > 2:
                    description += " " + ligne_suivante.strip()
                j += 1

            description = re.sub(r'\s+', ' ', description.strip())
            entreprise = entreprise.replace(description, '').strip() if entreprise and entreprise in description else entreprise

            experiences.append({
                "date": date,
                "poste": poste,
                "entreprise": entreprise or "Inconnu",
                "description": description[:200]  # limite de sécurité
            })
            i += j
        else:
            i += 1

    return experiences
