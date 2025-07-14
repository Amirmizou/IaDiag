#!/usr/bin/env python3
"""
Générateur de rapports PDF professionnels pour Medical Diagnosis AI
"""

from reportlab.lib.pagesizes import A4, letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import os
import tempfile
from PIL import Image as PILImage
import io
import re
import requests

class MedicalReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Configurer les styles personnalisés"""
        # Style pour le titre principal
        self.styles.add(ParagraphStyle(
            name='MainTitle',
            parent=self.styles['Heading1'],
            fontSize=28,
            spaceAfter=30,
            spaceBefore=20,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#1e3a8a'),
            fontName='Helvetica-Bold',
            borderWidth=2,
            borderColor=colors.HexColor('#1e3a8a'),
            borderPadding=15,
            backColor=colors.HexColor('#eff6ff')
        ))
        
        # Style pour les sous-titres de section
        self.styles.add(ParagraphStyle(
            name='SectionTitle',
            parent=self.styles['Heading2'],
            fontSize=18,
            spaceAfter=15,
            spaceBefore=25,
            textColor=colors.HexColor('#1e40af'),
            fontName='Helvetica-Bold',
            borderWidth=1,
            borderColor=colors.HexColor('#3b82f6'),
            borderPadding=10,
            backColor=colors.HexColor('#f8fafc'),
            alignment=TA_LEFT
        ))
        
        # Style pour les sous-sections
        self.styles.add(ParagraphStyle(
            name='SubSectionTitle',
            parent=self.styles['Heading3'],
            fontSize=14,
            spaceAfter=10,
            spaceBefore=15,
            textColor=colors.HexColor('#374151'),
            fontName='Helvetica-Bold',
            alignment=TA_LEFT
        ))
        
        # Style pour les informations importantes
        self.styles.add(ParagraphStyle(
            name='ImportantInfo',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=8,
            textColor=colors.HexColor('#1f2937'),
            fontName='Helvetica-Bold',
            backColor=colors.HexColor('#f3f4f6'),
            borderWidth=1,
            borderColor=colors.HexColor('#d1d5db'),
            borderPadding=8
        ))
        
        # Style pour le texte normal
        self.styles.add(ParagraphStyle(
            name='NormalText',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            textColor=colors.HexColor('#374151'),
            fontName='Helvetica',
            alignment=TA_JUSTIFY,
            leftIndent=10
        ))
        
        # Style pour les listes
        self.styles.add(ParagraphStyle(
            name='ListText',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=4,
            textColor=colors.HexColor('#374151'),
            fontName='Helvetica',
            alignment=TA_LEFT,
            leftIndent=20
        ))
        
        # Style pour les alertes
        self.styles.add(ParagraphStyle(
            name='Alert',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=8,
            textColor=colors.HexColor('#dc2626'),
            fontName='Helvetica-Bold',
            backColor=colors.HexColor('#fef2f2'),
            borderWidth=2,
            borderColor=colors.HexColor('#fecaca'),
            borderPadding=10,
            alignment=TA_LEFT
        ))
        
        # Style pour les succès
        self.styles.add(ParagraphStyle(
            name='Success',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=8,
            textColor=colors.HexColor('#059669'),
            fontName='Helvetica-Bold',
            backColor=colors.HexColor('#f0fdf4'),
            borderWidth=2,
            borderColor=colors.HexColor('#bbf7d0'),
            borderPadding=10,
            alignment=TA_LEFT
        ))
        
        # Style pour les informations techniques
        self.styles.add(ParagraphStyle(
            name='TechInfo',
            parent=self.styles['Normal'],
            fontSize=9,
            spaceAfter=4,
            textColor=colors.HexColor('#6b7280'),
            fontName='Helvetica',
            alignment=TA_LEFT
        ))
    
    def _create_header(self, canvas, doc):
        """Créer l'en-tête du rapport"""
        canvas.saveState()
        
        # Fond de l'en-tête
        canvas.setFillColor(colors.HexColor('#eff6ff'))
        canvas.rect(0, doc.height + doc.topMargin - 80, doc.width + doc.leftMargin + doc.rightMargin, 80, fill=1)
        
        # Logo (si disponible)
        logo_path = "static/logo.png"
        if os.path.exists(logo_path):
            try:
                canvas.drawImage(logo_path, 50, doc.height + doc.topMargin - 70, width=60, height=40)
            except:
                pass
        
        # Titre de l'application
        canvas.setFont('Helvetica-Bold', 20)
        canvas.setFillColor(colors.HexColor('#1e3a8a'))
        canvas.drawString(130, doc.height + doc.topMargin - 35, "Medical Diagnosis AI")
        
        # Sous-titre
        canvas.setFont('Helvetica', 12)
        canvas.setFillColor(colors.HexColor('#6b7280'))
        canvas.drawString(130, doc.height + doc.topMargin - 50, "Système de diagnostic médical par intelligence artificielle")
        
        # Date de génération
        canvas.setFont('Helvetica', 10)
        canvas.setFillColor(colors.HexColor('#9ca3af'))
        canvas.drawRightString(doc.width + doc.leftMargin + doc.rightMargin - 50, 
                              doc.height + doc.topMargin - 25, 
                              f"Généré le: {datetime.now().strftime('%d/%m/%Y à %H:%M')}")
        
        # Ligne de séparation
        canvas.setStrokeColor(colors.HexColor('#3b82f6'))
        canvas.setLineWidth(2)
        canvas.line(50, doc.height + doc.topMargin - 85, 
                   doc.width + doc.leftMargin + doc.rightMargin - 50, 
                   doc.height + doc.topMargin - 85)
        
        # Pied de page
        self._create_footer(canvas, doc)
        
        canvas.restoreState()
    
    def _create_footer(self, canvas, doc):
        """Créer le pied de page"""
        canvas.saveState()
        
        # Ligne de séparation
        canvas.setStrokeColor(colors.HexColor('#e5e7eb'))
        canvas.setLineWidth(1)
        canvas.line(50, 60, doc.width + doc.leftMargin + doc.rightMargin - 50, 60)
        
        # Informations de pied de page
        canvas.setFont('Helvetica', 9)
        canvas.setFillColor(colors.HexColor('#9ca3af'))
        
        # Page number
        canvas.drawCentredString(doc.width/2 + doc.leftMargin, 40, 
                                f"Page {doc.page}")
        
        # Disclaimer
        canvas.drawCentredString(doc.width/2 + doc.leftMargin, 25, 
                                "Ce rapport est généré automatiquement et nécessite une validation médicale professionnelle")
        
        # Informations de contact
        canvas.drawCentredString(doc.width/2 + doc.leftMargin, 10, 
                                "Medical Diagnosis AI - Contact: support@medical-ai.com")
        
        canvas.restoreState()
    
    def _download_and_resize_image(self, image_url, max_width=400, max_height=300):
        """Télécharger et redimensionner une image depuis une URL ou un chemin local"""
        try:
            # Vérifier si c'est une URL ou un chemin local
            if image_url.startswith(('http://', 'https://')):
                # URL externe - télécharger
                response = requests.get(image_url, timeout=10)
                if response.status_code == 200:
                    img = PILImage.open(io.BytesIO(response.content))
                else:
                    return None
            else:
                # Chemin local - ouvrir directement
                if os.path.exists(image_url):
                    img = PILImage.open(image_url)
                else:
                    # Essayer avec le dossier uploads
                    upload_path = os.path.join('uploads', os.path.basename(image_url))
                    if os.path.exists(upload_path):
                        img = PILImage.open(upload_path)
                    else:
                        print(f"Image non trouvée: {image_url}")
                        return None
            
            # Convertir en RGB si nécessaire
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Redimensionner l'image
            img.thumbnail((max_width, max_height), PILImage.Resampling.LANCZOS)
            
            # Sauvegarder temporairement
            temp_img_path = tempfile.mktemp(suffix='.jpg')
            img.save(temp_img_path, 'JPEG', quality=85)
            
            return temp_img_path
        except Exception as e:
            print(f"Erreur lors du traitement de l'image: {e}")
            return None
    
    def _format_diagnosis_text(self, diagnosis_text):
        """Formater le texte de diagnostic pour une meilleure lisibilité"""
        if not diagnosis_text:
            return [{'title': 'Analyse médicale', 'content': ['Aucun diagnostic disponible']}]
        
        # Diviser le texte en sections
        sections = re.split(r'\d+\.', diagnosis_text)
        sections = [section.strip() for section in sections if section.strip()]
        
        if len(sections) > 1:
            # Format structuré avec numérotation
            section_titles = [
                'Structures anatomiques visibles',
                'Anomalies ou lésions détectées',
                'Signes pathologiques observés',
                'Diagnostics différentiels probables',
                'Gravité apparente'
            ]
            
            formatted_sections = []
            for i, section in enumerate(sections):
                if section.strip():
                    title = section_titles[i] if i < len(section_titles) else f"Section {i + 1}"
                    content = self._format_section_content(section.strip())
                    
                    formatted_sections.append({
                        'title': title,
                        'content': content
                    })
            
            return formatted_sections
        else:
            # Format simple
            return [{
                'title': 'Analyse médicale',
                'content': self._format_section_content(diagnosis_text)
            }]
    
    def _format_section_content(self, content):
        """Formater le contenu d'une section"""
        lines = content.split('\n')
        formatted_lines = []
        
        for line in lines:
            line = line.strip()
            if line:
                if line.startswith('-') or line.startswith('•') or line.startswith('*'):
                    formatted_lines.append(line[1:].strip())
                else:
                    formatted_lines.append(line)
        
        return formatted_lines
    
    def _get_status_info(self, status, confidence):
        """Obtenir les informations de statut formatées"""
        status_info = {
            'pending_review': {
                'text': 'En attente de validation',
                'color': colors.HexColor('#f59e0b'),
                'style': 'Alert'
            },
            'confirmed': {
                'text': 'Validé par un professionnel',
                'color': colors.HexColor('#059669'),
                'style': 'Success'
            },
            'rejected': {
                'text': 'Rejeté',
                'color': colors.HexColor('#dc2626'),
                'style': 'Alert'
            }
        }
        
        return status_info.get(status, status_info['pending_review'])
    
    def _get_confidence_level(self, confidence):
        """Obtenir le niveau de confiance formaté"""
        confidence_percent = confidence * 100
        
        if confidence_percent >= 90:
            return "Très élevée", colors.HexColor('#059669')
        elif confidence_percent >= 80:
            return "Élevée", colors.HexColor('#059669')
        elif confidence_percent >= 70:
            return "Modérée", colors.HexColor('#f59e0b')
        elif confidence_percent >= 60:
            return "Faible", colors.HexColor('#f59e0b')
        else:
            return "Très faible", colors.HexColor('#dc2626')
    
    def generate_report(self, diagnosis_data, user_data=None):
        """Générer un rapport PDF complet et professionnel"""
        try:
            # Créer un fichier temporaire pour le PDF
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                doc = SimpleDocTemplate(
                    tmp_file.name,
                    pagesize=A4,
                    rightMargin=2*cm,
                    leftMargin=2*cm,
                    topMargin=4*cm,  # Plus d'espace pour l'en-tête
                    bottomMargin=3*cm  # Plus d'espace pour le pied de page
                )
                
                # Liste des éléments du rapport
                story = []
                
                # Titre principal
                story.append(Paragraph("RAPPORT DE DIAGNOSTIC MÉDICAL", self.styles['MainTitle']))
                story.append(Spacer(1, 30))
                
                # Section 1: Informations du patient
                story.append(Paragraph("1. INFORMATIONS PATIENT", self.styles['SectionTitle']))
                
                patient_info_data = [
                    ['ID Patient:', diagnosis_data['patient_id']],
                    ['Date de diagnostic:', diagnosis_data['created_at'].strftime('%d/%m/%Y à %H:%M') if hasattr(diagnosis_data['created_at'], 'strftime') else str(diagnosis_data['created_at'])],
                    ['Statut:', diagnosis_data['status'].replace('_', ' ').title()],
                    ['Confiance IA:', f"{diagnosis_data['confidence']:.1%}"]
                ]
                
                if user_data:
                    patient_info_data.append(['Médecin:', user_data['username']])
                
                patient_table = Table(patient_info_data, colWidths=[3.5*cm, 8.5*cm])
                patient_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8fafc')),
                    ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#374151')),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 11),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                    ('TOPPADDING', (0, 0), (-1, -1), 8),
                    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb'))
                ]))
                
                story.append(patient_table)
                story.append(Spacer(1, 25))
                
                # Section 2: Image médicale (si disponible)
                if diagnosis_data.get('image_path'):
                    story.append(Paragraph("2. IMAGE MÉDICALE", self.styles['SectionTitle']))
                    
                    # Télécharger et redimensionner l'image
                    temp_img_path = self._download_and_resize_image(diagnosis_data['image_path'])
                    
                    if temp_img_path and os.path.exists(temp_img_path):
                        try:
                            # Ajouter l'image au rapport
                            img = Image(temp_img_path, width=12*cm, height=9*cm)
                            img.hAlign = 'CENTER'
                            story.append(img)
                            story.append(Spacer(1, 15))
                            
                            # Légende de l'image
                            story.append(Paragraph(
                                f"<i>Image médicale analysée - Source: {diagnosis_data['image_path']}</i>", 
                                self.styles['TechInfo']
                            ))
                            
                            # Nettoyer le fichier temporaire
                            os.unlink(temp_img_path)
                        except Exception as e:
                            print(f"Erreur lors de l'ajout de l'image: {e}")
                            story.append(Paragraph("Image non disponible", self.styles['Alert']))
                    
                    story.append(Spacer(1, 20))
                
                # Section 3: Symptômes
                if diagnosis_data.get('symptoms'):
                    story.append(Paragraph("3. SYMPTÔMES DÉCRITS", self.styles['SectionTitle']))
                    story.append(Paragraph(diagnosis_data['symptoms'], self.styles['NormalText']))
                    story.append(Spacer(1, 25))
                
                # Section 4: Diagnostic IA
                story.append(Paragraph("4. DIAGNOSTIC PAR INTELLIGENCE ARTIFICIELLE", self.styles['SectionTitle']))
                
                # Niveau de confiance
                confidence_level, confidence_color = self._get_confidence_level(diagnosis_data['confidence'])
                confidence_text = f"Niveau de confiance: {confidence_level} ({diagnosis_data['confidence']:.1%})"
                story.append(Paragraph(confidence_text, self.styles['ImportantInfo']))
                story.append(Spacer(1, 15))
                
                # Contenu du diagnostic
                formatted_diagnosis = self._format_diagnosis_text(diagnosis_data['diagnosis'])
                
                for section in formatted_diagnosis:
                    story.append(Paragraph(section['title'], self.styles['SubSectionTitle']))
                    
                    if isinstance(section['content'], list):
                        for item in section['content']:
                            story.append(Paragraph(f"• {item}", self.styles['ListText']))
                    else:
                        story.append(Paragraph(section['content'], self.styles['NormalText']))
                    
                    story.append(Spacer(1, 10))
                
                story.append(Spacer(1, 25))
                
                # Section 5: Statut de validation
                story.append(Paragraph("5. STATUT DE VALIDATION", self.styles['SectionTitle']))
                status_info = self._get_status_info(diagnosis_data['status'], diagnosis_data['confidence'])
                status_text = f"Statut: {status_info['text']}"
                story.append(Paragraph(status_text, self.styles[status_info['style']]))
                
                # Commentaires du médecin (si disponibles)
                if diagnosis_data.get('doctor_comment'):
                    story.append(Spacer(1, 10))
                    story.append(Paragraph("Commentaires du médecin:", self.styles['SubSectionTitle']))
                    story.append(Paragraph(diagnosis_data['doctor_comment'], self.styles['NormalText']))
                
                story.append(Spacer(1, 30))
                
                # Section 6: Avertissements et recommandations
                story.append(Paragraph("6. AVERTISSEMENTS ET RECOMMANDATIONS", self.styles['SectionTitle']))
                
                warnings = [
                    "⚠️ Ce diagnostic est généré par une intelligence artificielle et nécessite une validation médicale professionnelle.",
                    "⚠️ Consultez toujours un médecin pour un diagnostic définitif et un traitement approprié.",
                    "⚠️ Ce rapport ne remplace pas une consultation médicale en personne.",
                    "✅ En cas d'urgence, contactez immédiatement les services d'urgence (112).",
                    "✅ Conservez ce rapport pour votre dossier médical personnel.",
                    "✅ Partagez ce rapport avec votre médecin traitant lors de votre prochaine consultation."
                ]
                
                for warning in warnings:
                    if warning.startswith("⚠️"):
                        story.append(Paragraph(warning, self.styles['Alert']))
                    else:
                        story.append(Paragraph(warning, self.styles['Success']))
                
                story.append(Spacer(1, 30))
                
                # Section 7: Informations techniques
                story.append(Paragraph("7. INFORMATIONS TECHNIQUES", self.styles['SectionTitle']))
                
                tech_info_data = [
                    ['Modèle IA utilisé:', 'MedGemma 4B (Google)'],
                    ['Version du système:', 'Medical Diagnosis AI v1.0'],
                    ['Date de génération:', datetime.now().strftime('%d/%m/%Y à %H:%M')],
                    ['ID du rapport:', str(diagnosis_data['_id'])],
                    ['Type d\'analyse:', 'Analyse d\'image médicale par IA']
                ]
                
                tech_table = Table(tech_info_data, colWidths=[4.5*cm, 7.5*cm])
                tech_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f1f5f9')),
                    ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#64748b')),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0'))
                ]))
                
                story.append(tech_table)
                
                # Construire le PDF avec en-tête et pied de page
                doc.build(story, onFirstPage=self._create_header, onLaterPages=self._create_header)
                
                return tmp_file.name
        
        except Exception as e:
            print(f"Erreur lors de la génération du rapport: {e}")
            return None
    
    def generate_summary_report(self, diagnoses_list, user_data=None):
        """Générer un rapport de synthèse pour plusieurs diagnostics"""
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                doc = SimpleDocTemplate(
                    tmp_file.name,
                    pagesize=A4,
                    rightMargin=2*cm,
                    leftMargin=2*cm,
                    topMargin=4*cm,
                    bottomMargin=3*cm
                )
                
                story = []
                
                # Titre
                story.append(Paragraph("RAPPORT DE SYNTHÈSE MÉDICALE", self.styles['MainTitle']))
                story.append(Spacer(1, 30))
                
                # Informations générales
                story.append(Paragraph("1. INFORMATIONS GÉNÉRALES", self.styles['SectionTitle']))
                
                summary_data = [
                    ['Nombre de diagnostics:', str(len(diagnoses_list))],
                    ['Période:', f"Du {min(d['created_at'] for d in diagnoses_list).strftime('%d/%m/%Y')} au {max(d['created_at'] for d in diagnoses_list).strftime('%d/%m/%Y')}"],
                    ['Date de génération:', datetime.now().strftime('%d/%m/%Y à %H:%M')]
                ]
                
                if user_data:
                    summary_data.append(['Patient:', user_data['username']])
                
                summary_table = Table(summary_data, colWidths=[4*cm, 8*cm])
                summary_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8fafc')),
                    ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#374151')),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 11),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                    ('TOPPADDING', (0, 0), (-1, -1), 8),
                    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb'))
                ]))
                
                story.append(summary_table)
                story.append(Spacer(1, 25))
                
                # Tableau des diagnostics
                story.append(Paragraph("2. RÉCAPITULATIF DES DIAGNOSTICS", self.styles['SectionTitle']))
                
                # En-têtes du tableau
                headers = ['Date', 'ID Patient', 'Confiance', 'Statut', 'Symptômes']
                table_data = [headers]
                
                for diagnosis in diagnoses_list:
                    date_str = diagnosis['created_at'].strftime('%d/%m/%Y') if hasattr(diagnosis['created_at'], 'strftime') else str(diagnosis['created_at'])
                    confidence_str = f"{diagnosis['confidence']:.1%}"
                    symptoms_preview = diagnosis.get('symptoms', 'N/A')[:50] + "..." if len(diagnosis.get('symptoms', '')) > 50 else diagnosis.get('symptoms', 'N/A')
                    
                    table_data.append([
                        date_str,
                        diagnosis['patient_id'],
                        confidence_str,
                        diagnosis['status'].replace('_', ' ').title(),
                        symptoms_preview
                    ])
                
                # Créer le tableau avec des largeurs de colonnes appropriées
                col_widths = [2.5*cm, 2.5*cm, 2*cm, 2.5*cm, 4.5*cm]
                summary_table = Table(table_data, colWidths=col_widths)
                summary_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#ffffff'), colors.HexColor('#f9fafb')])
                ]))
                
                story.append(summary_table)
                story.append(Spacer(1, 30))
                
                # Statistiques
                story.append(Paragraph("3. STATISTIQUES", self.styles['SectionTitle']))
                
                status_counts = {}
                for diagnosis in diagnoses_list:
                    status = diagnosis['status']
                    status_counts[status] = status_counts.get(status, 0) + 1
                
                stats_data = []
                for status, count in status_counts.items():
                    percentage = (count / len(diagnoses_list)) * 100
                    stats_data.append([
                        status.replace('_', ' ').title(),
                        str(count),
                        f"{percentage:.1f}%"
                    ])
                
                if stats_data:
                    stats_table = Table(stats_data, colWidths=[6*cm, 3*cm, 3*cm])
                    stats_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8fafc')),
                        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#374151')),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 0), (-1, -1), 11),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                        ('TOPPADDING', (0, 0), (-1, -1), 6),
                        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb'))
                    ]))
                    
                    story.append(stats_table)
                
                story.append(Spacer(1, 30))
                
                # Avertissements
                story.append(Paragraph("4. AVERTISSEMENTS", self.styles['SectionTitle']))
                
                warnings = [
                    "⚠️ Ce rapport de synthèse contient des diagnostics générés par IA nécessitant une validation médicale.",
                    "⚠️ Consultez un professionnel de santé pour toute décision médicale.",
                    "✅ Ce rapport peut être utilisé comme support pour votre dossier médical."
                ]
                
                for warning in warnings:
                    if warning.startswith("⚠️"):
                        story.append(Paragraph(warning, self.styles['Alert']))
                    else:
                        story.append(Paragraph(warning, self.styles['Success']))
                
                # Construire le PDF
                doc.build(story, onFirstPage=self._create_header, onLaterPages=self._create_header)
                
                return tmp_file.name
        
        except Exception as e:
            print(f"Erreur lors de la génération du rapport de synthèse: {e}")
            return None 