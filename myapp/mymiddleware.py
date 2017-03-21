
from urllib import quote
from django.http import HttpResponseRedirect
from django.contrib.auth import SESSION_KEY

#quit after 900s
class expiretimeset(object):
    def process_request(self, request):
        request.session.set_expiry(3600)