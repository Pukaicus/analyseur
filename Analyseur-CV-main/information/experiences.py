import re
import spacy

def extraire_experiences(texte_cv):
    # Chargement du modèle linguistique français de spaCy (ici, pas encore utilisé dans la fonction)
    nlp = spacy.load("fr_core_news_lg")
    
    # Découpage du texte en lignes, suppression des lignes vides et espaces superflus
    lignes = [l.strip() for l in texte_cv.splitlines() if l.strip()]
    
    experiences = []  # Liste qui contiendra les expériences extraites
    
    # Expression régulière pour détecter des dates au format 4 chiffres (ex : 2021) ou intervalle (ex : 2021-2022)
    date_pattern = re.compile(r'\b(?:\d{4})(?:\s*[-/–]\s*(?:\d{4}|\d{2}))?\b', re.IGNORECASE)
    
    # Liste des mots clés correspondant à des postes connus (en minuscules)
    postes_connus = [
        "développeur", "ingénieur", "technicien", "analyste", "chef de projet",
        "formateur", "enseignant", "commercial", "consultant", "assistant",
        "facteur", "conseiller", "vendeur", "stagiaire", "freelance", "professeur",
        "stage", "alternance", "alternant"
    ]
    
    # Liste des mots associés à des noms d'entreprises ou structures
    mots_entreprise = ["sarl", "sas", "groupe", "entreprise", "société", "agence", "banque", "poste", "edf", "bnp", "orange"]
    
    # Mots indiquant que la ligne ne fait pas partie de l'expérience professionnelle (ex : compétences, formations...)
    mots_interdits = ["compétence", "langue", "formation", "éducation", "diplôme"]

    i = 0
    # Parcours ligne par ligne du texte du CV
    while i < len(lignes):
        ligne = lignes[i]
        ligne_lower = ligne.lower()

        # Si la ligne contient un poste connu ET une date
        if any(poste in ligne_lower for poste in postes_connus) and re.search(date_pattern, ligne_lower):
            # Extraction de la date détectée
            date = re.search(date_pattern, ligne_lower).group(0)

            # Recherche du premier poste connu dans la ligne et mise en forme avec majuscule
            poste = next((p.title() for p in postes_connus if p in ligne_lower), "Inconnu")

            entreprise = ''
            # Recherche d'un mot lié à une entreprise sur la ligne ou la suivante
            if any(m in ligne_lower for m in mots_entreprise):
                entreprise = ligne
            elif i + 1 < len(lignes):
                ligne_suivante = lignes[i + 1].lower()
                if any(m in ligne_suivante for m in mots_entreprise):
                    entreprise = lignes[i + 1]

            description = ligne
            j = 1
            # Ajout jusqu'à 3 lignes suivantes dans la description si elles ne contiennent pas de mots interdits ni de dates
            while i + j < len(lignes) and j <= 3:
                ligne_suivante = lignes[i + j]
                if any(m in ligne_suivante.lower() for m in mots_interdits) or re.search(date_pattern, ligne_suivante):
                    break
                # On ajoute la ligne suivante à la description si elle contient plus de 2 mots
                if len(ligne_suivante.split()) > 2:
                    description += " " + ligne_suivante.strip()
                j += 1

            # Nettoyage des espaces multiples dans la description
            description = re.sub(r'\s+', ' ', description.strip())
            # Retirer le nom de l'entreprise de la description s'il y est inclus (éviter répétition)
            entreprise = entreprise.replace(description, '').strip() if entreprise and entreprise in description else entreprise

            # Ajout de l'expérience extraite dans la liste
            experiences.append({
                "date": date,
                "poste": poste,
                "entreprise": entreprise or "Inconnu",
                "description": description[:200]  # Limite de la description à 200 caractères pour la sécurité
            })
            i += j  # On avance de j lignes car on a traité plusieurs lignes
        else:
            i += 1  # Sinon, on passe à la ligne suivante

    return experiences
