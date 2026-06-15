from rest_framework import serializers
from .models import Account

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = '__all__'
        read_only_fields = ['user']

    def validate(self, data):
        user = self.context['request'].user
        name = data.get('name')

        # En edit, excluir el mismo objeto
        instance = self.instance
        qs = Account.objects.filter(user=user, name__iexact=name)
        if instance:
            qs = qs.exclude(pk=instance.pk)


        if qs.exists():
            raise serializers.ValidationError({"name": "An account with this name already exists."})
    
        return data