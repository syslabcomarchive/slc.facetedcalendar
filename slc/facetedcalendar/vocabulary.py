from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

class FacetedCalendarParameters(object):
    """ Provides a list of catalog indexes that can be used for faceted
        searching on a calendar.
    """
    implements(IVocabularyFactory)

    def __call__(self, context):
        # This used to be determined dynamically, but for now to keep things
        # simple we restrict it to these...
        items = []
        items.append(SimpleTerm('Creator'))
        items.append(SimpleTerm('SearchableText'))
        items.append(SimpleTerm('review_state'))
        return SimpleVocabulary(items)

FacetedCalendarParametersFactory = FacetedCalendarParameters()
