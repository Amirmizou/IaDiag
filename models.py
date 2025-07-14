from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid

class User(UserMixin):
    def __init__(self, username, email, password_hash, role='user', is_active=True, created_at=None, _id=None):
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.role = role  # 'admin', 'doctor', 'user'
        self._is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self._id = _id or str(uuid.uuid4())
    
    @property
    def is_active(self):
        return self._is_active
    
    @is_active.setter
    def is_active(self, value):
        self._is_active = value
    
    def get_id(self):
        return self._id
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_doctor(self):
        return self.role == 'doctor'
    
    def to_dict(self):
        return {
            '_id': self._id,
            'username': self.username,
            'email': self.email,
            'password_hash': self.password_hash,
            'role': self.role,
            'is_active': self._is_active,
            'created_at': self.created_at
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            username=data['username'],
            email=data['email'],
            password_hash=data['password_hash'],
            role=data.get('role', 'user'),
            is_active=data.get('is_active', True),
            created_at=data.get('created_at'),
            _id=data['_id']
        )

class Diagnosis:
    def __init__(self, patient_id, symptoms, diagnosis, confidence, user_id, image_path=None, status='pending_review', created_at=None, _id=None, doctor_comment=None, validated_by=None, validated_at=None):
        self.patient_id = patient_id
        self.symptoms = symptoms
        self.diagnosis = diagnosis
        self.confidence = confidence
        self.user_id = user_id  # ID de l'utilisateur qui a créé le diagnostic
        self.image_path = image_path
        self.status = status  # 'pending_review', 'confirmed', 'rejected'
        self.created_at = created_at or datetime.utcnow()
        self._id = _id or str(uuid.uuid4())
        self.doctor_comment = doctor_comment  # Commentaire du médecin
        self.validated_by = validated_by  # Nom du médecin qui a validé
        self.validated_at = validated_at  # Date de validation
    
    def to_dict(self):
        return {
            '_id': self._id,
            'patient_id': self.patient_id,
            'symptoms': self.symptoms,
            'diagnosis': self.diagnosis,
            'confidence': self.confidence,
            'user_id': self.user_id,
            'image_path': self.image_path,
            'status': self.status,
            'created_at': self.created_at,
            'doctor_comment': self.doctor_comment,
            'validated_by': self.validated_by,
            'validated_at': self.validated_at
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            patient_id=data['patient_id'],
            symptoms=data['symptoms'],
            diagnosis=data['diagnosis'],
            confidence=data['confidence'],
            user_id=data['user_id'],
            image_path=data.get('image_path'),
            status=data.get('status', 'pending_review'),
            created_at=data.get('created_at'),
            _id=data['_id'],
            doctor_comment=data.get('doctor_comment'),
            validated_by=data.get('validated_by'),
            validated_at=data.get('validated_at')
        ) 