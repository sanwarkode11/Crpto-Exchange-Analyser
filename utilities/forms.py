from django import forms
from localflavor.in_.forms import INStateField, INZipCodeField, INStateSelect

from utilities.models import Address, BaseImageModel, compressImage

address_fields = ['address1', 'address2', 'city', 'state', 'pincode']


class BaseImageForm(forms.ModelForm):
    class Meta:
        model = BaseImageModel
        exclude = []

    def save(self, commit=True):
        instance = super(BaseImageForm, self).save(commit=False)

        if 'image_file' in self.changed_data:
            instance.image_file = compressImage(self.cleaned_data['image_file'])

        if commit:
            instance.save()
            self._save_m2m()

        return instance


class AddressForm(forms.ModelForm):
    address1 = forms.CharField(max_length=255, required=True)
    address2 = forms.CharField(max_length=255, required=False)
    city = forms.CharField(max_length=100, required=True)
    # district = forms.CharField(max_length=100, required=True)
    state = INStateField(required=True, widget=INStateSelect)
    pincode = INZipCodeField(required=True)

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super(AddressForm, self).__init__(*args, **kwargs)

        if self.instance.id:
            if self.instance.address:
                for f in address_fields:
                    self.fields[f].initial = getattr(self.instance.address, f)

    def save(self, commit=True):
        address_data = {}
        for f in address_fields:
            address_data[f] = self.cleaned_data.pop(f)

        instance = super(AddressForm, self).save(commit=False)
        if hasattr(instance, 'address') and instance.address != None:
            for attr, value in address_data.items():
                setattr(instance.address, attr, value)
            instance.address.save()
        else:
            address = Address(**address_data)
            address.save()
            instance.address = address

        if commit:
            instance.save()
            self._save_m2m()

        return instance
