import re
from spacy import load
from spacy.matcher import Matcher
import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def charger_liste_noms_depuis_fichier(fichier_noms):
    noms = set()
    with open(fichier_noms, encoding='utf-8') as f:
        for line in f:
            if line.startswith("NOM") or not line.strip():
                continue
            nom = line.split('\t')[0].strip().lower()
            if nom:
                noms.add(nom)
    return noms

def charger_liste_prenoms_depuis_insee(fichier_prenoms):
    df = pd.read_csv(fichier_prenoms, sep='\t', encoding='utf-8', dtype=str)
    df = df[df['preusuel'] != '_PRENOMS_RARES']
    prenoms = set(df['preusuel'].str.lower().unique())
    return prenoms

LISTE_NOMS = charger_liste_noms_depuis_fichier(os.path.join(BASE_DIR, 'C:/Users/Lukas/Downloads/Analyseur-CV-main/Analyseur-CV-main/Data/noms.txt'))
LISTE_PRENOMS = charger_liste_prenoms_depuis_insee(os.path.join(BASE_DIR, 'C:/Users/Lukas/Downloads/Analyseur-CV-main/Analyseur-CV-main/Data/prenoms.txt'))

GENERIC_EMAIL_KEYWORDS = ["contact", "commercial", "info", "service", "admin", "support"]

def est_prenom(mot):
    mot = mot.lower().replace('-', '').replace('_', '')
    return mot in LISTE_PRENOMS

def est_nom(mot):
    mot = mot.lower().replace('-', '').replace('_', '')
    return mot in LISTE_NOMS

def is_email_generic(email):
    email = email.lower()
    return any(k in email for k in GENERIC_EMAIL_KEYWORDS)

def nettoyer_texte(texte):
    # Enlever caractères spéciaux superflus autour des mots
    return re.sub(r'[^a-zA-ZÀ-ÿ\s\-]', '', texte)

def contient_prenom_et_nom(chaine):
    mots = chaine.lower().split()
    return any(est_prenom(m) for m in mots) and any(est_nom(m) for m in mots)

def extraire_prenom_nom(texte_cv):
    nlp = load('fr_core_news_sm')
    doc = nlp(texte_cv)
    matcher = Matcher(nlp.vocab)

    # Blacklist globale
    blacklist = {
        "profil", "compétences", "formation", "expériences", "contact",
        "email", "téléphone", "adresse", "loisirs", "centre", "intérêt",
        "objectifs", "linkedin", "github"
    }

    # 1. Extraction prénom/nom depuis email (si email perso)
    email_match = re.search(r'([\w.-]+)@', texte_cv)
    email_prenom, email_nom = None, None
    if email_match:
        prefix = email_match.group(1)
        if not is_email_generic(prefix):
            parts = re.split(r'[._\-]', prefix)
            if len(parts) >= 2:
                email_prenom = parts[0].capitalize()
                email_nom = parts[1].capitalize()
            elif len(prefix) > 5:
                email_prenom = prefix[:1].upper() + prefix[1:]
                email_nom = ""
    email_fullname = f"{email_prenom or ''} {email_nom or ''}".strip()

    # 2. Lignes majuscules consécutives
    lignes = [l.strip() for l in texte_cv.splitlines() if l.strip()]
    candidats_lignes = []
    for i in range(len(lignes) - 1):
        l1, l2 = lignes[i], lignes[i + 1]
        if l1.isupper() and l2.isupper():
            phrase = f"{l1} {l2}"
            phrase_clean = nettoyer_texte(phrase)
            if len(phrase_clean.split()) < 2 or len(phrase_clean.split()) > 6:
                continue
            if any(char.isdigit() for char in phrase_clean):
                continue
            if any(m.lower() in blacklist for m in phrase_clean.lower().split()):
                continue
            if contient_prenom_et_nom(phrase_clean):
                candidats_lignes.append(phrase_clean)
    if candidats_lignes:
        if email_prenom and email_nom:
            for c in candidats_lignes:
                if email_prenom.lower() in c.lower() and email_nom.lower() in c.lower():
                    return c
        return candidats_lignes[0]

    # 3. Lignes simples
    for ligne in lignes:
        ligne_nettoyee = nettoyer_texte(ligne)
        mots = ligne_nettoyee.split()
        if len(mots) >= 2:
            if any(est_prenom(m) for m in mots) and any(est_nom(m) for m in mots):
                if email_prenom and email_nom:
                    if email_prenom.lower() in ligne.lower() and email_nom.lower() in ligne.lower():
                        if contient_prenom_et_nom(ligne):
                            return ligne
                else:
                    if contient_prenom_et_nom(ligne):
                        return ligne

    # 4. SpaCy + filtrage
    motif_2 = [{'POS': 'PROPN'}, {'POS': 'PROPN'}]
    motif_3 = [{'POS': 'PROPN'}] * 3
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
        if any(est_prenom(t) for t in tokens) and any(est_nom(t) for t in tokens):
            bonus = 0
            if email_prenom and email_prenom.lower() in segment.text.lower():
                bonus += 1
            if email_nom and email_nom.lower() in segment.text.lower():
                bonus += 1
            candidats.append((segment_clean, bonus))
    if candidats:
        candidats = sorted(candidats, key=lambda x: (-x[1], len(x[0])))
        for c, _ in candidats:
            if contient_prenom_et_nom(c):
                return c

    # 5. Fallback : email
    if email_fullname and contient_prenom_et_nom(email_fullname):
        return email_fullname

    return None


