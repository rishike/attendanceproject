use with python 3.6

`python -m venv YourVirtualEnvName`

### for windows users
`YourVirtualEnvName\Scripts\activate` 

### for mac user
`source bin\activate` 


`python -m pip install -r requirements.txt`

`cd attendanceProject`
`configure settings.py and add your msql database information`

`python manage.py makemigrations`  <!-- if changes in model file -->

`python manage.py migrate`

`python manage.py runserver`


### For login  and create account for first time admin
`python manage.py shell`

`from accounts.models import Accounts`

`from django.contrib.auth.hashers import make_password`

`password = make_password('yourdesiredpassword')`

`username = 'qwerty'`

`name = 'qwerty asdf'`

`active = True`

`type = 'Admin'`

`email = 'qwerty@mail.com'`

`Accounts.objects.create(username=username, password=password, email=email, active=active, type=type, name=name)`

### make folder of your username in capture folder

`mkdir capture\yourusername\`
