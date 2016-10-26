import sae
import os
import sys
from driving import wsgi

app_root = os.path.dirname(__file__) 
sys.path.insert(0, os.path.join(app_root, 'django-filter-0.9.2')) 


application = sae.create_wsgi_app(wsgi.application)