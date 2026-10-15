# UndaJamii

**Community Facility Maintenance Tracker**

UndaJamii (from Swahili *unda* = "build/create" and *jamii* = "community") is a
lightweight web application for logging and tracking maintenance issues at
community facilities — halls, playgrounds, water points, toilets, and more.

## Features

- Register issues with facility, description, priority, reporter, assigned staff, and due date
- View, search, filter, and sort all issues
- Update status through a full lifecycle: Open → In Progress → Resolved
- Attach comments and progress notes to any ticket
- Automatic overdue detection — past-due issues are flagged
- Dashboard with live summary statistics
- Status breakdown chart and monthly trend chart
- Export all issues as CSV for reporting
- Bulk-clear resolved issues
- Dark mode with persistent preference
- Mobile-first layout — works on phone, tablet, and desktop

## Screenshots

![Home](screenshots/01_home_light.png)
![Stats](screenshots/03_stats.png)

## Technology

- **Python 3.12+** — the runtime
- **Flask** — the web framework
- **SQLite** — self-contained single-file database
- **Jinja2** — HTML templating
- **Bootstrap 5 + Bootstrap Icons** — UI components (loaded from CDN)
- **Chart.js** — charts (loaded from CDN)

## Getting Started

### Prerequisites

- Python 3.10 or newer
- pip (bundled with Python)

### Installation

```bash
git clone <your-repo-url> undajamii
cd undajamii
python -m pip install -r requirements.txt
```

### Run

```bash
python app.py
```

Open http://127.0.0.1:5000 in your browser.

The database file `undajamii.db` is created automatically on first run.

## Project Structure

```
UndaJamii-Web/
├── app.py               # Flask routes and form handling
├── database.py          # SQLite helpers
├── requirements.txt     # Python dependencies
├── undajamii.db         # Database (auto-created)
├── static/
│   ├── style.css        # Custom styles
│   └── app.js           # Theme toggle, toast auto-dismiss
└── templates/
    ├── base.html        # Shared layout
    ├── index.html       # Home page
    ├── register.html    # Register form
    ├── search.html      # Search page
    ├── edit.html        # Edit + comments
    ├── filter.html      # Filter page
    └── stats.html       # Statistics and charts
```

## Usage

| Action | Where |
|--------|-------|
| See recent issues | Home |
| Register a new issue | Bottom nav → Register |
| Find by ticket ID | Bottom nav → Search |
| Apply filters | Funnel icon (top bar) |
| See charts and export | Bar-chart icon (top bar) |
| Toggle theme | Bottom nav → Theme |

## License

Free to use and modify for community and educational purposes.