# 🚀 Guide de déploiement sur Render

Ce guide vous accompagne étape par étape pour déployer l'application Medical Diagnosis AI sur Render.

## 📋 Prérequis

- Compte GitHub avec le code source
- Compte Render (gratuit disponible)
- Compte MongoDB Atlas (gratuit disponible)
- Compte Cloudinary (gratuit disponible)
- Clé API Hugging Face

## 🔧 Étape 1: Préparation du code

### 1.1 Vérifier les fichiers de configuration

Assurez-vous que tous ces fichiers sont présents dans votre repository :

```
medical_diagnosis_app/
├── app.py                 ✅ Application principale
├── requirements.txt       ✅ Dépendances Python
├── render.yaml           ✅ Configuration Render
├── gunicorn.conf.py      ✅ Configuration Gunicorn
├── Procfile              ✅ Procfile pour Render
├── runtime.txt           ✅ Version Python
├── .gitignore            ✅ Fichiers à ignorer
└── env_example.txt       ✅ Variables d'environnement
```

### 1.2 Tester localement

```bash
# Installer les dépendances
pip install -r requirements.txt

# Tester l'application
python app.py

# Vérifier l'endpoint de santé
curl http://localhost:5000/health
```

## 🌐 Étape 2: Configuration des services externes

### 2.1 MongoDB Atlas

1. **Créer un compte** sur [MongoDB Atlas](https://www.mongodb.com/atlas)
2. **Créer un cluster** gratuit (M0)
3. **Configurer l'accès réseau** :
   - Aller dans "Network Access"
   - Cliquer "Add IP Address"
   - Ajouter "0.0.0.0/0" (tous les IPs)
4. **Créer un utilisateur** :
   - Aller dans "Database Access"
   - Cliquer "Add New Database User"
   - Créer un utilisateur avec mot de passe
5. **Obtenir l'URI de connexion** :
   - Aller dans "Clusters"
   - Cliquer "Connect"
   - Choisir "Connect your application"
   - Copier l'URI

### 2.2 Cloudinary

1. **Créer un compte** sur [Cloudinary](https://cloudinary.com/)
2. **Aller dans le Dashboard**
3. **Noter les informations** :
   - Cloud Name
   - API Key
   - API Secret

### 2.3 Hugging Face

1. **Créer un compte** sur [Hugging Face](https://huggingface.co/)
2. **Aller dans Settings > Access Tokens**
3. **Créer un nouveau token**
4. **Copier le token**

## 🚀 Étape 3: Déploiement sur Render

### 3.1 Créer un nouveau service

1. **Aller sur** [Render Dashboard](https://dashboard.render.com/)
2. **Cliquer "New +"**
3. **Sélectionner "Web Service"**
4. **Connecter votre repository GitHub**

### 3.2 Configuration automatique (avec render.yaml)

Si vous avez un fichier `render.yaml`, Render détectera automatiquement la configuration :

```yaml
services:
  - type: web
    name: medical-diagnosis-ai
    env: python
    plan: starter
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn app:app
```

### 3.3 Configuration manuelle

Si vous n'utilisez pas `render.yaml`, configurez manuellement :

- **Name** : `medical-diagnosis-ai`
- **Environment** : `Python`
- **Build Command** : `pip install -r requirements.txt`
- **Start Command** : `gunicorn app:app --config gunicorn.conf.py`
- **Plan** : `Starter` (gratuit)

### 3.4 Variables d'environnement

Dans la section "Environment Variables", ajoutez :

```bash
# Configuration Flask
SECRET_KEY=votre-clé-secrète-très-longue
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
ADMIN_PASSWORD=votre-mot-de-passe-admin-securise
```

### 3.5 Générer une clé secrète

```bash
# Dans votre terminal
python -c "import secrets; print(secrets.token_hex(32))"
```

## 🔍 Étape 4: Vérification du déploiement

### 4.1 Surveiller le build

1. **Cliquer "Create Web Service"**
2. **Surveiller les logs de build**
3. **Attendre que le déploiement soit terminé**

### 4.2 Tester l'application

```bash
# Remplacer par votre URL Render
curl https://votre-app.onrender.com/health

# Réponse attendue
{"status": "healthy", "message": "Medical Diagnosis AI is running"}
```

### 4.3 Tester l'interface

1. **Aller sur votre URL Render**
2. **Vous devriez être redirigé vers `/login`**
3. **Se connecter avec** :
   - Username : `admin`
   - Password : `votre-mot-de-passe-admin`

## 🛠️ Étape 5: Configuration avancée

### 5.1 Domaines personnalisés

1. **Aller dans les paramètres du service**
2. **Section "Custom Domains"**
3. **Ajouter votre domaine**
4. **Configurer les DNS**

### 5.2 Variables d'environnement sensibles

Pour les variables sensibles, utilisez les "Secret Files" de Render :

1. **Aller dans "Environment"**
2. **Section "Secret Files"**
3. **Ajouter vos fichiers de configuration**

### 5.3 Monitoring et logs

- **Logs** : Accessibles dans l'onglet "Logs"
- **Metrics** : Disponibles dans l'onglet "Metrics"
- **Health checks** : Automatiques via `/health`

## 🚨 Dépannage

### Erreurs courantes

#### 1. Build échoue

```bash
# Vérifier les logs de build
# Erreur typique : dépendance manquante
```

**Solution** : Vérifier `requirements.txt` et les versions

#### 2. Application ne démarre pas

```bash
# Vérifier les logs d'application
# Erreur typique : variable d'environnement manquante
```

**Solution** : Vérifier toutes les variables d'environnement

#### 3. Erreur de connexion MongoDB

```
# Erreur : Connection refused
```

**Solution** :
- Vérifier l'URI MongoDB
- S'assurer que l'IP est autorisée dans Atlas
- Vérifier les credentials

#### 4. Erreur Cloudinary

```
# Erreur : Invalid credentials
```

**Solution** :
- Vérifier les clés API Cloudinary
- S'assurer que le compte est actif

#### 5. Erreur Hugging Face

```
# Erreur : Invalid API key
```

**Solution** :
- Vérifier la clé API Hugging Face
- S'assurer d'avoir des crédits suffisants

### Logs utiles

```bash
# Vérifier les logs en temps réel
# Dans le dashboard Render > Logs

# Tester l'endpoint de santé
curl https://votre-app.onrender.com/health

# Tester la connexion MongoDB
# Les erreurs apparaîtront dans les logs
```

## 📊 Monitoring

### Métriques importantes

- **Uptime** : Disponibilité de l'application
- **Response Time** : Temps de réponse
- **Error Rate** : Taux d'erreurs
- **Memory Usage** : Utilisation mémoire
- **CPU Usage** : Utilisation CPU

### Alertes

Configurez des alertes pour :
- Downtime > 5 minutes
- Error rate > 5%
- Response time > 10 secondes

## 🔄 Mises à jour

### Déploiement automatique

1. **Push sur la branche main**
2. **Render déploiera automatiquement**
3. **Vérifier les logs de déploiement**

### Déploiement manuel

1. **Aller dans le dashboard Render**
2. **Cliquer "Manual Deploy"**
3. **Choisir la branche/commit**

## 💰 Coûts

### Plan gratuit (Starter)

- **750 heures/mois** (gratuit)
- **512 MB RAM**
- **0.1 CPU**
- **Pas de domaine personnalisé**

### Plan payant (Standard)

- **$7/mois**
- **1 GB RAM**
- **0.5 CPU**
- **Domaine personnalisé**
- **Support prioritaire**

## 🔒 Sécurité

### Bonnes pratiques

1. **Changer le mot de passe admin** après le premier déploiement
2. **Utiliser des clés secrètes fortes**
3. **Limiter l'accès MongoDB** aux IPs Render
4. **Surveiller les logs** régulièrement
5. **Mettre à jour les dépendances** régulièrement

### Variables sensibles

- `SECRET_KEY` : Clé secrète Flask
- `MONGO_URI` : URI de connexion MongoDB
- `CLOUDINARY_API_SECRET` : Clé secrète Cloudinary
- `HUGGINGFACE_API_KEY` : Clé API Hugging Face
- `ADMIN_PASSWORD` : Mot de passe administrateur

## 📞 Support

### Ressources utiles

- [Documentation Render](https://render.com/docs)
- [Documentation MongoDB Atlas](https://docs.atlas.mongodb.com/)
- [Documentation Cloudinary](https://cloudinary.com/documentation)
- [Documentation Hugging Face](https://huggingface.co/docs)

### En cas de problème

1. **Vérifier les logs** dans Render
2. **Tester localement** d'abord
3. **Consulter la documentation** des services
4. **Créer une issue** sur GitHub

---

**🎉 Félicitations !** Votre application Medical Diagnosis AI est maintenant déployée sur Render et accessible publiquement. 