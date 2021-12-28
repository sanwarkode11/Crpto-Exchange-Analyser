from rest_framework import serializers

from utilities.models import Address
from utilities.storage_backends import BASE_MEDIA_URL


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['address1', 'address2', 'city', 'state', 'pincode']


class AbstractAddressSerializer(serializers.ModelSerializer):
    address = AddressSerializer(allow_null=True)

    def create(self, validated_data):
        address_data = validated_data.pop('address')
        model = self.Meta.model(**validated_data)

        if address_data:
            address = Address(**address_data)
            address.save()
            model.address = address
        model.save()

        return model

    def update(self, instance, validated_data):
        if validated_data.get('address'):
            if hasattr(instance, 'address'):
                has_changed = False
                for attr, value in validated_data.pop('address').items():
                    if getattr(instance.address, attr) != value:
                        has_changed = True
                        setattr(instance.address, attr, value)

                if has_changed:
                    instance.address.save()
            else:
                address = Address(**validated_data.pop('address'))
                address.save()
                instance.address = address

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class S3FileField(serializers.CharField):
    def run_validation(self, data=serializers.empty):
        # check if url is avalid media upload url
        if data and BASE_MEDIA_URL not in data:
            raise serializers.ValidationError('The url should begin with {}.'.format(BASE_MEDIA_URL))
        return super().run_validation(data)

    def to_internal_value(self, data):
        # remove the BASE URL before storing
        data = super().to_internal_value(data)
        return data.replace(BASE_MEDIA_URL, "")

    def to_representation(self, value):
        """
        Transform the *outgoing* native value into primitive data.
        """
        if value:
            return value.url
        else:
            return None
