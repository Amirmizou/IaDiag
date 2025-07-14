<<<<<<< HEAD
# Diag
=======
>>>>>>> 10caec8 (Initial commit: ready for Render deployment)
# Medical Diagnosis AI

Application web de diagnostic médical assisté par intelligence artificielle utilisant le modèle MedGemma de Google pour l'analyse d'images médicales et de symptômes.

## 🚀 Fonctionnalités

- **Diagnostic IA** : Analyse d'images médicales et de symptômes avec MedGemma 4B
- **Authentification** : Système de connexion avec rôles (admin, médecin, utilisateur)
- **Gestion des diagnostics** : Création, validation et suivi des diagnostics
- **Rapports PDF** : Génération de rapports professionnels avec visualisation d'images
- **Interface moderne** : Design responsive avec Tailwind CSS
- **Base de données** : Stockage MongoDB avec gestion des utilisateurs et diagnostics

## 🛠️ Technologies utilisées

- **Backend** : Flask, Python 3.10
- **Base de données** : MongoDB avec PyMongo
- **IA** : Hugging Face MedGemma 4B
- **Stockage d'images** : Cloudinary
- **Frontend** : HTML, CSS (Tailwind), JavaScript
- **Rapports** : ReportLab pour PDF
- **Authentification** : Flask-Login, bcrypt

## 📋 Prérequis

- Python 3.10+
- MongoDB (local ou cloud)
- Compte Cloudinary
- Clé API Hugging Face

## 🚀 Déploiement sur Render

### Option 1 : Déploiement automatique avec render.yaml

1. **Forkez ce repository** sur GitHub
2. **Connectez-vous à Render** et créez un nouveau service web
3. **Liez votre repository** GitHub
4. **Render détectera automatiquement** le fichier `render.yaml` et configurera le service

### Option 2 : Déploiement manuel

1. **Créez un nouveau service web** sur Render
2. **Liez votre repository** GitHub
3. **Configurez les paramètres** :
   - **Build Command** : `pip install -r requirements.txt`
   - **Start Command** : `gunicorn app:app --config gunicorn.conf.py`
   - **Python Version** : `3.10.14`

### Variables d'environnement à configurer

Dans les paramètres de votre service Render, ajoutez ces variables d'environnement :

```bash
# Configuration Flask
SECRET_KEY=votre-clé-secrète-générée
FLASK_ENV=production

# Configuration MongoDB
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/
MONGO_DB_NAME=medical_diagnosis

# Configuration Cloudinary
CLOUDINARY_CLOUD_NAME=votre-cloud-name
CLOUDINARY_API_KEY=votre-api-key
CLOUDINARY_API_SECRET=votre-api-secret

# Configuration Hugging Face
HUGGINGFACE_API_KEY=votre-huggingface-api-key

# Configuration Admin
ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@medical-ai.com
ADMIN_PASSWORD=votre-mot-de-passe-admin
```

## 🏃‍♂️ Installation locale

### 1. Cloner le repository

```bash
git clone <votre-repo>
cd medical_diagnosis_app
```

### 2. Créer un environnement virtuel

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Configurer les variables d'environnement

Copiez `env_example.txt` vers `.env` et configurez vos variables :

```bash
cp env_example.txt .env
# Éditez .env avec vos valeurs
```

### 5. Démarrer l'application

```bash
python app.py
```

L'application sera accessible sur `http://localhost:5000`

## 📁 Structure du projet

```
medical_diagnosis_app/
├── app.py                 # Application Flask principale
├── database.py            # Service de base de données
├── models.py              # Modèles de données
├── auth.py                # Décorateurs d'authentification
├── report_generator.py    # Générateur de rapports PDF
├── requirements.txt       # Dépendances Python
├── render.yaml           # Configuration Render
├── gunicorn.conf.py      # Configuration Gunicorn
├── Procfile              # Procfile pour Render
├── runtime.txt           # Version Python
├── env_example.txt       # Variables d'environnement
├── static/               # Fichiers statiques
├── templates/            # Templates HTML
│   ├── admin/           # Interface administrateur
│   ├── doctor/          # Interface médecin
│   └── *.html           # Pages principales
└── uploads/             # Dossier d'upload (créé automatiquement)
```

## 🔐 Authentification

### Comptes par défaut

- **Admin** : `admin` / `admin123` (configurable via variables d'environnement)
- **Utilisateurs** : Création via l'interface d'inscription

### Rôles

- **Admin** : Gestion complète des utilisateurs et diagnostics
- **Médecin** : Validation et commentaires sur les diagnostics
- **Utilisateur** : Création de diagnostics et consultation de l'historique

## 📊 API Endpoints

### Authentification
- `POST /login` - Connexion
- `POST /register` - Inscription
- `GET /logout` - Déconnexion

### Diagnostics
- `POST /diagnose` - Créer un diagnostic
- `GET /get_diagnoses` - Lister les diagnostics
- `GET /get_diagnosis/<id>` - Obtenir un diagnostic
- `PUT /api/diagnoses/<id>/status` - Modifier le statut
- `GET /download_report/<id>` - Télécharger le rapport

### Administration
- `GET /admin` - Tableau de bord admin
- `GET /admin/users` - Gestion des utilisateurs
- `POST /admin/users/create` - Créer un utilisateur
- `PUT /admin/users/<id>` - Modifier un utilisateur
- `DELETE /admin/users/<id>` - Supprimer un utilisateur

### Compatibilité API
- `GET /api/diagnoses` - Endpoint de compatibilité
- `GET /api/diagnoses/<id>` - Endpoint de compatibilité
- `GET /api/diagnoses/<id>/report` - Endpoint de compatibilité

## 🏥 Utilisation

### 1. Connexion
- Accédez à l'application et connectez-vous
- Utilisez les identifiants admin par défaut ou créez un compte

### 2. Création de diagnostic
- Allez dans "Nouveau diagnostic"
- Uploadez une image médicale ou décrivez les symptômes
- L'IA analysera et générera un diagnostic

### 3. Validation (médecins)
- Les médecins peuvent valider/rejeter les diagnostics
- Ajout de commentaires médicaux
- Changement de statut

### 4. Rapports
- Téléchargement de rapports PDF individuels
- Rapports de synthèse pour tous les diagnostics
- Visualisation d'images dans les rapports

## 🔧 Configuration avancée

### MongoDB Atlas
1. Créez un cluster MongoDB Atlas
2. Obtenez votre URI de connexion
3. Configurez `MONGO_URI` dans les variables d'environnement

### Cloudinary
1. Créez un compte Cloudinary
2. Obtenez vos clés API
3. Configurez les variables `CLOUDINARY_*`

### Hugging Face
1. Créez un compte Hugging Face
2. Obtenez votre clé API
3. Configurez `HUGGINGFACE_API_KEY`

## 🚨 Sécurité

- **Mots de passe** : Hachés avec bcrypt
- **Sessions** : Gérées par Flask-Login
- **Authentification** : Requise pour toutes les routes sensibles
- **Validation** : Contrôle d'accès basé sur les rôles
- **Variables d'environnement** : Secrets stockés de manière sécurisée

## 📝 Logs et monitoring

### Health Check
- Endpoint : `GET /health`
- Retourne le statut de l'application

### Logs Render
- Accessibles dans le dashboard Render
- Logs d'application et d'erreurs

## 🐛 Dépannage

### Erreurs courantes

1. **Erreur de connexion MongoDB**
   - Vérifiez `MONGO_URI`
   - Assurez-vous que l'IP est autorisée

2. **Erreur Cloudinary**
   - Vérifiez les clés API
   - Assurez-vous que le compte est actif

3. **Erreur Hugging Face**
   - Vérifiez `HUGGINGFACE_API_KEY`
   - Assurez-vous d'avoir des crédits suffisants

4. **Erreur de génération PDF**
   - Vérifiez les permissions d'écriture
   - Assurez-vous que ReportLab est installé

### Support

Pour toute question ou problème :
1. Vérifiez les logs dans Render
2. Consultez la documentation des services utilisés
3. Créez une issue sur GitHub

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
1. Fork le projet
2. Créer une branche pour votre fonctionnalité
3. Commiter vos changements
4. Pousser vers la branche
5. Ouvrir une Pull Request

## 📞 Contact

Pour toute question ou suggestion, n'hésitez pas à ouvrir une issue sur GitHub. # IaDiag
# IaDiag
# IaDiag
# IaDiag
