import re
from spacy import load
from spacy.matcher import Matcher
import os
import pandas as pd

# Récupération du dossier du script courant (utile pour construire des chemins relatifs)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def charger_liste_noms_depuis_fichier(fichier_noms):
    """
    Charge une liste de noms depuis un fichier texte.
    Ignore les lignes vides ou celles commençant par "NOM" (entête).
    Retourne un ensemble de noms en minuscules.
    """
    noms = set()
    with open(fichier_noms, encoding='utf-8') as f:
        for line in f:
            if line.startswith("NOM") or not line.strip():
                continue
            nom = line.split('\t')[0].strip().lower()  # Premier champ avant tabulation
            if nom:
                noms.add(nom)
    return noms

def charger_liste_prenoms_depuis_insee(fichier_prenoms):
    """
    Charge une liste de prénoms depuis un fichier CSV INSEE.
    Filtre les prénoms rares et renvoie un ensemble de prénoms en minuscules.
    """
    df = pd.read_csv(fichier_prenoms, sep='\t', encoding='utf-8', dtype=str)
    df = df[df['preusuel'] != '_PRENOMS_RARES']
    prenoms = set(df['preusuel'].str.lower().unique())
    return prenoms

# Chargement des listes de noms et prénoms depuis fichiers externes
LISTE_NOMS = charger_liste_noms_depuis_fichier(os.path.join(BASE_DIR, 'C:/Users/Lukas/Downloads/Analyseur-CV-main/Analyseur-CV-main/Data/noms.txt'))
LISTE_PRENOMS = charger_liste_prenoms_depuis_insee(os.path.join(BASE_DIR, 'C:/Users/Lukas/Downloads/Analyseur-CV-main/Analyseur-CV-main/Data/prenoms.txt'))

# Mots-clés souvent présents dans des emails génériques à ignorer
GENERIC_EMAIL_KEYWORDS = ["contact", "commercial", "info", "service", "admin", "support"]

def est_prenom(mot):
    """
    Vérifie si un mot correspond à un prénom de la liste, après nettoyage.
    """
    mot = mot.lower().replace('-', '').replace('_', '')
    return mot in LISTE_PRENOMS

def est_nom(mot):
    """
    Vérifie si un mot correspond à un nom de la liste, après nettoyage.
    """
    mot = mot.lower().replace('-', '').replace('_', '')
    return mot in LISTE_NOMS

def is_email_generic(email):
    """
    Indique si une adresse email semble générique (par ses mots clés).
    """
    email = email.lower()
    return any(k in email for k in GENERIC_EMAIL_KEYWORDS)

def nettoyer_texte(texte):
    """
    Nettoie un texte en supprimant les caractères non alphabétiques (sauf accents, espaces et tirets).
    Utile pour éviter les erreurs sur les noms.
    """
    return re.sub(r'[^a-zA-ZÀ-ÿ\s\-]', '', texte)

def contient_prenom_et_nom(chaine):
    """
    Indique si une chaîne contient au moins un prénom ET un nom reconnus.
    """
    mots = chaine.lower().split()
    return any(est_prenom(m) for m in mots) and any(est_nom(m) for m in mots)

def extraire_prenom_nom(texte_cv):
    """
    Fonction principale d'extraction du prénom et nom dans un texte de CV.
    Utilise plusieurs heuristiques pour identifier la bonne ligne ou segment.
    """

    # Chargement du modèle spaCy français léger (sm)
    nlp = load('fr_core_news_sm')
    doc = nlp(texte_cv)
    matcher = Matcher(nlp.vocab)

    # Liste noire de mots interdits dans les segments candidats
    blacklist = {
        "profil", "compétences", "formation", "expériences", "contact",
        "email", "téléphone", "adresse", "loisirs", "centre", "intérêt",
        "objectifs", "linkedin", "github"
    }

    # 1. Extraction du prénom/nom à partir de l'email si ce n'est pas un email générique
    email_match = re.search(r'([\w.-]+)@', texte_cv)
    email_prenom, email_nom = None, None
    if email_match:
        prefix = email_match.group(1)  # Partie avant @
        if not is_email_generic(prefix):
            # Découpage du préfixe email en morceaux pour isoler prénom/nom
            parts = re.split(r'[._\-]', prefix)
            if len(parts) >= 2:
                email_prenom = parts[0].capitalize()
                email_nom = parts[1].capitalize()
            elif len(prefix) > 5:
                # Cas où on a un seul mot assez long, on suppose que c'est un prénom
                email_prenom = prefix[:1].upper() + prefix[1:]
                email_nom = ""
    email_fullname = f"{email_prenom or ''} {email_nom or ''}".strip()

    # 2. Recherche des lignes consécutives entièrement en majuscules (souvent prénom + nom)
    lignes = [l.strip() for l in texte_cv.splitlines() if l.strip()]
    candidats_lignes = []
    for i in range(len(lignes) - 1):
        l1, l2 = lignes[i], lignes[i + 1]
        # Teste si deux lignes consécutives sont en majuscules
        if l1.isupper() and l2.isupper():
            phrase = f"{l1} {l2}"
            phrase_clean = nettoyer_texte(phrase)
            # Ignore phrases trop courtes ou trop longues
            if len(phrase_clean.split()) < 2 or len(phrase_clean.split()) > 6:
                continue
            # Ignore phrases contenant des chiffres
            if any(char.isdigit() for char in phrase_clean):
                continue
            # Ignore phrases contenant un mot de la blacklist
            if any(m.lower() in blacklist for m in phrase_clean.lower().split()):
                continue
            # Vérifie si la phrase contient un prénom et un nom reconnus
            if contient_prenom_et_nom(phrase_clean):
                candidats_lignes.append(phrase_clean)
    # Si on a trouvé des candidats lignes, on essaie d'abord de matcher avec email, sinon on retourne le premier
    if candidats_lignes:
        if email_prenom and email_nom:
            for c in candidats_lignes:
                if email_prenom.lower() in c.lower() and email_nom.lower() in c.lower():
                    return c
        return candidats_lignes[0]

    # 3. Recherche sur les lignes simples (une seule ligne)
    for ligne in lignes:
        ligne_nettoyee = nettoyer_texte(ligne)
        mots = ligne_nettoyee.split()
        if len(mots) >= 2:
            if any(est_prenom(m) for m in mots) and any(est_nom(m) for m in mots):
                # Si email prénom/nom connu, on vérifie la présence dans la ligne
                if email_prenom and email_nom:
                    if email_prenom.lower() in ligne.lower() and email_nom.lower() in ligne.lower():
                        if contient_prenom_et_nom(ligne):
                            return ligne
                else:
                    if contient_prenom_et_nom(ligne):
                        return ligne

    # 4. Recherche avec spaCy Matcher : deux ou trois noms propres consécutifs
    motif_2 = [{'POS': 'PROPN'}, {'POS': 'PROPN'}]  # Deux noms propres consécutifs
    motif_3 = [{'POS': 'PROPN'}] * 3  # Trois noms propres consécutifs
    matcher.add('NOM', [motif_2, motif_3])
    candidats = []
    for _, start, end in matcher(doc):
        segment = doc[start:end]
        tokens = [t.text.lower() for t in segment]
        segment_clean = nettoyer_texte(segment.text)
        if len(segment_clean.split()) < 2 or len(segment_clean.split()) > 6:
            continue
        if any(char.isdigit() for char in segment_clean):
            continue
        if any(m in blacklist for m in segment_clean.lower().split()):
            continue
        # Vérifie présence prénom et nom dans le segment
        if any(est_prenom(t) for t in tokens) and any(est_nom(t) for t in tokens):
            bonus = 0
            # Bonus si prénom/nom correspond à celui extrait de l'email
            if email_prenom and email_prenom.lower() in segment.text.lower():
                bonus += 1
            if email_nom and email_nom.lower() in segment.text.lower():
                bonus += 1
            candidats.append((segment_clean, bonus))
    # Tri des candidats par bonus (descendant) puis par longueur (ascendant)
    if candidats:
        candidats = sorted(candidats, key=lambda x: (-x[1], len(x[0])))
        for c, _ in candidats:
            if contient_prenom_et_nom(c):
                return c

    # 5. En dernier recours, retourne le prénom et nom extrait de l'email si valide
    if email_fullname and contient_prenom_et_nom(email_fullname):
        return email_fullname

    # Si rien trouvé, retourne None
    return None
