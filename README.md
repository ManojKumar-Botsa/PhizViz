# PhishViz - Advanced Phishing Detection System

PhishViz is a comprehensive web-based application designed to detect and analyze various forms of phishing threats including emails, URLs, documents, and steganography in images. The system uses machine learning and heuristic-based approaches to provide real-time threat analysis.

## Features

- **Email Analyzer**: ML-powered email phishing detection
- **Link Detector**: URL analysis with risk scoring
- **Document Scanner**: Macro and embedded link detection
- **Steganography Kit**: Hidden data detection in images
- **Threat Dashboard**: Real-time monitoring and statistics
- **Reports**: Exportable scan results and history

## Project Structure

### Backend Files

#### Core Application
- `app.py` - Main Flask application server handling API endpoints and routing
- `ml.py` - Machine learning model for email classification using trained algorithms
- `generator.py` - Data generation utilities for training and testing datasets

#### Data and Configuration
- `requirements.txt` - Python dependencies and versions
- `dataset.csv` - Training dataset for ML models

### Modules Directory (`modules/`)

#### Core Detection Modules
- `email_analyzer/` - Email parsing and ML-based phishing detection
  - `__init__.py` - Module initialization
  - `predict.py` - ML prediction logic for emails
- `link_detector/` - URL analysis and risk assessment
  - `__init__.py` - Module initialization
  - `url_checks.py` - URL validation and heuristic checks
  - `verdict.py` - Risk scoring and verdict generation
- `document_scanner/` - File analysis for malicious content
  - `__init__.py` - Module initialization
  - `embedded_links.py` - Detection of hidden links in documents
  - `file_checks.py` - General file validation
  - `macro_scan.py` - Macro virus detection
- `risk_engine/` - Centralized risk assessment
  - `__init__.py` - Module initialization
  - `score.py` - Risk scoring algorithms
- `steganography_kit/` - Image steganography analysis
  - `__init__.py` - Module initialization
  - `image_analysis.py` - Image processing and analysis
  - `metadata_check.py` - EXIF and metadata examination

### Frontend Directory (`frontend/`)

#### HTML Pages
- `index.html` - Homepage with feature overview and navigation
- `email-scan.html` - Email analysis interface
- `link-scan.html` - URL scanning interface
- `document-scan.html` - File upload and scanning interface
- `stego-kit.html` - Image steganography analysis interface
- `dashboard.html` - Threat monitoring dashboard
- `reports.html` - Scan results and export functionality

#### Assets and Styling
- `assets/images/` - Logo and interface images
- `css/` - Stylesheets for responsive design
  - `style.css` - Main styling and layout
  - `buttons.css` - Button component styles
  - `cards.css` - Card component styles with glassmorphism
  - `background.css` - Background effects and animations
- `js/` - Client-side JavaScript
  - `main.js` - Homepage animations and effects
  - `email.js` - Email scanning functionality
  - `link.js` - URL analysis client logic
  - `document.js` - File upload and processing
  - `stego.js` - Image analysis interface
  - `dashboard.js` - Dashboard data visualization
  - `reports.js` - Report generation and export

### Data Directory (`data/`)

- `malicious_urls.txt` - Known malicious URL database
- `safe_urls.txt` - Whitelist of safe URLs
- `sample_emails/` - Test email samples for validation

### Documentation (`docs/`)

- `abstract.txt` - Project abstract and overview
- `architecture.txt` - System architecture documentation
- `module_description.txt` - Detailed module descriptions
- `viva_notes.txt` - Presentation and defense notes

### Reports (`reports/`)

- `scan_reports.json` - Stored scan results and history

### Backup and Templates

- `backup/` - Backup of previous versions
- `templates/` - Flask template files (legacy)

## Installation and Setup

### Prerequisites

- Python 3.8+
- Flask
- Required ML libraries (scikit-learn, pandas, etc.)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd PhishViz
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

4. Open browser to `http://localhost:5000`

## Usage

### Web Interface

1. **Homepage**: Overview of all detection features
2. **Email Analyzer**: Paste email content for ML-based analysis
3. **Link Detector**: Enter URLs for risk assessment
4. **Document Scanner**: Upload files to check for macros and embedded threats
5. **Steganography Kit**: Upload images to detect hidden data
6. **Dashboard**: View scan statistics and recent activity
7. **Reports**: Export scan results in JSON format

### API Endpoints

- `POST /analyze-email` - Email analysis
- `POST /analyze-url` - URL analysis
- `POST /analyze-document` - File analysis
- `POST /analyze-image` - Image steganography analysis
- `GET /dashboard-data` - Dashboard statistics
- `GET /reports` - Scan reports

## Technology Stack

- **Backend**: Python Flask
- **Frontend**: HTML5, CSS3, JavaScript
- **ML**: Scikit-learn, Pandas
- **Styling**: Custom CSS with glassmorphism effects
- **Database**: JSON-based storage

## Security Features

- Input validation and sanitization
- File type restrictions
- Rate limiting (recommended for production)
- Secure file handling

## Development

### Adding New Detection Modules

1. Create new module in `modules/`
2. Implement analysis logic
3. Add API endpoint in `app.py`
4. Create frontend interface
5. Update navigation and routing

### Training ML Models

Use `generator.py` to create training data and `ml.py` for model training.

## Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## License

This project is for educational and research purposes.

## Contact

For questions or contributions, please open an issue or contact the development team.</content>
<parameter name="filePath">c:\Users\kanne\Phishviz\README.md