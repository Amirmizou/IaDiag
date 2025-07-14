#!/bin/bash

# Script de déploiement pour Medical Diagnosis AI
# Usage: ./deploy.sh [production|staging]

set -e

ENVIRONMENT=${1:-production}
echo "🚀 Déploiement en mode: $ENVIRONMENT"

# Vérifier que git est configuré
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Erreur: Ce n'est pas un repository git"
    exit 1
fi

# Vérifier que tous les fichiers sont commités
if ! git diff-index --quiet HEAD --; then
    echo "❌ Erreur: Il y a des modifications non commitées"
    echo "Veuillez commiter vos changements avant le déploiement"
    exit 1
fi

# Vérifier que la branche est main/master
CURRENT_BRANCH=$(git branch --show-current)
if [[ "$CURRENT_BRANCH" != "main" && "$CURRENT_BRANCH" != "master" ]]; then
    echo "⚠️  Attention: Vous n'êtes pas sur la branche main/master"
    echo "Branche actuelle: $CURRENT_BRANCH"
    read -p "Continuer quand même ? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Vérifier les fichiers de configuration
echo "📋 Vérification des fichiers de configuration..."

REQUIRED_FILES=(
    "requirements.txt"
    "app.py"
    "database.py"
    "models.py"
    "auth.py"
    "report_generator.py"
    "gunicorn.conf.py"
    "Procfile"
    "runtime.txt"
    "render.yaml"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [[ ! -f "$file" ]]; then
        echo "❌ Erreur: Fichier manquant: $file"
        exit 1
    fi
done

echo "✅ Tous les fichiers requis sont présents"

# Vérifier les variables d'environnement
echo "🔧 Vérification des variables d'environnement..."

if [[ -f ".env" ]]; then
    echo "✅ Fichier .env trouvé"
else
    echo "⚠️  Fichier .env non trouvé"
    echo "Assurez-vous de configurer les variables d'environnement sur Render"
fi

# Tests de base
echo "🧪 Exécution des tests de base..."

# Test de syntaxe Python
echo "  - Test de syntaxe Python..."
python -m py_compile app.py
python -m py_compile database.py
python -m py_compile models.py
python -m py_compile auth.py
python -m py_compile report_generator.py

# Test d'import des modules
echo "  - Test d'import des modules..."
python -c "
import app
import database
import models
import auth
import report_generator
print('✅ Tous les modules s\'importent correctement')
"

echo "✅ Tests de base réussis"

# Préparation du déploiement
echo "📦 Préparation du déploiement..."

# Créer un tag de version
VERSION=$(date +"%Y%m%d-%H%M%S")
git tag "v-$VERSION"
echo "🏷️  Tag créé: v-$VERSION"

# Push vers le repository distant
echo "📤 Push vers le repository distant..."
git push origin $CURRENT_BRANCH
git push origin "v-$VERSION"

echo "✅ Déploiement préparé avec succès!"
echo ""
echo "📋 Prochaines étapes:"
echo "1. Allez sur https://dashboard.render.com"
echo "2. Créez un nouveau service web"
echo "3. Liez votre repository GitHub"
echo "4. Configurez les variables d'environnement:"
echo "   - SECRET_KEY"
echo "   - MONGO_URI"
echo "   - CLOUDINARY_CLOUD_NAME"
echo "   - CLOUDINARY_API_KEY"
echo "   - CLOUDINARY_API_SECRET"
echo "   - HUGGINGFACE_API_KEY"
echo "   - ADMIN_PASSWORD"
echo "5. Déployez!"
echo ""
echo "🔗 Votre application sera disponible sur: https://votre-app.onrender.com"
echo ""
echo "📊 Pour vérifier le déploiement:"
echo "curl https://votre-app.onrender.com/health" 