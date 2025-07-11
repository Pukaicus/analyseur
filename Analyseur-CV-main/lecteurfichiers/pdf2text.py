import re
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
import io

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as fh:
        for page in PDFPage.get_pages(fh, caching=True, check_extractable=True):
            resource_manager = PDFResourceManager()
            fake_file_handle = io.StringIO()
            converter = TextConverter(resource_manager, fake_file_handle, codec='utf-8', laparams=LAParams())
            page_interpreter = PDFPageInterpreter(resource_manager, converter)
            page_interpreter.process_page(page)
            text = fake_file_handle.getvalue()
            yield text
            converter.close()
            fake_file_handle.close()

def get_Text(filePath):
    text = ""
    for page in extract_text_from_pdf(filePath):
        text += '\n' + page
    return text


def extraire_formations(texte):
    lignes = [l.strip() for l in texte.split('\n') if l.strip()]
    formations = []
    date_pattern = re.compile(r'\b(19|20)\d{2}(?:[-/–]\s*(?:19|20)?\d{2})?\b')

    i = 0
    while i < len(lignes):
        ligne = lignes[i]
        date_match = date_pattern.search(ligne)

        if date_match:
            date = date_match.group(0)

            if len(ligne.split()) > 4:  # ligne assez longue
                contenu = ligne.replace(date, '').strip()
                contenu = re.sub(r'^[•:\-–\(\)]*', '', contenu)

                if '-' in contenu:
                    parts = contenu.split('-')
                    diplome = parts[0].strip()
                    ecole = '-'.join(parts[1:]).strip()
                else:
                    diplome = contenu.strip()
                    ecole = "Inconnu"

                formations.append({
                    "date": date,
                    "diplome": ecole if ecole else "Inconnu",    # inversion ici
                    "ecole": diplome if diplome else "Inconnu"   # inversion ici
                })
                i += 1

            else:
                diplome = lignes[i + 1].strip() if i + 1 < len(lignes) else "Inconnu"
                ecole = lignes[i + 2].strip() if i + 2 < len(lignes) else "Inconnu"

                formations.append({
                    "date": date,
                    "diplome": ecole if ecole else "Inconnu",    # inversion ici
                    "ecole": diplome if diplome else "Inconnu"   # inversion ici
                })
                i += 3
        else:
            i += 1

    return formations

# --- Regroupe les lignes d'une même expérience ---
def regrouper_experiences(lignes):
    experiences = []
    buffer = []
    debut_experience_pattern = re.compile(r'\b(19|20)\d{2}\b.*(stage|emploi|contrat|cdd|intérim|job|mission)?', re.IGNORECASE)

    for ligne in lignes:
        if not ligne.strip():
            # Fin d'un bloc
            if buffer:
                experiences.append(' '.join(buffer).replace('\n', ' ').strip())
                buffer = []
            continue

        if debut_experience_pattern.match(ligne):
            if buffer:
                experiences.append(' '.join(buffer).replace('\n', ' ').strip())
                buffer = []
            buffer.append(ligne.strip())
        else:
            buffer.append(ligne.strip())

    if buffer:
        experiences.append(' '.join(buffer).replace('\n', ' ').strip())

    return experiences

# --- Analyse un bloc d'expérience (date, entreprise, description) ---
def analyser_bloc_experience(bloc):
    date_pattern = re.compile(r'\b(19|20)\d{2}(?:[-/–]\d{2,4})?\b')
    date = "Inconnu"
    entreprise = "Inconnu"
    poste = "Inconnu"
    missions = []

    # Trouver date dans les 2 premières lignes
    for ligne in bloc[:2]:
        m = date_pattern.search(ligne)
        if m:
            date = m.group(0)
            break

    # Extraire ligne contenant le poste et entreprise (1ère ligne contenant un tiret)
    for ligne in bloc:
        if '-' in ligne:
            parties = ligne.split('-')
            poste = parties[0].strip()
            entreprise = '-'.join(parties[1:]).strip()
            break

    # Le reste = missions / description
    debut_missions = False
    for ligne in bloc:
        if poste in ligne or entreprise in ligne:
            debut_missions = True
            continue
        if debut_missions and ligne:
            missions.append(ligne)

    description = " ".join(missions).strip()

    return {
        "date": date,
        "poste": poste if poste else "Inconnu",
        "entreprise": entreprise if entreprise else "Inconnu",
        "description": description if description else "Inconnu"
    }


def extraire_experiences(texte):
    lignes = [l.strip() for l in texte.split('\n') if l.strip()]
    blocs = regrouper_experiences(lignes)
    experiences = [analyser_bloc_experience(bloc.split(' ')) for bloc in blocs]
    return experiences

# --- Fonction principale pour analyser un PDF et renvoyer dict ---
def analyser_pdf(pdf_path):
    texte = get_Text(pdf_path)
    formations = extraire_formations(texte)
    experiences = extraire_experiences(texte)
    return {
        "formations": formations,
        "experiences": experiences
    }

if __name__ == "__main__":
    fichier_pdf = "exemple.pdf"
    resultat = analyser_pdf(fichier_pdf)
    print("Formations:")
    for f in resultat["formations"]:
        print(f)
    print("\nExpériences:")
    for e in resultat["experiences"]:
        print(e)
