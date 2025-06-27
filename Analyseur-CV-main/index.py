import os
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.constants import *
import xml.etree.ElementTree as ET

# Import des extracteurs
from information.prenom_nom import extraire_prenom_nom, contient_prenom_et_nom, nettoyer_texte
from information.education import extraire_education
from information.telephone import extraire_numero_telephone
from information.email import extraire_email
from information.competence import extraire_competences
from information.experiences import extraire_experiences
import lecteurfichiers.pdf2text as pdf2text


import xml.etree.ElementTree as ET

def generer_xml(nom, numero_telephone, email, education, competences, experiences, chemin_sortie):
    root = ET.Element("CV")

    # Identité
    identite = ET.SubElement(root, "Identite")
    ET.SubElement(identite, "Nom").text = str(nom) if nom else "Inconnu"
    ET.SubElement(identite, "Email").text = str(email) if email else "Inconnu"
    ET.SubElement(identite, "Telephone").text = str(numero_telephone) if numero_telephone else "Inconnu"

    # Formations
    formations = ET.SubElement(root, "Formations")
    for formation in education:
       formation_el = ET.SubElement(formations, "Formation")
       ET.SubElement(formation_el, "Date").text = formation.get("date", "Inconnu")
       ET.SubElement(formation_el, "Diplome").text = formation.get("diplome", "Inconnu")  # ici diplome
       ET.SubElement(formation_el, "Ecole").text = formation.get("ecole", "Inconnu")      # ici ecole

    # Compétences
    competences_xml = ET.SubElement(root, "Competences")
    for comp in competences:
        ET.SubElement(competences_xml, "Competence").text = str(comp).strip()

    # Expériences
    experiences_xml = ET.SubElement(root, "Experiences")
    for exp in experiences:
        exp_el = ET.SubElement(experiences_xml, "Experience")
        ET.SubElement(exp_el, "Date").text = exp.get("date", "Inconnu")
        ET.SubElement(exp_el, "Poste").text = exp.get("poste", "Inconnu")
        ET.SubElement(exp_el, "Entreprise").text = exp.get("entreprise", "Inconnu")
        ET.SubElement(exp_el, "Description").text = exp.get("description", "Inconnu")

    # Écriture du fichier
    tree = ET.ElementTree(root)
    tree.write(chemin_sortie, encoding="utf-8", xml_declaration=True)

def process(initial_filepath, root):
    from tkinter import filedialog as fd
    from tkinter import messagebox
    import re
    import time
    import os

    # Sélection du fichier PDF
    chemin_fichier = fd.askopenfilename(
        initialdir=initial_filepath,
        title='Sélectionner le fichier',
        filetypes=(('fichiers PDF', '*.pdf'),)
    )
    if not chemin_fichier:
        return

    # Extraction du texte du CV
    texte = pdf2text.get_Text(chemin_fichier)

    # Création du dossier output s’il n’existe pas
    dossier_output = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(dossier_output, exist_ok=True)

    # Sauvegarde du texte brut dans un fichier rapport
    chemin_rapport = os.path.join(dossier_output, "rapport_analyse_cv.txt")
    with open(chemin_rapport, "w", encoding="utf-8") as f:
        f.write(texte)

    # Affichage d'un extrait du texte dans le terminal
    print("------ TEXTE BRUT EXTRAIT ------")
    print(texte[:1000])
    print("------ FIN EXTRAIT TEXTE ------\n")

    # Extraction des informations
    nom = extraire_prenom_nom(texte)

    # ✅ Vérification finale du nom (anti bug "profil", "2009", etc.)
    nom_nettoye = nettoyer_texte(nom or "")
    if (
        not contient_prenom_et_nom(nom_nettoye)
        or any(char.isdigit() for char in nom_nettoye)
        or len(nom_nettoye.split()) > 5
    ):
        print("⚠️ Aucun nom/prénom fiable détecté, fallback vers email.")
        email_brut = extraire_email(texte)
        if email_brut:
            prefix = email_brut.split('@')[0].lower()
            generic_keywords = ["contact", "commercial", "info", "service", "admin", "support"]
            if any(k in prefix for k in generic_keywords):
                nom = None
            else:
                nom = prefix.replace('.', ' ').replace('_', ' ').title()
        else:
            nom = None



    numero_telephone = extraire_numero_telephone(texte)
    email = extraire_email(texte)
    education = extraire_education(texte)
    competences = extraire_competences(texte)
    experiences = extraire_experiences(texte)

    # Nettoyage et génération du nom de fichier XML sécurisé
    if nom:
       nom_clean = re.sub(r'[^a-zA-Z0-9_-]', '_', nom)
       if len(nom_clean) < 3:
        # fallback vers l’email
          email_brut = email or extraire_email(texte)
          prefix = email_brut.split('@')[0] if email_brut else 'inconnu'
          nom_clean = f"inconnu_{prefix}"
    else:
      email_brut = email or extraire_email(texte)
      prefix = email_brut.split('@')[0] if email_brut else 'inconnu'
      nom_clean = f"inconnu_{prefix}"


    nom_fichier_xml = f"{nom_clean}.xml"
    chemin_sortie = os.path.join(dossier_output, nom_fichier_xml)

    # Génération du fichier XML
    generer_xml(nom, numero_telephone, email, education, competences, experiences, chemin_sortie)

    # Message de confirmation
    messagebox.showinfo("Terminé", f"Fichier XML généré dans :\n{chemin_sortie}")


if __name__ == '__main__':
    largeur = 600
    hauteur = 300

    root = tk.Tk()
    root.title("Analyseur de CV")

    largeur_ecran = root.winfo_screenwidth()
    hauteur_ecran = root.winfo_screenheight()
    x = (largeur_ecran / 2) - (largeur / 2)
    y = (hauteur_ecran / 2) - (hauteur / 2)

    root.geometry(f"{largeur}x{hauteur}+{int(x)}+{int(y)}")

    label_chargement = ttk.Label(root, text="Chargement…")
    label_chargement.pack_forget()  # Caché au départ

    def lancer_process():
        label_chargement.pack(fill=X)
        root.update_idletasks()  # force l’affichage immédiat du label
        process('.', root)
        label_chargement.pack_forget()

    bouton = ttk.Button(root, text='Parcourir le fichier', command=lancer_process)
    bouton.pack(fill=X)

    root.mainloop()

