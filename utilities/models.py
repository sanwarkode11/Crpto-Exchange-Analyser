import sys
from abc import abstractmethod
from decimal import Decimal, InvalidOperation
from io import BytesIO

from PIL import Image
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.validators import MinLengthValidator
from django.db import models
from django.db.models import signals
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.fields import CreationDateTimeField
from localflavor.in_.models import INStateField
from phonenumber_field.modelfields import PhoneNumberField
from simple_history.models import HistoricalRecords

from .db_config import INITIAL_PROJECT_CONFIG_VALUES
from .requestMW import get_request
from .storage_backends import publicMediaStorage
from .utils import is_database_synchronized


class Address(models.Model):
    address1 = models.CharField(max_length=255, blank=False, null=False)
    address2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=False, null=False,
                            verbose_name="Village/Town",
                            help_text="This can be city, village, town etc or even same as district")
    # district = models.CharField(max_length=100, blank=False, null=False)
    state = INStateField(blank=False, null=False, verbose_name=_("State"))
    pincode = models.CharField(max_length=6, validators=[MinLengthValidator(6)], blank=False, null=False)

    def __str__(self):
        if self.address2 is None:
            return '{}, {}, {} - {}'.format(self.address1, self.city, self.state, self.pincode)
        else:
            return '{}, {}, {}, {} - {}'.format(self.address1, self.address2, self.city,
                                                    self.state, self.pincode)


class BaseModelWithCreatedInfo(models.Model):
    created_at = CreationDateTimeField(_('Created At'))
    created_by = models.ForeignKey(User, models.SET_NULL, related_name="+", editable=False, blank=True, null=True,
                                   verbose_name=_('Created By'))

    class Meta:
        abstract = True
        ordering = ['created_at']

    def save(self, **kwargs):
        # used only for objects created by web (not api or through scripts)

        if not self.id and not self.created_by:
            if get_request() != None and get_request().user.is_authenticated:
                self.created_by = get_request().user

        return super(BaseModelWithCreatedInfo, self).save(**kwargs)

    def __str__(self):
        return "{}".format(self.id)


class BaseModelWithName(BaseModelWithCreatedInfo):
    name = models.CharField(max_length=255, verbose_name=_('Name'))

    class Meta:
        abstract = True

    def __str__(self):
        return self.name.title()


class BaseModelWithUniqueName(BaseModelWithCreatedInfo):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        abstract = True
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, **kwargs):
        self.name = self.name.title()
        return super(BaseModelWithUniqueName, self).save(**kwargs)


class BaseModelWithNameAddressMobile(BaseModelWithName):
    mobile = PhoneNumberField(blank=True, null=True, verbose_name=_('Mobile'))
    address = models.OneToOneField(Address, on_delete=models.SET_NULL, blank=True, null=True, verbose_name=_('Address'))

    class Meta:
        abstract = True


def get_image_path(instance, filename):
    return '{0}'.format(filename)


def compressImage(uploadedImage):
    if 'image' in uploadedImage.content_type:
        imageTemproary = Image.open(uploadedImage)
        outputIoStream = BytesIO()
        # imageTemproaryResized = imageTemproary.resize(
        #     (1020, 573))  # Resize can be set to various varibale values in settings.py
        # converts png to jpeg
        if imageTemproary.mode in ("RGBA", "P"):
            imageTemproary = imageTemproary.convert("RGB")
        imageTemproary.save(outputIoStream, format='JPEG', quality=60)  # change quality according to requirement.
        outputIoStream.seek(0)
        uploadedImage = InMemoryUploadedFile(outputIoStream, 'ImageField', "%s.jpg" % uploadedImage.name.split('.')[0],
                                             'image/jpeg', sys.getsizeof(outputIoStream), None)
    return uploadedImage


class BaseImageModel(models.Model):
    image_file = models.ImageField(_("Image"), upload_to=get_image_path)
    image_caption = models.CharField(_("caption"), null=True, blank=True, max_length=255)

    class Meta:
        abstract = True

    def save(self, **kwargs):
        #  Removes the public aws url from image . Image will be saved with name in db
        self.image_file.name = self.image_file.name.replace(publicMediaStorage.url(""), "")

        if "http" in self.image_file.name or "https" in self.image_file.name:
            raise ValidationError("image being uploaded is an external image")

        super().save(**kwargs)


class BaseModelWithStatus(models.Model):
    _status = models.IntegerField(default=1, verbose_name=_("Status"))

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super(BaseModelWithStatus, self).__init__(*args, **kwargs)
        self._meta.get_field('_status').choices = [(tag.value, _(tag.name)) for tag in self.status_type_enum()]

    @abstractmethod
    def status_type_enum(self):
        pass

    @abstractmethod
    def set_status(self, tag_name):
        pass

    @property
    def status(self):
        if self._status is None:
            return None
        return self.status_type_enum()(self._status).name

    @status.setter
    def status(self, tag_name):
        self.set_status(tag_name)

    def set_non_initial_status(self, tag_name, validation_dict):
        if (self._status == None):
            raise ValueError(_("Please call set_initial_status"))
        else:
            if tag_name not in validation_dict.keys():
                raise ValueError(_('Invalid tagname: {0}'.format(tag_name)))
            else:
                for current_tag, prev_tags in validation_dict.items():
                    if tag_name == self.status_type_enum()[current_tag].name:
                        # validating that current status exist in  previous tags.
                        if any([self._status == self.status_type_enum()[prev_tag].value for prev_tag in prev_tags]):
                            self._status = self.status_type_enum()[current_tag].value
                        else:
                            raise ValueError(_("Can't move from {0} to {1}".format(self.status, current_tag)))

    def set_initial_status(self, tag_name, allowed_tags):
        if (self._status != None):
            raise ValueError(_("Please call set_non_initial_status"))
        else:
            if tag_name in allowed_tags:
                self._status = self.status_type_enum()[tag_name].value
            else:
                raise ValueError(_('Invalid transaction.'))


PROJECT_CONFIG_CACHE = {}


class ProjectConfigurations(models.Model):
    key = models.CharField(_("Key"), max_length=55, primary_key=True)
    _value = models.TextField(_("Value"), null=True)
    type = models.CharField(max_length=2, choices=(('S', 'string'), ('I', 'int'), ('D', 'decimal'), ('C', 'csv')),
                            default='S')
    history = HistoricalRecords()

    def __str__(self):
        return "{} - {}".format(self.key, self._value)

    def save(self, **kwargs):
        self.key = self.key.lower()
        return super(ProjectConfigurations, self).save(**kwargs)

    def clean(self):
        if self.type == 'I':
            try:
                int(self._value)
            except ValueError:
                raise ValidationError({'_value': _(
                    "Value {} is not a valid Integer .".format(self._value))})
        if self.type == 'D':
            try:
                Decimal(self._value)
            except InvalidOperation:
                raise ValidationError({'_value': [_(
                    "Value {} is not a valid Decimal .".format(self._value))], })

    @property
    def value(self):
        if self.type == 'S':
            if self._value is None:
                return ""
            return self._value.strip()
        if self.type == 'I':
            return int(self._value)
        if self.type == 'D':
            return Decimal(self._value)
        if self.type == 'C':
            if self._value is None:
                return []
            return [x.strip() for x in self._value.split(",")]

    @staticmethod
    def get_value(key):
        if key.lower() in PROJECT_CONFIG_CACHE:
            return PROJECT_CONFIG_CACHE[key.lower()]

        val = ProjectConfigurations.objects.get(key=key.lower()).value
        PROJECT_CONFIG_CACHE[key.lower()] = val
        return val

    @staticmethod
    def set_value(key, value):
        if ProjectConfigurations.objects.filter(key=key.lower()).count() == 0:
            config_type = 'S'
            if type(value) is list:
                config_type = 'C'
                value = ','.join(val for val in value)
            elif type(value) is int:
                config_type = 'I'
            elif type(value) is float:
                config_type = 'D'

            ProjectConfigurations.objects.create(key=key.lower(), type=config_type, _value=value)

    @staticmethod
    def one_time_setup():
        if is_database_synchronized():
            for key, value in INITIAL_PROJECT_CONFIG_VALUES.items():
                ProjectConfigurations.set_value(key=key, value=value)


@receiver(signals.post_save, sender=ProjectConfigurations)
def update_project_config_cache(sender, instance, **kwargs):
    # delete key from cache
    if instance.key in PROJECT_CONFIG_CACHE:
        del PROJECT_CONFIG_CACHE[instance.key]
