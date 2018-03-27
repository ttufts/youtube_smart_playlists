from oauth2client.tools import run_flow
from oauth2client.file import Storage
from google_auth_oauthlib.flow import InstalledAppFlow
from oauth2client.client import flow_from_clientsecrets

CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE,
                               scope=SCOPES,
                               redirect_uri="http://127.0.0.1/auth_return")

auth_uri = flow.step1_get_authorize_url()
code = raw_input("{}:\n".format(auth_uri))
credentials = flow.step2_exchange(code)

storage = Storage('creds.data')

storage.put(credentials)

print "access_token: %s" % credentials.access_token
