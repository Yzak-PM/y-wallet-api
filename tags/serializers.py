from rest_framework import serializers
from .models import Tag

class TagSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Tag
        fields = '__all__'
        read_only_fields = ['user']

    def validate(self, data):
        user = self.context['request'].user
        name = data.get('name', '').strip()

        if not name:
            raise serializers.ValidationError({"name": "Name is required."})

        # Normaliza para guardar consistente
        data['name'] = name.capitalize()

        instance = self.instance
        qs = Tag.objects.filter(user=user, name__iexact=name)
        if instance:
            qs = qs.exclude(pk=instance.pk)

        if qs.exists():
            raise serializers.ValidationError({"name": "A tag with this name already exists."})

        return data