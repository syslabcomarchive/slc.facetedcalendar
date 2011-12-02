from persistent.dict import PersistentDict
from Products.CMFCore.utils import getToolByName

def save_form_in_session(context, request):
    sdm = getToolByName(context, 'session_data_manager')
    session = sdm.getSessionData(create=True)
    path = '/'.join(context.getPhysicalPath())
    pdict = PersistentDict()
    pdict.update(request.form)
    session.set(path, pdict) 
