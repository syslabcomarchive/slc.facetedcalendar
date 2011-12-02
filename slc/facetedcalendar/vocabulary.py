from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
from Products.PluginIndexes.FieldIndex.FieldIndex import FieldIndex
from Products.CMFCore.utils import getToolByName

class FacetedCalendarParameters(object):
    """ Provides a list of catalog indexes that can be used for faceted
        searching on a calendar.
    """
    implements(IVocabularyFactory)

    def __call__(self, context):
        catalog = getToolByName(context, 'portal_catalog')
        items = []
        for index in catalog._catalog.indexes.values():
            if isinstance(index, FieldIndex):
                items.append(SimpleTerm(index.id))
            
        return SimpleVocabulary(items)

FacetedCalendarParametersFactory = FacetedCalendarParameters()
