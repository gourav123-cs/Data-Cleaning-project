import os
import spacy
from datetime import datetime
from flask import Flask, request, jsonify, render_template, send_from_directory, redirect, url_for
from werkzeug.utils import secure_filename
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

# --- 1. App Initialization & Configuration ---
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SECRET_KEY'] = 'your-super-secret-key' # IMPORTANT: Change this for production
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# --- 2. NLP Model Loading ---
try:
    nlp = spacy.load("en_core_web_md")
except OSError:
    print("Downloading spaCy model 'en_core_web_md'...")
    os.system("python -m spacy download en_core_web_md")
    nlp = spacy.load("en_core_web_md")

# --- 3. In-memory "Databases" ---
documents_db = []
users_db = {} 

# --- 4. User Authentication Setup (Flask-Login) ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, username, department):
        self.id = id
        self.username = username
        self.department = department

def setup_users():
    global users_db
    users_data = {
        'eng_user': {'id': '1', 'department': 'Engineering'},
        'fin_user': {'id': '2', 'department': 'Financial'},
        'admin':    {'id': '3', 'department': 'Admin'},
    }
    for username, data in users_data.items():
        users_db[username] = User(id=data['id'], username=username, department=data['department'])

setup_users()

@login_manager.user_loader
def load_user(user_id):
    for user in users_db.values():
        if user.id == user_id:
            return user
    return None

# --- 5. Helper Functions ---
def extract_text(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f: return f.read()
    except Exception: return ""

def analyze_content(text):
    title, vendor, category = "Unknown Title", "Unknown Vendor", "General"
    lines = text.split('\n')
    if lines and len(lines[0].strip()) < 70: title = lines[0].strip()
    for line in lines[:10]:
        if "vendor:" in line.lower(): vendor = line.split(":", 1)[1].strip(); break
    categories = {'Engineering': ['technical', 'construction'], 'Financial': ['financial', 'revenue'], 'Legal': ['legal', 'contract'], 'Safety': ['safety', 'incident']}
    text_lower = text.lower()
    for cat, keywords in categories.items():
        if any(kw in text_lower for kw in keywords): category = cat; break
    return title, vendor, category

def create_snippet(text, query_tokens):
    sentences = text.split('.')
    best_sentence = ""
    max_matches = -1
    for sentence in sentences:
        matches = sum(1 for token in query_tokens if token in sentence.lower())
        if matches > max_matches: max_matches, best_sentence = matches, sentence
    if not best_sentence and sentences: best_sentence = sentences[0]
    snippet = (best_sentence.strip()[:200] + '...') if len(best_sentence.strip()) > 200 else best_sentence.strip()
    for token in query_tokens: snippet = snippet.replace(token, f"<b>{token}</b>")
    return snippet

# --- 6. Main Application Routes ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = users_db.get(request.form['username'])
        if user:
            login_user(user)
            return redirect(url_for('index'))
        return render_template('login.html', error="Invalid username")
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
@login_required
def upload_file_route():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        text = extract_text(filepath)
        title, vendor, category = analyze_content(text)
        documents_db.append({
            'id': len(documents_db) + 1, 'filename': filename, 'title': title, 'vendor': vendor,
            'category': category, 'department': current_user.department,
            'uploaded_by': current_user.username, 'uploaded_at': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'doc_obj': nlp(text)
        })
        return jsonify({'message': f"'{filename}' processed successfully!"}), 200
    return jsonify({'error': 'File upload failed'}), 500


@app.route('/search', methods=['GET'])
@login_required
def search_documents():
    query = request.args.get('q', '').lower()
    if not query: return jsonify([])
    query_doc = nlp(query)
    query_tokens = [token.text for token in query_doc if not token.is_stop and not token.is_punct]
    results = []
    accessible_docs = [doc for doc in documents_db if current_user.department == 'Admin' or doc['department'] == current_user.department]
    for doc in accessible_docs:
        keyword_score = sum(1 for token in query_tokens if token in doc['doc_obj'].text.lower())
        similarity_score = query_doc.similarity(doc['doc_obj']) if query_doc.vector_norm and doc['doc_obj'].vector_norm else 0.0
        total_score = (keyword_score * 10) + similarity_score
        if total_score > 0.5:
            results.append({
                'score': total_score, 'filename': doc['filename'], 'title': doc['title'],
                'category': doc['category'], 'uploaded_by': doc['uploaded_by'],
                'uploaded_at': doc['uploaded_at'], 'snippet': create_snippet(doc['doc_obj'].text, query_tokens)
            })
    return jsonify(sorted(results, key=lambda x: x['score'], reverse=True)[:10])

@app.route('/download/<filename>')
@login_required
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/view/<filename>')
@login_required
def view_file(filename):
    doc_record = next((doc for doc in documents_db if doc['filename'] == filename), None)
    if not doc_record or (current_user.department != 'Admin' and doc_record['department'] != current_user.department):
        return jsonify({"error": "Access denied"}), 403
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    try:
        return jsonify({"content": extract_text(filepath)})
    except FileNotFoundError:
        return jsonify({"error": "File not found on server"}), 404

# --- 7. Main Execution Point ---
if __name__ == '__main__':
    app.run(debug=True, port=5001)

