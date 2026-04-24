from datetime import datetime
import os
from functools import wraps

from flask import (
    Flask,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    send_from_directory,
    url_for,
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

app = Flask(__name__, template_folder="app/templates", static_folder="app/static")
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-me")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(BASE_DIR, 'mehendi.db')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    favorites = db.relationship("Favorite", back_populates="user", cascade="all, delete-orphan")


class Design(db.Model):
    __tablename__ = "designs"

    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    keyword_tags = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    favorites = db.relationship("Favorite", back_populates="design", cascade="all, delete-orphan")


class Favorite(db.Model):
    __tablename__ = "favorites"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    design_id = db.Column(db.Integer, db.ForeignKey("designs.id"), primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="favorites")
    design = db.relationship("Design", back_populates="favorites")


def serialize_design(design, user_id=None):
    liked = False
    if user_id:
        liked = Favorite.query.filter_by(user_id=user_id, design_id=design.id).first() is not None
    return {
        "id": design.id,
        "image_url": design.image_url,
        "category": design.category,
        "description": design.description,
        "keyword_tags": design.keyword_tags,
        "liked": liked,
    }


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login_page"))
        return fn(*args, **kwargs)

    return wrapper


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user_id = session.get("user_id")
        if not user_id:
            return redirect(url_for("login_page"))
        user = db.session.get(User, user_id)
        if not user or not user.is_admin:
            return redirect(url_for("dashboard"))
        return fn(*args, **kwargs)

    return wrapper


@app.route("/")
def home():
    featured = Design.query.order_by(Design.created_at.desc()).limit(8).all()
    return render_template("index.html", featured=featured)


@app.route("/login")
def login_page():
    return render_template("login.html")


@app.route("/signup")
def signup_page():
    return render_template("signup.html")


@app.route("/dashboard")
@login_required
def dashboard():
    user = db.session.get(User, session["user_id"])
    recs = Design.query.order_by(Design.created_at.desc()).limit(6).all()
    return render_template("dashboard.html", user=user, recommendations=recs)


@app.route("/gallery")
def gallery():
    return render_template("gallery.html")


@app.route("/favorites")
@login_required
def favorites_page():
    return render_template("favorites.html")


@app.route("/about")
def about_page():
    return render_template("about.html")


@app.route("/contact")
def contact_page():
    return render_template("contact.html")


@app.route("/admin")
@admin_required
def admin_page():
    categories = sorted({d.category for d in Design.query.all()})
    return render_template("admin.html", categories=categories)


@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


# ---- API ----
@app.route("/api/signup", methods=["POST"])
def api_signup():
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if len(name) < 2 or "@" not in email or len(password) < 6:
        return jsonify({"error": "Invalid input. Name/email/password requirements not met."}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered."}), 409

    user = User(name=name, email=email, password=generate_password_hash(password), is_admin=False)
    db.session.add(user)
    db.session.commit()
    session["user_id"] = user.id
    return jsonify({"message": "Signup successful", "redirect": url_for("dashboard")})


@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return jsonify({"error": "Invalid credentials."}), 401

    session["user_id"] = user.id
    return jsonify({"message": "Login successful", "redirect": url_for("dashboard")})


@app.route("/api/logout", methods=["POST"])
def api_logout():
    session.clear()
    return jsonify({"message": "Logged out"})


@app.route("/api/designs", methods=["GET"])
def api_designs():
    query = request.args.get("q", "").strip().lower()
    category = request.args.get("category", "").strip().lower()

    q = Design.query
    if category:
        q = q.filter(db.func.lower(Design.category) == category)
    if query:
        like = f"%{query}%"
        q = q.filter(
            db.or_(
                db.func.lower(Design.description).like(like),
                db.func.lower(Design.keyword_tags).like(like),
                db.func.lower(Design.category).like(like),
            )
        )

    designs = q.order_by(Design.created_at.desc()).all()
    user_id = session.get("user_id")
    return jsonify([serialize_design(d, user_id) for d in designs])


@app.route("/api/categories", methods=["GET"])
def api_categories():
    categories = sorted({d.category for d in Design.query.all()})
    return jsonify(categories)


@app.route("/api/favorites", methods=["GET"])
@login_required
def api_favorites():
    user_id = session["user_id"]
    favorites = (
        db.session.query(Design)
        .join(Favorite, Favorite.design_id == Design.id)
        .filter(Favorite.user_id == user_id)
        .order_by(Favorite.created_at.desc())
        .all()
    )
    return jsonify([serialize_design(d, user_id) for d in favorites])


@app.route("/api/favorites/<int:design_id>", methods=["POST"])
@login_required
def api_add_favorite(design_id):
    user_id = session["user_id"]
    design = db.session.get(Design, design_id)
    if not design:
        return jsonify({"error": "Design not found."}), 404
    existing = Favorite.query.filter_by(user_id=user_id, design_id=design_id).first()
    if existing:
        return jsonify({"message": "Already saved."})

    db.session.add(Favorite(user_id=user_id, design_id=design_id))
    db.session.commit()
    return jsonify({"message": "Saved to favorites."})


@app.route("/api/favorites/<int:design_id>", methods=["DELETE"])
@login_required
def api_remove_favorite(design_id):
    user_id = session["user_id"]
    favorite = Favorite.query.filter_by(user_id=user_id, design_id=design_id).first()
    if not favorite:
        return jsonify({"error": "Favorite not found."}), 404

    db.session.delete(favorite)
    db.session.commit()
    return jsonify({"message": "Removed from favorites."})


@app.route("/api/admin/upload", methods=["POST"])
@admin_required
def api_admin_upload():
    category = request.form.get("category", "").strip()
    description = request.form.get("description", "").strip()
    tags = request.form.get("tags", "").strip().lower()
    image = request.files.get("image")

    if not category or not description or not image:
        return jsonify({"error": "Category, description, and image are required."}), 400
    if not allowed_file(image.filename):
        return jsonify({"error": "Unsupported file type."}), 400

    filename = secure_filename(f"{datetime.utcnow().timestamp()}_{image.filename}")
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    image.save(filepath)

    design = Design(
        image_url=url_for("uploaded_file", filename=filename),
        category=category,
        description=description,
        keyword_tags=tags,
    )
    db.session.add(design)
    db.session.commit()
    return jsonify({"message": "Design uploaded successfully."})


@app.route("/api/admin/designs/<int:design_id>", methods=["DELETE"])
@admin_required
def api_admin_delete_design(design_id):
    design = db.session.get(Design, design_id)
    if not design:
        return jsonify({"error": "Design not found."}), 404

    if design.image_url.startswith("/uploads/"):
        filename = design.image_url.replace("/uploads/", "", 1)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        if os.path.exists(filepath):
            os.remove(filepath)

    db.session.delete(design)
    db.session.commit()
    return jsonify({"message": "Design deleted."})


def seed_data():
    if Design.query.count() > 0:
        return

    placeholders = [
        ("Bridal Mehendi", "Intricate bridal design with peacocks and paisleys", "bridal,wedding,intricate", "https://images.unsplash.com/photo-1590845947670-c009801ffa74?auto=format&fit=crop&w=900&q=80"),
        ("Arabic Mehendi", "Bold floral arabic style flowing from wrist to finger", "arabic,bold,floral", "https://images.unsplash.com/photo-1610173827002-62c0f1f32f76?auto=format&fit=crop&w=900&q=80"),
        ("Minimal Mehendi", "Simple finger-focused modern minimal mehendi", "minimal,simple,modern", "https://images.unsplash.com/photo-1626197031507-c17099713f64?auto=format&fit=crop&w=900&q=80"),
        ("Traditional Mehendi", "Classic mandala centerpiece with symmetrical details", "traditional,mandala,classic", "https://images.unsplash.com/photo-1583391733981-02f5f8f5fbc9?auto=format&fit=crop&w=900&q=80"),
        ("Modern Designs", "Fusion pattern combining geometric and leafy motifs", "modern,geometric,fusion", "https://images.unsplash.com/photo-1605000797499-95a51c5269ae?auto=format&fit=crop&w=900&q=80"),
        ("Bridal Mehendi", "Full-hand bridal composition with dense motifs", "bridal,full hand,dense", "https://images.unsplash.com/photo-1591635113902-48d0f77f7485?auto=format&fit=crop&w=900&q=80"),
    ]

    for category, description, tags, url in placeholders:
        db.session.add(Design(category=category, description=description, keyword_tags=tags, image_url=url))

    if not User.query.filter_by(email="admin@mehendi.com").first():
        db.session.add(
            User(
                name="Admin",
                email="admin@mehendi.com",
                password=generate_password_hash("Admin@123"),
                is_admin=True,
            )
        )

    db.session.commit()


with app.app_context():
    db.create_all()
    seed_data()


if __name__ == "__main__":
    app.run(debug=True)
