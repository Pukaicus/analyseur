README - Analyseur de CV en Python

Description du projet
Ce projet est un analyseur automatique de CV en PDF (texte non scanné) développé en Python. Il permet d’extraire plusieurs informations clés telles que :

Identité (prénom, nom, email, téléphone)

Compétences

Formations

Langues

Expériences professionnelles

Les données extraites sont ensuite structurées dans un fichier XML. Un rapport d’analyse détaillé est aussi généré pour vérifier le contenu extrait.

L’outil inclut une interface graphique simple permettant de sélectionner un fichier CV ou un dossier entier.

Prérequis
Python 3.8 ou supérieur

Librairies Python à installer :
pip install -r requirements.txt
pip install spacy lxml
Modèle spaCy français (large) :

python -m spacy download fr_core_news_lg
Fichiers de données externes (à placer dans le dossier Data)
Le projet utilise plusieurs fichiers texte servant de base pour les extractions. Les chemins vers ces fichiers ont été modifiés dans le code selon votre organisation locale :

Fichier	Utilisation	Chemin dans le code
education.txt	Mots-clés formations/diplômes	dans education.py
prenoms.txt	Base des prénoms	dans prenom_nom.py
noms.txt	Base des noms de famille	dans prenom_nom.py
skills_db.txt	Base des compétences métiers	dans competences.py

Fonctionnement global
Lancement
Le script principal (par exemple index.py) lance une interface graphique (Tkinter).

Sélection du fichier ou dossier
L’utilisateur choisit soit un fichier PDF unique, soit un dossier contenant plusieurs CV.

Analyse
Le programme extrait ligne par ligne toutes les informations importantes avec spaCy, regex et mots-clés.

Rapport d’analyse
Un fichier texte (ex: rapport_analyse_cv.txt) est généré, détaillant tout ce qui a été détecté, pour faciliter la vérification.

Export XML
Les données extraites sont enregistrées dans un fichier XML structuré dans un dossier output/ pour chaque CV analysé.

Notes importantes
Les fichiers de données (education.txt, prenoms.txt, etc.) doivent être à jour et correctement placés pour assurer la bonne reconnaissance.

Le projet est conçu pour des PDF contenant du texte « sélectionnable » (non scanné).

L’analyse est effectuée principalement ligne par ligne et en blocs de 2 ou 3 lignes pour détecter les formations, expériences, etc.

Certains faux positifs peuvent apparaître ; le rapport d’analyse permet de détecter ces cas et d’ajuster les listes ou règles.

Organisation du projet
Analyseur-CV/
├── Data/
│   ├── education.txt
│   ├── prenoms.txt
│   ├── noms.txt
│   └── skills_db.txt
├── extraction/
│   ├── education.py
│   ├── prenom_nom.py
│   ├── competences.py
│   ├── experiences.py
│   └── langues.py
├── output/
│   └── (fichiers XML générés)
├── index.py
├── rapport_analyse_cv.txt
└── README.md
Personnalisation
Les chemins vers les fichiers education.txt, prenoms.txt, noms.txt, skills_db.txt sont modifiables directement dans leurs fichiers .py respectifs (variables en début de fichier).

Les listes de mots-clés, mots interdits, et regex peuvent être ajustées dans les scripts pour améliorer la reconnaissance selon vos besoins.

Comment lancer le programme
python index.py
Une fenêtre s’ouvre pour sélectionner le CV ou dossier, puis l’analyse se lance automatiquement.

Contact / Support
Pour toute question ou problème, merci de me contacter ou d’ouvrir une issue sur le dépôt GitHub.