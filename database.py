from pymongo import MongoClient
from models import User, Diagnosis
from datetime import datetime
import os

class DatabaseService:
    def __init__(self):
        # Configuration MongoDB
        mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
        db_name = os.getenv('MONGO_DB_NAME', 'medical_diagnosis')
        
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]
        self.users_collection = self.db.users
        self.diagnoses_collection = self.db.diagnoses
        
        # Créer les index pour les performances
        self.users_collection.create_index("username", unique=True)
        self.users_collection.create_index("email", unique=True)
        self.diagnoses_collection.create_index("user_id")
        self.diagnoses_collection.create_index("created_at")
        
        # Initialiser l'admin si nécessaire
        self._init_admin()
    
    def _init_admin(self):
        """Initialiser le compte admin par défaut"""
        admin_username = os.getenv('ADMIN_USERNAME', 'admin')
        admin_email = os.getenv('ADMIN_EMAIL', 'admin@medical.com')
        admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
        
        # Vérifier si l'admin existe déjà
        existing_admin = self.users_collection.find_one({"username": admin_username})
        if not existing_admin:
            admin_user = User(
                username=admin_username,
                email=admin_email,
                password_hash="",  # Sera défini par set_password
                role='admin'
            )
            admin_user.set_password(admin_password)
            self.users_collection.insert_one(admin_user.to_dict())
            print(f"Admin user created: {admin_username}")
    
    # Méthodes pour les utilisateurs
    def get_user_by_id(self, user_id):
        """Récupérer un utilisateur par son ID"""
        user_data = self.users_collection.find_one({"_id": user_id})
        if user_data:
            return User.from_dict(user_data)
        return None
    
    def get_user_by_username(self, username):
        """Récupérer un utilisateur par son nom d'utilisateur"""
        user_data = self.users_collection.find_one({"username": username})
        if user_data:
            return User.from_dict(user_data)
        return None
    
    def get_user_by_email(self, email):
        """Récupérer un utilisateur par son email"""
        user_data = self.users_collection.find_one({"email": email})
        if user_data:
            return User.from_dict(user_data)
        return None
    
    def create_user(self, username, email, password, role='user'):
        """Créer un nouvel utilisateur"""
        # Vérifier si l'utilisateur existe déjà
        if self.get_user_by_username(username):
            raise ValueError("Username already exists")
        if self.get_user_by_email(email):
            raise ValueError("Email already exists")
        
        user = User(username=username, email=email, password_hash="", role=role)
        user.set_password(password)
        
        result = self.users_collection.insert_one(user.to_dict())
        user._id = result.inserted_id
        return user
    
    def update_user(self, user_id, **kwargs):
        """Mettre à jour un utilisateur"""
        update_data = {}
        for key, value in kwargs.items():
            if key in ['username', 'email', 'role', 'is_active']:
                update_data[key] = value
        
        if update_data:
            self.users_collection.update_one(
                {"_id": user_id},
                {"$set": update_data}
            )
            return True
        return False
    
    def delete_user(self, user_id):
        """Supprimer un utilisateur"""
        result = self.users_collection.delete_one({"_id": user_id})
        return result.deleted_count > 0
    
    def get_all_users(self):
        """Récupérer tous les utilisateurs"""
        users_data = self.users_collection.find()
        return [User.from_dict(user_data) for user_data in users_data]
    
    # Méthodes pour les diagnostics
    def create_diagnosis(self, patient_id, symptoms, diagnosis, confidence, user_id, image_path=None):
        """Créer un nouveau diagnostic"""
        diagnosis_obj = Diagnosis(
            patient_id=patient_id,
            symptoms=symptoms,
            diagnosis=diagnosis,
            confidence=confidence,
            user_id=user_id,
            image_path=image_path
        )
        
        result = self.diagnoses_collection.insert_one(diagnosis_obj.to_dict())
        diagnosis_obj._id = result.inserted_id
        return diagnosis_obj
    
    def get_diagnosis_by_id(self, diagnosis_id):
        """Récupérer un diagnostic par son ID"""
        diagnosis_data = self.diagnoses_collection.find_one({"_id": diagnosis_id})
        if diagnosis_data:
            return Diagnosis.from_dict(diagnosis_data)
        return None
    
    def get_diagnoses_by_user(self, user_id):
        """Récupérer tous les diagnostics d'un utilisateur"""
        diagnoses_data = self.diagnoses_collection.find({"user_id": user_id})
        return [Diagnosis.from_dict(diagnosis_data) for diagnosis_data in diagnoses_data]
    
    def get_all_diagnoses(self):
        """Récupérer tous les diagnostics"""
        diagnoses_data = self.diagnoses_collection.find()
        return [Diagnosis.from_dict(diagnosis_data) for diagnosis_data in diagnoses_data]
    
    def update_diagnosis_status(self, diagnosis_id, status):
        """Mettre à jour le statut d'un diagnostic"""
        result = self.diagnoses_collection.update_one(
            {"_id": diagnosis_id},
            {"$set": {"status": status}}
        )
        return result.modified_count > 0
    
    def update_diagnosis(self, diagnosis_id, **kwargs):
        """Mettre à jour un diagnostic avec plusieurs champs"""
        update_data = {}
        for key, value in kwargs.items():
            if key in ['status', 'doctor_comment', 'validated_by', 'validated_at']:
                update_data[key] = value
        
        if update_data:
            result = self.diagnoses_collection.update_one(
                {"_id": diagnosis_id},
                {"$set": update_data}
            )
            return result.modified_count > 0
        return False
    
    def get_diagnoses_by_status(self, status):
        """Récupérer tous les diagnostics par statut"""
        diagnoses_data = self.diagnoses_collection.find({"status": status})
        return [Diagnosis.from_dict(diagnosis_data) for diagnosis_data in diagnoses_data]
    
    def delete_diagnosis(self, diagnosis_id):
        """Supprimer un diagnostic"""
        result = self.diagnoses_collection.delete_one({"_id": diagnosis_id})
        return result.deleted_count > 0
    
    def get_diagnoses_stats(self):
        """Obtenir les statistiques des diagnostics"""
        total = self.diagnoses_collection.count_documents({})
        pending = self.diagnoses_collection.count_documents({"status": "pending_review"})
        confirmed = self.diagnoses_collection.count_documents({"status": "confirmed"})
        rejected = self.diagnoses_collection.count_documents({"status": "rejected"})
        
        return {
            "total": total,
            "pending": pending,
            "confirmed": confirmed,
            "rejected": rejected
        } 