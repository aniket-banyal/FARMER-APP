from django.contrib.auth import password_validation
from rest_framework import serializers

from app.models import (Bookmark, CartItem, Delivery, Machine, Order,
                        RentOrder, Residue, ResidueOrder, User, CartResidueItem, Machine_models)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'name', 'email',
                  'phone', 'is_industry', 'location']
        extra_kwargs = {'password': {'write_only': True}}


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'name',
                  'phone', 'is_industry', 'location']


class MachineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Machine
        fields = ['id', 'owner', 'name', 'description', 'details', 'quantity', 'warranty', 'guarantee',
                  'loyalty', 'for_sale', 'for_rent', 'sell_price', 'rent_price', 'discount', 'image', 'debit', 'credit', 'upi', 'cash']
        read_only_fields = ['id', 'owner']


class Machine_modelsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Machine_models
        fields = ['id', 'admin', 'name', 'image1', 'image2']
        read_only_fields = ['id', 'admin']


class RentMachineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Machine
        fields = ['id', 'owner', 'name', 'description',
                  'rent_price', 'discount', 'image']
        read_only_fields = ['id', 'owner']


class DeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = Delivery
        fields = '__all__'


class BookmarkSerializer(serializers.ModelSerializer):

    class Meta:
        model = Bookmark
        fields = ['id', 'user', 'machine']
        read_only_fields = ['id', 'user']


class BookmarkDetailSerializer(serializers.ModelSerializer):
    machine = MachineSerializer()

    class Meta:
        model = Bookmark
        fields = ['id', 'user', 'machine']
        read_only_fields = ['id', 'user']


class ResidueCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Residue
        fields = ['id', 'owner', 'type_of_residue',
                  'price', 'description', 'quantity', 'image']
        read_only_fields = ['id', 'owner']


class ResidueSerializer(serializers.ModelSerializer):
    owner = UserSerializer()

    class Meta:
        model = Residue
        fields = ['id', 'owner', 'type_of_residue',
                  'price', 'description', 'quantity', 'image', ]


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'customer', 'machine', 'quantity', 'status',
                  'name_of_recipient', 'phone', 'state', 'city', 'pincode', 'address']
        read_only_fields = ['id', 'customer']


class OrderDetailSerializer(serializers.ModelSerializer):
    customer = UserSerializer()
    machine = MachineSerializer()

    class Meta:
        model = Order
        fields = ['id', 'customer', 'machine', 'quantity', 'status',
                  'name_of_recipient', 'phone', 'state', 'city', 'pincode', 'address']
        read_only_fields = ['id', 'customer']


class OrderCustomerSerializer(serializers.ModelSerializer):
    machine = MachineSerializer()

    class Meta:
        model = Order
        fields = ['id', 'machine', 'quantity', 'status', 'name_of_recipient',
                  'phone', 'state', 'city', 'pincode', 'address']


class RentOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = RentOrder
        fields = ['id', 'customer', 'machine', 'num_of_days', 'status']
        read_only_fields = ['id', 'customer']


class ResidueOrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResidueOrder
        fields = ['customer', 'residue', 'status', 'name_of_recipient',
                  'phone', 'state', 'city', 'pincode', 'address']
        read_only_fields = ['customer']


class ResidueOrderSerializer(serializers.ModelSerializer):
    residue = ResidueSerializer()
    customer = UserSerializer()

    class Meta:
        model = ResidueOrder
        fields = ['id', 'customer', 'residue', 'status', 'name_of_recipient',
                  'phone', 'state', 'city', 'pincode', 'address']


class CartItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['cart', 'machine', 'quantity']
        write_only_fields = ['cart']


class CartItemDetailSerializer(serializers.ModelSerializer):
    machine = MachineSerializer()

    class Meta:
        model = CartItem
        fields = ['id', 'machine', 'quantity']
        read_only_fields = ['id']


class CartItemUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['machine', 'quantity']
        read_only_fields = ['machine']


class CartRentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['cart', 'machine', 'num_of_days']
        write_only_fields = ['cart']


class CartRentDetailSerializer(serializers.ModelSerializer):
    machine = MachineSerializer()

    class Meta:
        model = CartItem
        fields = ['id', 'machine', 'num_of_days']
        read_only_fields = ['id']


class CartResidueCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartResidueItem
        fields = ['cart', 'residue', ]
        write_only_fields = ['cart']


class CartResidueDetailSerializer(serializers.ModelSerializer):
    residue = ResidueSerializer()

    class Meta:
        model = CartResidueItem
        fields = ['id', 'residue']
        read_only_fields = ['id']


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(
        max_length=128, write_only=True, required=True)
    new_password1 = serializers.CharField(
        max_length=128, write_only=True, required=True)
    new_password2 = serializers.CharField(
        max_length=128, write_only=True, required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        print(value)
        if not user.check_password(value):
            raise serializers.ValidationError(
                ('Your old password was entered incorrectly. Please enter it again.')
            )
        return value

    def validate(self, data):
        if data['new_password1'] != data['new_password2']:
            raise serializers.ValidationError(
                {'new_password2': ("The two password fields didn't match.")})
        password_validation.validate_password(
            data['new_password1'], self.context['request'].user)
        return data

    def save(self, **kwargs):
        password = self.validated_data['new_password1']
        user = self.context['request'].user
        user.set_password(password)
        user.save()
        return user
