import re
import spacy

def extraire_experiences(texte_cv):
    nlp = spacy.load("fr_core_news_lg")
    lignes = [ligne.strip() for ligne in texte_cv.splitlines() if ligne.strip()]

    experiences = []
    date_pattern = re.compile(r'\b(19|20)\d{2}(?:\s*[-/–]\s*(?:19|20)?\d{2})?\b')

    postes_connus = [
        "développeur", "ingénieur", "technicien", "analyste", "chef de projet",
        "formateur", "enseignant", "commercial", "consultant", "assistant",
        "facteur", "conseiller", "vendeur", "stagiaire", "freelance", "professeur",
        "stage", "alternance", "alternant"
    ]

    mots_entreprise = ["sarl", "sas", "groupe", "entreprise", "société", "agence", "banque", "poste", "edf", "bnp", "orange"]

    for i, ligne in enumerate(lignes):
        ligne_lower = ligne.lower()

        # Critères pour détecter une expérience
        if any(m in ligne_lower for m in postes_connus) and re.search(date_pattern, ligne_lower):
            date_match = re.search(date_pattern, ligne_lower)
            date = date_match.group(0) if date_match else ''

            poste = ''
            for mot in postes_connus:
                if mot in ligne_lower:
                    poste = mot.title()
                    break

            # Essayer de détecter une entreprise dans la ligne ou la suivante
            entreprise = ''
            for mot in mots_entreprise:
                if mot in ligne_lower:
                    entreprise = ligne.strip()
                    break
            if not entreprise and i + 1 < len(lignes):
                ligne_suivante = lignes[i + 1].lower()
                if any(m in ligne_suivante for m in mots_entreprise):
                    entreprise = lignes[i + 1].strip()

            # Mini description = ligne de base (sans répétition)
            description = ligne
            if i + 1 < len(lignes):
                ligne_suivante = lignes[i + 1].strip()
                if len(ligne_suivante.split()) > 3 and not re.search(date_pattern, ligne_suivante):
                    description += " " + ligne_suivante

            # Nettoyage final
            description = re.sub(r'\s+', ' ', description.strip())
            entreprise = entreprise.replace(description, '').strip() if entreprise else ''
            
            experiences.append({
                "date": date,
                "poste": poste or "Inconnu",
                "entreprise": entreprise or "Inconnu",
                "description": description[:150]  # Limite pour éviter les pavés
            })

    return experiences
