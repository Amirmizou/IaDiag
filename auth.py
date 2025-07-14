from functools import wraps
from flask import redirect, url_for, flash, request
from flask_login import current_user, login_required

def admin_required(f):
    """Décorateur pour les routes qui nécessitent des privilèges admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        if not current_user.is_admin():
            flash('Accès refusé. Privilèges administrateur requis.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def doctor_required(f):
    """Décorateur pour les routes qui nécessitent des privilèges doctor"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        if not (current_user.is_admin() or current_user.is_doctor()):
            flash('Accès refusé. Privilèges médecin requis.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def active_user_required(f):
    """Décorateur pour vérifier que l'utilisateur est actif"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        if not current_user.is_active:
            flash('Votre compte a été désactivé. Contactez l\'administrateur.', 'error')
            return redirect(url_for('logout'))
        return f(*args, **kwargs)
    return decorated_function 