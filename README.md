use with python 3.6

python -m venv YourVirtualEnvName
YourVirtualEnvName\Scripts\activate
python -m pip install -r requirements.txt
cd attendanceProject
configure settings.py and add your msql database information
python manage.py makemigrations #-- if changes in model file
python manage.py migrate
python manage.py runserver