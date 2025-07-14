from flask import Flask, request, jsonify, render_template, send_from_directory, redirect, url_for, flash
from flask_cors import CORS
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import os
from dotenv import load_dotenv
import requests
import json
from datetime import datetime
import uuid
from PIL import Image
import io
import base64
import numpy as np
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import tempfile
import cloudinary
import cloudinary.uploader
from huggingface_hub import InferenceClient
from database import DatabaseService
from auth import admin_required, doctor_required, active_user_required
from report_generator import MedicalReportGenerator

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'mizou450')
app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 16777216))

# Flask-Login configuration
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'
login_manager.login_message_category = 'info'

# Database service
db_service = DatabaseService()

# Report generator
report_generator = MedicalReportGenerator()

# Hugging Face API configuration
HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY')
HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/google/medgemma-2b"

# Cloudinary configuration
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)

# Hugging Face Inference Client
HF_TOKEN = os.getenv('HUGGINGFACE_API_KEY')
hf_client = InferenceClient(
    api_key=HF_TOKEN,
)

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Headers for Hugging Face API
headers = {
    "Authorization": f"Bearer {HUGGINGFACE_API_KEY}",
    "Content-Type": "application/json"
}

@login_manager.user_loader
def load_user(user_id):
    """Callback pour Flask-Login"""
    return db_service.get_user_by_id(user_id)

def analyze_medical_image(image_data):
    """Analyze medical image using Cloudinary + Hugging Face MedGemma API (InferenceClient)"""
    try:
        import base64
        # 1. Décoder l'image base64 et uploader sur Cloudinary
        image_bytes = base64.b64decode(image_data)
        upload_result = cloudinary.uploader.upload(
            image_bytes,
            resource_type="image"
        )
        image_url = upload_result['secure_url']

        # 2. Appeler MedGemma via InferenceClient
        completion = hf_client.chat.completions.create(
            model="google/medgemma-4b-it",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Analyse cette image médicale en détail. Identifie et décris :\n\n1. Les structures anatomiques visibles\n2. Les anomalies ou lésions détectées (si présentes)\n3. Les signes pathologiques observés\n4. Les diagnostics différentiels probables\n5. La gravité apparente (normale, légère, modérée, sévère)\n\nDonne une analyse structurée et professionnelle en français."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url
                            }
                        }
                    ]
                }
            ],
        )
        return {
            'success': True,
            'analysis': completion.choices[0].message.content,
            'confidence': 0.85  # Placeholder
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'analysis': None,
            'confidence': 0.0
        }

def generate_pdf_report(diagnosis_data, user_data=None):
    """Generate a professional PDF report for the diagnosis"""
    try:
        return report_generator.generate_report(diagnosis_data, user_data)
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return None

# Routes d'authentification
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Page de connexion"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = db_service.get_user_by_username(username)
        if user and user.check_password(password):
            if not user.is_active:
                flash('Votre compte a été désactivé.', 'error')
                return render_template('login.html')
            
            login_user(user)
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('dashboard'))
        else:
            flash('Nom d\'utilisateur ou mot de passe incorrect.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """Déconnexion"""
    logout_user()
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Page d'inscription (seulement pour les utilisateurs normaux)"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Les mots de passe ne correspondent pas.', 'error')
            return render_template('register.html')
        
        try:
            user = db_service.create_user(username, email, password, role='user')
            flash('Compte créé avec succès. Vous pouvez maintenant vous connecter.', 'success')
            return redirect(url_for('login'))
        except ValueError as e:
            flash(str(e), 'error')
    
    return render_template('register.html')

# Routes principales (protégées)
@app.route('/')
@login_required
@active_user_required
def dashboard():
    """Tableau de bord principal"""
    return render_template('dashboard.html')

@app.route('/diagnosis')
@login_required
@active_user_required
def diagnosis_page():
    """Page de diagnostic"""
    return render_template('diagnosis.html')

@app.route('/diagnose', methods=['POST'])
@login_required
@active_user_required
def diagnose():
    """Endpoint pour le diagnostic médical avec support des fichiers"""
    try:
        patient_id = request.form.get('patient_id', f'PAT{datetime.now().strftime("%Y%m%d%H%M%S")}')
        symptoms = request.form.get('symptoms', '')
        image_file = request.files.get('image')
        
        if not symptoms and not image_file:
            return jsonify({'success': False, 'error': 'Veuillez fournir soit des symptômes soit une image'})
        
        # Traitement de l'image si fournie
        image_path = None
        if image_file:
            try:
                # Upload vers Cloudinary
                upload_result = cloudinary.uploader.upload(
                    image_file,
                    resource_type="image",
                    folder="medical_images"
                )
                image_path = upload_result['secure_url']
                
                # Analyse de l'image
                try:
                    completion = hf_client.chat.completions.create(
                        model="google/medgemma-4b-it",
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "text",
                                        "text": "Analyse cette image médicale en détail. Identifie et décris :\n\n1. Les structures anatomiques visibles\n2. Les anomalies ou lésions détectées (si présentes)\n3. Les signes pathologiques observés\n4. Les diagnostics différentiels probables\n5. La gravité apparente (normale, légère, modérée, sévère)\n\nDonne une analyse structurée et professionnelle en français."
                                    },
                                    {
                                        "type": "image_url",
                                        "image_url": {
                                            "url": image_path
                                        }
                                    }
                                ]
                            }
                        ],
                    )
                    diagnosis_text = completion.choices[0].message.content
                    confidence = 0.85
                except Exception as e:
                    return jsonify({'success': False, 'error': f'Erreur lors de l\'analyse de l\'image: {str(e)}'})
            except Exception as e:
                return jsonify({'success': False, 'error': f'Erreur lors du traitement de l\'image: {str(e)}'})
        else:
            # Diagnostic basé sur les symptômes uniquement
            try:
                completion = hf_client.chat.completions.create(
                    model="google/medgemma-4b-it",
                    messages=[
                        {
                            "role": "user",
                            "content": f"Analyse ces symptômes médicaux et fournis un diagnostic détaillé :\n\n{symptoms}\n\nDonne une analyse structurée en français avec :\n1. Les structures anatomiques concernées\n2. Les anomalies ou lésions probables\n3. Les signes pathologiques\n4. Les diagnostics différentiels\n5. La gravité apparente"
                        }
                    ],
                )
                diagnosis_text = completion.choices[0].message.content
                confidence = 0.75  # Confiance plus faible pour diagnostic basé sur symptômes
            except Exception as e:
                return jsonify({'success': False, 'error': f'Erreur lors de l\'analyse des symptômes: {str(e)}'})
        
        # Créer le diagnostic en base
        diagnosis = db_service.create_diagnosis(
            patient_id=patient_id,
            symptoms=symptoms,
            diagnosis=diagnosis_text,
            confidence=confidence,
            user_id=current_user.get_id(),
            image_path=image_path
        )
        
        return jsonify({
            'success': True,
            'diagnosis_id': diagnosis._id,
            'patient_id': diagnosis.patient_id,
            'symptoms': diagnosis.symptoms,
            'diagnosis': diagnosis.diagnosis,
            'confidence': diagnosis.confidence,
            'image_path': diagnosis.image_path,
            'status': diagnosis.status,
            'created_at': diagnosis.created_at
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/get_diagnoses', methods=['GET'])
@login_required
@active_user_required
def get_diagnoses():
    """Get diagnoses (filtered by user role)"""
    try:
        if current_user.is_admin():
            # Admin can see all diagnoses
            diagnoses = db_service.get_all_diagnoses()
        else:
            # Regular users can only see their own diagnoses
            diagnoses = db_service.get_diagnoses_by_user(current_user.get_id())
        
        return jsonify({
            'success': True,
            'diagnoses': [d.to_dict() for d in diagnoses]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/diagnoses', methods=['GET'])
@login_required
@active_user_required
def api_get_diagnoses():
    """API endpoint for diagnoses (compatibility)"""
    return get_diagnoses()

@app.route('/get_diagnosis/<diagnosis_id>', methods=['GET'])
@login_required
@active_user_required
def get_diagnosis(diagnosis_id):
    """Get a specific diagnosis"""
    try:
        diagnosis = db_service.get_diagnosis_by_id(diagnosis_id)
        if not diagnosis:
            return jsonify({'success': False, 'error': 'Diagnosis not found'})
        
        # Check if user has access to this diagnosis
        if not current_user.is_admin() and diagnosis.user_id != current_user.get_id():
            return jsonify({'success': False, 'error': 'Access denied'})
        
        return jsonify({
            'success': True,
            'diagnosis': diagnosis.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/diagnoses/<diagnosis_id>', methods=['GET'])
@login_required
@active_user_required
def api_get_diagnosis(diagnosis_id):
    """API endpoint for specific diagnosis (compatibility)"""
    return get_diagnosis(diagnosis_id)

@app.route('/api/diagnoses/<diagnosis_id>/status', methods=['PUT'])
@login_required
@doctor_required
def update_diagnosis_status(diagnosis_id):
    """Update diagnosis status (doctors and admins only)"""
    try:
        data = request.get_json()
        status = data.get('status')
        comment = data.get('comment', '')  # Commentaire optionnel du médecin
        
        if not status:
            return jsonify({'error': 'Status is required'}), 400
        
        if status not in ['pending_review', 'confirmed', 'rejected']:
            return jsonify({'error': 'Invalid status'}), 400
        
        diagnosis = db_service.get_diagnosis_by_id(diagnosis_id)
        if not diagnosis:
            return jsonify({'error': 'Diagnosis not found'}), 404
        
        # Mettre à jour le statut et ajouter un commentaire si fourni
        update_data = {'status': status}
        if comment:
            update_data['doctor_comment'] = comment
            update_data['validated_by'] = current_user.username
            update_data['validated_at'] = datetime.utcnow()
        
        success = db_service.update_diagnosis(diagnosis_id, **update_data)
        if success:
            updated_diagnosis = db_service.get_diagnosis_by_id(diagnosis_id)
            return jsonify({
                'success': True,
                'diagnosis': updated_diagnosis.to_dict(),
                'message': f'Diagnostic {status.replace("_", " ")} avec succès'
            })
        else:
            return jsonify({'error': 'Failed to update status'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/diagnoses/pending', methods=['GET'])
@login_required
@doctor_required
def get_pending_diagnoses():
    """Get all pending diagnoses for review (doctors and admins only)"""
    try:
        # Récupérer tous les diagnostics en attente
        diagnoses = db_service.get_diagnoses_by_status('pending_review')
        
        return jsonify({
            'success': True,
            'diagnoses': [d.to_dict() for d in diagnoses],
            'count': len(diagnoses)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/doctor/review')
@login_required
@doctor_required
def doctor_review():
    """Page de validation des diagnostics pour les médecins"""
    return render_template('doctor/review.html')

@app.route('/download_report/<diagnosis_id>', methods=['GET'])
@login_required
@active_user_required
def download_report(diagnosis_id):
    """Download PDF report for a diagnosis"""
    try:
        diagnosis = db_service.get_diagnosis_by_id(diagnosis_id)
        if not diagnosis:
            return jsonify({'success': False, 'error': 'Diagnosis not found'})
        
        # Check if user has access to this diagnosis
        if not current_user.is_admin() and diagnosis.user_id != current_user.get_id():
            return jsonify({'success': False, 'error': 'Access denied'})
        
        # Récupérer les informations de l'utilisateur
        user_data = db_service.get_user_by_id(diagnosis.user_id)
        user_dict = user_data.to_dict() if user_data else None
        
        pdf_path = generate_pdf_report(diagnosis.to_dict(), user_dict)
        if pdf_path:
            return send_from_directory(
                os.path.dirname(pdf_path),
                os.path.basename(pdf_path),
                as_attachment=True,
                download_name=f"diagnosis_report_{diagnosis_id}.pdf"
            )
        else:
            return jsonify({'error': 'Failed to generate PDF report'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/diagnoses/<diagnosis_id>/report', methods=['GET'])
@login_required
@active_user_required
def api_download_report(diagnosis_id):
    """API endpoint for downloading report (compatibility)"""
    return download_report(diagnosis_id)

@app.route('/api/reports/summary', methods=['GET'])
@login_required
@active_user_required
def generate_summary_report():
    """Generate summary PDF report for all user diagnoses"""
    try:
        # Récupérer tous les diagnostics de l'utilisateur
        if current_user.is_admin():
            diagnoses = db_service.get_all_diagnoses()
        else:
            diagnoses = db_service.get_diagnoses_by_user(current_user.get_id())
        
        if not diagnoses:
            return jsonify({'error': 'No diagnoses found'}), 404
        
        # Convertir en dictionnaires
        diagnoses_dicts = [d.to_dict() for d in diagnoses]
        
        # Générer le rapport de synthèse
        pdf_path = report_generator.generate_summary_report(diagnoses_dicts, current_user.to_dict())
        
        if pdf_path:
            return send_from_directory(
                os.path.dirname(pdf_path),
                os.path.basename(pdf_path),
                as_attachment=True,
                download_name=f"medical_summary_report_{current_user.username}_{datetime.now().strftime('%Y%m%d')}.pdf"
            )
        else:
            return jsonify({'error': 'Failed to generate summary PDF report'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Routes d'administration (admin only)
@app.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    """Tableau de bord administrateur"""
    stats = db_service.get_diagnoses_stats()
    users = db_service.get_all_users()
    return render_template('admin/dashboard.html', stats=stats, users=users)

@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    """Gestion des utilisateurs"""
    users = db_service.get_all_users()
    return render_template('admin/users.html', users=users)

@app.route('/admin/users/create', methods=['POST'])
@login_required
@admin_required
def create_user():
    """Créer un nouvel utilisateur"""
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role', 'user')
        
        user = db_service.create_user(username, email, password, role)
        return jsonify({
            'success': True,
            'user': user.to_dict()
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/users/<user_id>', methods=['PUT'])
@login_required
@admin_required
def update_user(user_id):
    """Mettre à jour un utilisateur"""
    try:
        data = request.get_json()
        success = db_service.update_user(user_id, **data)
        
        if success:
            user = db_service.get_user_by_id(user_id)
            return jsonify({
                'success': True,
                'user': user.to_dict()
            })
        else:
            return jsonify({'error': 'Failed to update user'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/users/<user_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_user(user_id):
    """Supprimer un utilisateur"""
    try:
        # Prevent admin from deleting themselves
        if user_id == current_user.get_id():
            return jsonify({'error': 'Cannot delete your own account'}), 400
        
        success = db_service.delete_user(user_id)
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Failed to delete user'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/uploads/<filename>')
@login_required
@active_user_required
def uploaded_file(filename):
    """Serve uploaded files"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files"""
    return send_from_directory('static', filename)

# Health check endpoint for Render
@app.route('/health')
def health_check():
    """Health check endpoint for Render"""
    return jsonify({'status': 'healthy', 'message': 'Medical Diagnosis AI is running'})

if __name__ == '__main__':
    # Get port from environment variable (Render sets PORT)
    port = int(os.environ.get('PORT', 5000))
    
    # Run in production mode on Render
    if os.environ.get('FLASK_ENV') == 'production':
        app.run(host='0.0.0.0', port=port)
    else:
        app.run(debug=True, host='0.0.0.0', port=port) 