# imports
import six

from django.db.models.fields.related_descriptors import ReverseManyToOneDescriptor
from django.db.models.fields.related_descriptors import ReverseOneToOneDescriptor

from python_utilities.objects.object_helper import ObjectHelper
from python_utilities.django_utils.django_model_helper import DjangoModelHelper

from sourcenet.data.person_data import PersonData
from sourcenet.models import Person

# get list of reverse lookup sets in Person.
reverse_lookup_name_list = PersonData.get_person_related_set_attribute_names()

# and again, to test cache - should not be any output.
reverse_lookup_name_list = PersonData.get_person_related_set_attribute_names()