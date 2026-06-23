from rest_framework import serializers
from .models import Transaction

class TransactionSerializer(serializers.ModelSerializer):
	class Meta:
		model = Transaction
		fields = '__all__'
		read_only_fields = ['user']

	def validate(self, data):
		user = self.context['request'].user

		account = data.get('account')
		amount = data.get('amount')
		destination_account = data.get('destination_account')
		category = data.get('category')
		tags = data.get('tags', [])
			
		if account.balance < amount:
			raise serializers.ValidationError(
				{"amount": "This account doesn't have enough balance."}
			)

		if account and account.user != user:
			raise serializers.ValidationError(
				{"account": "This account does not belong to the authenticated user."}
			)
		
		if account and account.nature == "liability" and data.get('type') in [Transaction.Type.INCOME, Transaction.Type.MOVEMENT]:
			raise serializers.ValidationError(
				{"type": "Income transactions are not allowed on liability accounts. Pay the debt from an asset account instead."}
			)
			
		if destination_account:
			data['type'] = Transaction.Type.MOVEMENT

			if not account:
				raise serializers.ValidationError(
					{"account": "An account is required for transfers."}
				)

			if account.nature != "asset":
				raise serializers.ValidationError(
					{"account": "Only asset accounts can be the source of a transfer."}
				)

			if destination_account.user != user:
				raise serializers.ValidationError(
					{"destination_account": "This destination account does not belong to the authenticated user."}
				)
			
			if destination_account == account:
				raise serializers.ValidationError(
					{"destination_account": "Destination account must be different from source account."}
				)
			
		if category and category.user != user:
			raise serializers.ValidationError(
				{"category": "This category does not belong to the authenticated user."}
			)
		
		for tag in tags:
			if tag.user != user:
				raise serializers.ValidationError(
					{"tags": f"Tag '{tag.name}' does not belong to the authenticated user."}
				)
				
		return super().validate(data)
	
class TagBriefSerializer(serializers.Serializer):
	id = serializers.IntegerField()
	name = serializers.CharField()
	color = serializers.CharField()
	icon = serializers.CharField()

class TransactionReadSerializer(serializers.ModelSerializer):
	account_name = serializers.CharField(source="account.name", read_only=True)
	account_color = serializers.CharField(source="account.color", read_only=True)
	destination_account_name = serializers.CharField(
		source="destination_account.name",
		read_only=True,
		allow_null=True,
		default=None
	)
	category_title = serializers.CharField(source="category.title", read_only=True)
	category_icon = serializers.CharField(source="category.icon", read_only=True)
	category_color = serializers.CharField(source="category.color", read_only=True)
	tags = TagBriefSerializer(many=True, read_only=True)

	class Meta:
		model = Transaction
		fields = [
			"id",
			"amount",
			"date",
			"description",
			"account",
			"account_name",
			"account_color",
			"destination_account",
			"destination_account_name",
			"category",
			"category_title",
			"category_icon",
			"category_color",
			"tags",
			"type"
		]