## Running the Application
1. Clone the repository:
```bash
git clone ""
cd <repository-name>
```
2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```
3. Install the required packages:
```bash
pip install -r requirements.txt
```
4. Run the application:
```bash
python run.py
```

## Environment Variables
- `DATABASE_URL`: MySQL connection string. Example: `mysql+pymysql://username:password@localhost/dbname?ssl=REQUIRED`
- `FLASK_ENV`: Set to `development` for development mode.
- `FLASK_APP`: The entry point of the application. Set to `run.py`.

## Migration
1. Initialize the migration (only once, I already did this so you can skip this step unless you remove the migrations folder):
```bash
flask db init
```
2. Create a migration script:
```bash
flask db migrate -m "Initial migration."
```
3. Apply the migration:
```bash
flask db upgrade
```
4. If you need to downgrade:
```bash
flask db downgrade
```
5. Check the current migration version:
```bash
flask db current
```

