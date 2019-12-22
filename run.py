from app import app
from app import views

import logging
logging.basicConfig(filename='myWebApp.log', filemode='w', format='%(levelname)s %(asctime)s : %(message)s', level=logging.INFO)
logging.info('Started')

app.run(debug=True)