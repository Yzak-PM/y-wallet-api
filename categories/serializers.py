from rest_framework import serializers
from .models import Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = ['user']

    def validate(self, data):
        user = self.context['request'].user
        title = data.get('title')

        # En edit, excluir el mismo objeto
        instance = self.instance
        qs = Category.objects.filter(user=user, title__iexact=title)
        if instance:
            qs = qs.exclude(pk=instance.pk)

        if qs.exists():
            raise serializers.ValidationError({"title": "A category with this name already exists."})
        
        return data