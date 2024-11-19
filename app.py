from flask import Flask, render_template, request
from pydub import AudioSegment
import os
import logging

app = Flask(__name__)

# Configuration des dossiers
UPLOAD_FOLDER = 'uploads'
EXTRACT_FOLDER = 'extracted'

# Assurez-vous que les dossiers nécessaires existent
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(EXTRACT_FOLDER, exist_ok=True)

# Configuration des logs
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

@app.route('/')
def index():
    """
    Page principale avec formulaire HTML
    """
    logging.info("Accès à la page principale.")
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    """
    Gérer l'upload, sauvegarder le fichier et extraire une portion d'audio.
    """
    try:
        logging.info("Requête POST reçue pour extraire l'audio.")

        # Étape 1 : Récupérer le fichier et les données du formulaire
        if 'file' not in request.files:
            logging.error("Aucun fichier trouvé dans la requête.")
            return "Aucun fichier trouvé dans la requête."

        file = request.files['file']
        if file.filename == '':
            logging.error("Aucun fichier sélectionné.")
            return "Aucun fichier sélectionné."

        logging.info(f"Fichier reçu : {file.filename}")

        # Sauvegarder le fichier uploadé
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)
        logging.info(f"Fichier sauvegardé à : {filepath}")

        # Étape 2 : Récupérer les paramètres du formulaire
        try:
            start_min = int(request.form['start_min'])
            start_sec = int(request.form['start_sec'])
            end_min = int(request.form['end_min'])
            end_sec = int(request.form['end_sec'])
            output_format = request.form['output_format']
            output_name = request.form['output_name']
        except Exception as e:
            logging.error(f"Erreur dans les données du formulaire : {e}")
            return f"Erreur dans les données du formulaire : {e}"

        logging.info(f"Données du formulaire reçues : "
                     f"start_min={start_min}, start_sec={start_sec}, "
                     f"end_min={end_min}, end_sec={end_sec}, "
                     f"output_format={output_format}, output_name={output_name}")

        # Étape 3 : Convertir les timestamps en millisecondes
        start_time = (start_min * 60 + start_sec) * 1000
        end_time = (end_min * 60 + end_sec) * 1000
        logging.info(f"Timestamps convertis : début={start_time}ms, fin={end_time}ms.")

        # Étape 4 : Charger le fichier audio
        try:
            audio = AudioSegment.from_file(filepath)
            logging.info("Fichier audio chargé avec succès.")
        except Exception as e:
            logging.error(f"Erreur lors du chargement du fichier audio : {e}")
            return f"Erreur lors du chargement du fichier audio : {e}"

        # Étape 5 : Extraire la portion audio
        try:
            extracted_audio = audio[start_time:end_time]
            logging.info("Extraction de l'audio réussie.")
        except Exception as e:
            logging.error(f"Erreur lors de l'extraction de l'audio : {e}")
            return f"Erreur lors de l'extraction de l'audio : {e}"

        # Étape 6 : Sauvegarder l'extrait
        try:
            output_path = os.path.join(EXTRACT_FOLDER, f"{output_name}.{output_format}")
            extracted_audio.export(output_path, format=output_format)
            logging.info(f"Extrait sauvegardé à : {output_path}")
            return f"Extraction réussie ! Fichier sauvegardé : {output_path}"
        except Exception as e:
            logging.error(f"Erreur lors de la sauvegarde de l'extrait audio : {e}")
            return f"Erreur lors de la sauvegarde de l'extrait audio : {e}"

    except Exception as e:
        logging.error(f"Une erreur s'est produite : {e}")
        return f"Erreur : {e}"

if __name__ == '__main__':
    logging.info("Lancement du serveur Flask.")
    app.run(debug=True)