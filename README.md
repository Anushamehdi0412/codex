# Mehendi Muse - Full-Stack Mehendi Design Website

A modern, responsive, Pinterest-style Mehendi design platform with a Flask backend, SQLite database, elegant glassmorphism UI, auth, favorites, admin uploads, search/filter, and dark/light mode.

## Tech Stack
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Backend:** Python + Flask + REST API
- **Database:** SQLite (via SQLAlchemy)

## Folder Structure
```
/workspace/codex
├── app.py
├── requirements.txt
├── mehendi.db                  # auto-created
├── uploads/                    # admin uploaded images
├── app/
│   ├── static/
│   │   ├── css/style.css
│   │   ├── js/
│   │   │   ├── main.js
│   │   │   ├── home.js
│   │   │   ├── auth.js
│   │   │   ├── gallery.js
│   │   │   ├── favorites.js
│   │   │   ├── favorites-list.js
│   │   │   └── admin.js
│   └── templates/
│       ├── base.html
│       ├── index.html
│       ├── login.html
│       ├── signup.html
│       ├── dashboard.html
│       ├── gallery.html
│       ├── favorites.html
│       ├── admin.html
│       ├── about.html
│       └── contact.html
└── README.md
```

## Features Implemented
1. Home page with hero section, featured carousel, category previews.
2. Signup/Login with input validation + hashed passwords.
3. User dashboard with personalized recommendations and quick save favorites.
4. Gallery with category filters, search, hover effects, full-image lightbox.
5. Favorites saved per user in DB.
6. Admin panel to upload new design images and manage categories.
7. REST APIs for auth, designs, favorites, categories, upload/delete.
8. SQLite schema includes Users, Designs, Favorites.
9. About + Contact pages, social footer links.
10. Smooth animations, modern cards, loading text, dark/light mode toggle.

## Default Seed Data
- Several sample Mehendi designs from placeholder Unsplash image URLs.
- Admin user:
  - **Email:** `admin@mehendi.com`
  - **Password:** `Admin@123`

## Run Instructions
1. **Create virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run app**
   ```bash
   python app.py
   ```
4. Open browser at: `http://127.0.0.1:5000`

## API Endpoints
- `POST /api/signup`
- `POST /api/login`
- `POST /api/logout`
- `GET /api/designs?q=&category=`
- `GET /api/categories`
- `GET /api/favorites`
- `POST /api/favorites/<design_id>`
- `DELETE /api/favorites/<design_id>`
- `POST /api/admin/upload` (admin only)
- `DELETE /api/admin/designs/<design_id>` (admin only)

## Notes
- Uploaded images are stored in `uploads/` and served from `/uploads/<filename>`.
- You can switch to MongoDB later by replacing SQLAlchemy models with PyMongo logic.
