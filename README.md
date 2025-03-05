```markdown
              # ShopEasy Customer Behavior Analytics Project

## 📋 Project Overview
A data-driven analytics pipeline that processes customer journey data,
generates business insights, and creates PDF reports. Includes SQL data insertion,
marketing/customer experience analysis, and strategic recommendations.

## 🛠 Prerequisites
- Python 3.8+
- MySQL Server
- MySQL Connector/Python
- Required Python packages (install via `requirements.txt`)

## 📥 Dependencies
```bash
# requirements.txt
pandas
sqlalchemy
mysql-connector-python
reportlab
textblob
python-dotenv  # Recommended for credential management
```

## 🔧 Setup Instructions

### 1. Database Configuration
1. Create MySQL user with required privileges:
```sql
CREATE USER 'shopeasy_user'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON ShopEasy.* TO 'shopeasy_user'@'localhost';
FLUSH PRIVILEGES;
```

2. Replace default credentials in all scripts:
```python
# In all files (01-07), replace:
engine = create_engine('mysql+mysqlconnector://root:456123@localhost/ShopEasy')

# With either:
engine = create_engine('mysql+mysqlconnector://shopeasy_user:your_secure_password@localhost/ShopEasy')
# OR using environment variables (recommended):
from dotenv import load_dotenv
import os
load_dotenv()
engine = create_engine(f'mysql+mysqlconnector://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}@localhost/ShopEasy')
```

### 2. File Structure Setup
```bash
project-root/
├── data/                 # CSV source files
├── results/              # Generated reports (auto-created)
├── 01_CBA_Data_Insertion-Script.py
├── 02_CBA_Overal_Report.py
└── ... (other scripts in numerical order)
```

### 3. Initial Data Load
```bash
python 01_CBA_Data_Insertion-Script.py
```

## 🚀 Execution Order
1. Data Insertion: `01_*.py`
2. Core Analysis: `02_*.py`
3. Marketing Analysis: `03_*.py` → `04_*.py`
4. Customer Experience: `05_*.py` → `06_*.py`
5. Final Recommendations: `07_*.py`

## 📄 Expected Outputs
- `results/` directory will contain:
  - Marketing_Analysis_SQL__Table.pdf
  - Cx_Experience_Analysis_SQL_Tables.pdf
  - ShopEasy_Final_Report.pdf
  - ShopEasy_Business_Recommendations.pdf
  - customer_experience_recommendations.txt
  - Marketing_recommendation.txt

## 🔍 Project Structure
| Script | Purpose |
|--------|---------|
| 01_* | Database creation & data insertion |
| 02_* | Comprehensive customer behavior analysis |
| 03-04_* | Marketing channel performance reports |
| 05-06_* | Customer experience insights |
| 07_* | Executive business recommendations |

## 🚨 Troubleshooting
1. **MySQL Connection Issues**:
   - Verify user privileges
   - Check firewall settings
   - Ensure MySQL service is running

2. **Missing Dependencies**:
   ```bash
   pip install -r requirements.txt
   python -m textblob.download_corpora  # For sentiment analysis
   ```

3. **File Path Errors**:
   - Ensure relative path structure is maintained
   - Create missing directories manually if needed

```

