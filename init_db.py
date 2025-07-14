#!/usr/bin/env python3
"""
Script d'initialisation de la base de données MongoDB
Créé automatiquement le compte admin et configure les index
"""

import os
import sys
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

def init_database():
    """Initialiser la base de données MongoDB"""
    try:
        from database import DatabaseService
        from models import User
        
        print("🔧 Initialisation de la base de données MongoDB...")
        
        # Créer le service de base de données
        db_service = DatabaseService()
        
        print("✅ Base de données initialisée avec succès!")
        print("📊 Statistiques:")
        
        # Compter les utilisateurs
        users = db_service.get_all_users()
        print(f"   - Utilisateurs: {len(users)}")
        
        # Compter les diagnostics
        diagnoses = db_service.get_all_diagnoses()
        print(f"   - Diagnostics: {len(diagnoses)}")
        
        # Afficher les utilisateurs existants
        if users:
            print("\n👥 Utilisateurs existants:")
            for user in users:
                status = "✅ Actif" if user.is_active else "❌ Inactif"
                print(f"   - {user.username} ({user.email}) - {user.role} - {status}")
        
        print("\n🎉 Initialisation terminée!")
        print("\n📝 Informations de connexion:")
        print(f"   - URI MongoDB: {os.getenv('MONGO_URI', 'mongodb://localhost:27017/')}")
        print(f"   - Base de données: {os.getenv('MONGO_DB_NAME', 'medical_diagnosis')}")
        print(f"   - Admin par défaut: {os.getenv('ADMIN_USERNAME', 'admin')}")
        print(f"   - Mot de passe admin: {os.getenv('ADMIN_PASSWORD', 'admin123')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation: {e}")
        return False

def check_mongodb_connection():
    """Vérifier la connexion MongoDB"""
    try:
        from pymongo import MongoClient
        
        mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        
        # Tester la connexion
        client.admin.command('ping')
        print("✅ Connexion MongoDB réussie!")
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Erreur de connexion MongoDB: {e}")
        print("\n🔧 Solutions possibles:")
        print("   1. Vérifiez que MongoDB est installé et en cours d'exécution")
        print("   2. Vérifiez l'URI MongoDB dans votre fichier .env")
        print("   3. Si vous utilisez MongoDB Atlas, vérifiez votre clé de connexion")
        return False

def main():
    """Fonction principale"""
    print("🚀 Initialisation de Medical Diagnosis AI")
    print("=" * 50)
    
    # Vérifier la connexion MongoDB
    if not check_mongodb_connection():
        sys.exit(1)
    
    # Initialiser la base de données
    if not init_database():
        sys.exit(1)
    
    print("\n🎯 Prochaines étapes:")
    print("   1. Lancez l'application: python app.py")
    print("   2. Connectez-vous avec le compte admin")
    print("   3. Créez des utilisateurs supplémentaires via l'interface d'administration")
    print("   4. Configurez vos clés API dans le fichier .env")

if __name__ == "__main__":
    main() 