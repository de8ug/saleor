import graphene
from django.core.exceptions import ValidationError
from django.template.defaultfilters import slugify

from ....product import models
from ...core.mutations import ModelDeleteMutation, ModelMutation


class AttributeCreateValueInput(graphene.InputObjectType):
    name = graphene.String(
        required=True, description='Name displayed in the interface.')
    value = graphene.String(
        required=True, description='Real value eg. HEX color.')


class AttributeCreateInput(graphene.InputObjectType):
    name = graphene.String(
        required=True, description='Name displayed in the interface.')
    values = graphene.List(
        AttributeCreateValueInput,
        description='Attribute values to be created for this attribute.')


class AttributeCreate(ModelMutation):
    class Arguments:
        input = AttributeCreateInput(
            required=True,
            description='Fields required to create an attribute.')

    class Meta:
        description = 'Creates an attribute.'
        model = models.Attribute

    @classmethod
    def user_is_allowed(cls, user, input):
        return user.has_perm('product.manage_products')

    @classmethod
    def clean_input(cls, info, instance, input, errors):
        cleaned_input = super().clean_input(info, instance, input, errors)
        cleaned_input['slug'] = slugify(cleaned_input['name'])

        values = cleaned_input.get('values', [])
        names = [value['name'] for value in values]
        if len(set(names)) != len(names):
            cls.add_error(
                errors, 'values', 'Duplicated attribute value names provided.')
        for value_data in values:
            value_data['slug'] = slugify(value_data['name'])
            attribute_value = models.AttributeValue(**value_data)
            try:
                attribute_value.full_clean()
            except ValidationError as validation_errors:
                for field in validation_errors.message_dict:
                    if field == 'attribute':
                        continue
                    for message in validation_errors.message_dict[field]:
                        error_field = 'values:%(field)s' % {'field': field}
                        cls.add_error(errors, error_field, message)
        return cleaned_input

    @classmethod
    def _save_m2m(cls, info, instance, cleaned_data):
        super()._save_m2m(info, instance, cleaned_data)
        values = cleaned_data.get('values', [])
        for value in values:
            instance.values.create(**value)


class AttributeUpdateInput(graphene.InputObjectType):
    slug = graphene.String(
        required=True, description='Internal name.')
    name = graphene.String(
        required=True, description='Name displayed in the interface.')
    remove_values = graphene.List(
        graphene.ID, name='removeValues',
        description='List of attributes to be removed from this attribute.')
    add_values = graphene.List(
        AttributeCreateValueInput, name='addValues',
        description='Attribute values to be created for this attribute.')


class AttributeUpdate(AttributeCreate):
    class Arguments:
        id = graphene.ID(
            required=True, description='ID of an attribute to update.')
        input = AttributeUpdateInput(
            required=True,
            description='Fields required to update an attribute.')

    class Meta:
        description = 'Updates attribute.'
        model = models.Attribute


class AttributeDelete(ModelDeleteMutation):
    class Arguments:
        id = graphene.ID(
            required=True, description='ID of an attribute to delete.')

    class Meta:
        description = 'Deletes an attribute.'
        model = models.Attribute

    @classmethod
    def user_is_allowed(cls, user, input):
        return user.has_perm('product.manage_products')


class AttributeValueCreateInput(graphene.InputObjectType):
    attribute = graphene.ID(
        required=False,
        description='Attribute to which value will be assigned.',
        name='attribute')
    name = graphene.String(
        required=True, description='Name displayed in the interface.')
    value = graphene.String(
        required=True, description='Real value eg. HEX color.')


class AttributeValueCreate(ModelMutation):
    class Arguments:
        input = AttributeValueCreateInput(
            required=True,
            description='Fields required to create an attribute choice value.')

    class Meta:
        description = 'Creates an attribute choice value.'
        model = models.AttributeValue

    @classmethod
    def user_is_allowed(cls, user, input):
        return user.has_perm('product.manage_products')

    @classmethod
    def clean_input(cls, info, instance, input, errors):
        cleaned_input = super().clean_input(info, instance, input, errors)
        cleaned_input['slug'] = slugify(cleaned_input['name'])
        return cleaned_input


class AttributeValueUpdateInput(graphene.InputObjectType):
    slug = graphene.String(
        required=True, description='Internal name.')
    name = graphene.String(
        required=True, description='Name displayed in the interface.')
    value = graphene.String(
        required=True, description='Real value eg. HEX color.')


class AttributeValueUpdate(AttributeValueCreate):
    class Arguments:
        id = graphene.ID(
            required=True,
            description='ID of an attribute choice value to update.')
        input = AttributeValueUpdateInput(
            required=True,
            description='Fields required to update an attribute choice value.')

    class Meta:
        description = 'Updates an attribute choice value.'
        model = models.AttributeValue


class AttributeValueDelete(ModelDeleteMutation):
    class Arguments:
        id = graphene.ID(
            required=True,
            description='ID of an attribute choice value to delete.')

    class Meta:
        description = 'Deletes an attribute choice value.'
        model = models.AttributeValue

    @classmethod
    def user_is_allowed(cls, user, input):
        return user.has_perm('product.manage_products')
