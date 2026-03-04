# Projet Collaboration Designer & Developper

Ce projet est une application web développée en Python (probablement avec Flask) permettant la gestion de la collaboration autour de la conception et du développement de designs.

## Fonctionnalités principales
- Authentification des utilisateurs (connexion, inscription)
- Gestion des designs
- Téléversement de fichiers
- Interface utilisateur moderne avec CSS et JavaScript

## Structure du projet
```
├── authoriser.py
├── config.py
├── requirements.txt
├── run.py
├── structure.txt
├── app/
│   ├── __init__.py
│   ├── auth.py
│   ├── designs.py
│   ├── extensions.py
│   ├── static/
│   │   ├── css/style.css
│   │   └── js/script.js
│   └── templates/
│       ├── index.html
│       ├── login.html
│       └── register.html
└── static/uploads/
```

## Installation
1. Cloner le dépôt :
   ```bash
   git clone <url-du-repo>
   ```
2. Installer les dépendances :
   ```bash
   pip install -r requirements.txt
   ```
3. Lancer l’application :
   ```bash
   python run.py
   ```

## Utilisation
- Accéder à l’application via votre navigateur à l’adresse indiquée dans la console.
- S’inscrire ou se connecter pour accéder aux fonctionnalités de gestion des designs.

## Dossiers importants
- `app/static/` : Fichiers statiques (CSS, JS)
- `app/templates/` : Templates HTML
- `static/uploads/` : Fichiers téléversés

## Auteur
Projet réalisé dans le cadre du cours de 5ème année, Semestre 1, Dr Tchana.

## Licence
Ce projet est sous licence MIT (à adapter selon vos besoins).
