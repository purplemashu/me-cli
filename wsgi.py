# This file contains the WSGI configuration required to serve up your
# web application at http://<your-username>.pythonanywhere.com/
# It works by setting the variable 'application' to a WSGI handler of some
# description.
#
# The variable 'application' is exposed to the WSGI server as a WSGI
# callable.

import sys

# Add your project's directory to the sys.path.
# This is required for PythonAnywhere to find your app.
# Replace '/home/<your-username>/<your-project-directory>' with the actual path.
# For example: path = '/home/myusername/myproject'
path = '/home/UkonsDor/Ukons-Dor'
if path not in sys.path:
    sys.path.insert(0, path)

# Import the Flask app instance
from flask_app import app as application
