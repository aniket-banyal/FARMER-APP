from app.serializers import (CartItemCreateSerializer,
                             CartItemDetailSerializer,
                             CartItemUpdateSerializer, CartRentCreateSerializer, CartRentDetailSerializer,
                             CartResidueDetailSerializer, CartResidueCreateSerializer,
                             #  ChangePasswordSerializer,
                             MachineSerializer, Machine_modelsSerializer,
                             OrderCustomerSerializer, OrderDetailSerializer,
                             OrderSerializer, RentMachineSerializer,
                             RentOrderSerializer, ResidueCreateSerializer,
                             ResidueOrderCreateSerializer,
                             ResidueOrderSerializer, ResidueSerializer,
                             #  UserSerializer, UserUpdateSerializer,
                             BookmarkSerializer, BookmarkDetailSerializer, ReportSerializer)
from app.models import (CartItem, Machine, Order, RentOrder, Residue,
                        ResidueOrder,
                        # User,
                        CartResidueItem, Machine_models, Bookmark)
from users.serializers import UserSerializer
from users.permissions import IsFarmer, IsIndustry
from users.models import User
from rest_framework.views import APIView
from rest_framework.serializers import ValidationError
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.generics import UpdateAPIView
from rest_framework import generics, status
from django_filters.rest_framework import DjangoFilterBackend
import datetime
from django.conf import settings
User = settings.AUTH_USER_MODEL

# class registerUser(APIView):
#     permission_classes = [AllowAny]

#     def post(self, request, format=None):
#         data = request.data
#         user = User.objects.create_user(
#             data["username"], data["email"], data["password"])
#         user.name = data["name"]
#         user.is_industry = data["is_industry"]
#         user.phone = data["phone"]
#         user.location = data["location"]
#         user.save()
#         serializer = UserSerializer(user)
#         return Response(serializer.data)


# class UsersView(generics.RetrieveAPIView):
#     def get_permissions(self):
#         method = self.request.method
#         if method == 'GET':
#             permission_classes = [AllowAny]
#         else:
#             permission_classes = [IsAuthenticated]
#         return [permission() for permission in permission_classes]

#     queryset = User.objects.all()
#     serializer_class = UserSerializer


# class ProfileView(generics.RetrieveUpdateDestroyAPIView):
#     permission_classes = [IsAuthenticated]
#     serializer_class = UserSerializer

#     def get_object(self):
#         return self.request.user

#     def update(self, request, *args, **kwargs):
#         partial = kwargs.pop('partial', False)
#         serializer = UserUpdateSerializer(
#             instance=request.user, data=request.data, partial=partial)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()

#         return Response(serializer.data, status=status.HTTP_200_OK)

#     def destroy(self, request, *args, **kwargs):
#         request.user.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


# class ChangePasswordView(UpdateAPIView):
#     permission_classes = [IsAuthenticated]
#     serializer_class = ChangePasswordSerializer

#     def update(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(status=status.HTTP_200_OK)


class Machine_modelsView(generics.ListCreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = Machine_modelsSerializer

    def get_serializer_class(self):
        method = self.request.method

        if method == 'GET':
            return Machine_modelsSerializer

        if method == 'POST':
            return Machine_modelsSerializer

    def get_queryset(self):

        return Machine_models.objects.all()

    def perform_create(self, serializer):

        serializer.save(admin=self.request.user)


class MachinesView(generics.ListCreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = MachineSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['for_rent', 'for_sale',
                        'owner__location', 'discount', 'name', 'old_machine', 'date']

    def get_serializer_class(self):
        method = self.request.method

        if method == 'GET':
            for_rent = self.request.query_params.get('for_rent')
            own = self.request.query_params.get('own')

            for_sale = self.request.query_params.get('for_sale')
            if not (for_sale and for_sale.lower() == 'true') and (for_rent and for_rent.lower() == 'true') or (own and own.lower() == 'true'):
                return RentMachineSerializer
            return MachineSerializer

        if method == 'POST':

            if self.request.user.role == 8:
                return MachineSerializer
            elif self.request.user.role == 7:
                return RentMachineSerializer

    def get_queryset(self):
        user = self.request.user

        if user.is_anonymous:
            return Machine.objects.filter(for_sale=True)

        if user.role == 8:
            return user.machine_set.all()

        own = self.request.query_params.get('own')
        if own:
            return Machine.objects.filter(owner=user)
        return Machine.objects.exclude(owner=user)
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['name', 'discount', 'old_machine', 'date']

    def perform_create(self, serializer):
        if self.request.user.role == 7 or self.request.user.role == 8:
            if self.request.user.role == 8:
                serializer.save(owner=self.request.user)
            else:
                serializer.save(owner=self.request.user,
                                for_sale=False, for_rent=True)


class Machine_modelsDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = Machine_modelsSerializer

    def get_serializer_class(self):
        if self.request.user.role == 7 or self.request.user.role == 8:
            return Machine_modelsSerializer

    def get_queryset(self):
        if self.request.user.role == 7 or self.request.user.role == 8:
            return Machine_models.objects.all()

    def update(self, request, *args, **kwargs):
        if self.request.user.role == 7 or self.request.user.role == 8:
            machine_model = self.get_object()
            if machine_model.admin != request.user:
                return Response(status=status.HTTP_403_FORBIDDEN)

            partial = kwargs.pop('partial', False)
            serializer = self.get_serializer(
                machine_model, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        if self.request.user.role == 7 or self.request.user.role == 8:
            machine_model = self.get_object()
            if machine_model.admin != request.user:
                return Response(status=status.HTTP_403_FORBIDDEN)

            machine_model.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class MachineDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MachineSerializer

    def get_serializer_class(self):
        if self.request.user.role == 7 or self.request.user.role == 8:
            user = self.request.user
            if user.role == 8:
                return MachineSerializer

            machine = self.get_object()
            method = self.request.method
            if method == 'GET':
                if machine.owner == user:
                    return RentMachineSerializer
                return MachineSerializer

            if machine.for_rent:
                return RentMachineSerializer
            return MachineSerializer

    def get_queryset(self):
        user = self.request.user
        if self.request.user.role == 7 or self.request.user.role == 8:
            if user.role == 8:
                return user.machine_set.all()
            return Machine.objects.all()

    def update(self, request, *args, **kwargs):
        if self.request.user.role == 7 or self.request.user.role == 8:
            machine = self.get_object()
            if machine.owner != request.user:
                return Response(status=status.HTTP_403_FORBIDDEN)

            partial = kwargs.pop('partial', False)
            serializer = self.get_serializer(
                machine, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        if self.request.user.role == 7 or self.request.user.role == 8:
            machine = self.get_object()
            if machine.owner != request.user:
                return Response(status=status.HTTP_403_FORBIDDEN)

            machine.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class OrdersView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.user.role == 7 or self.request.user.role == 8:
            method = self.request.method
            user = self.request.user

            if method == 'GET':
                if user.role == 8:
                    return OrderDetailSerializer
                return OrderCustomerSerializer

            return OrderSerializer

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'date']

    def get_queryset(self):
        if self.request.user.role == 7 or self.request.user.role == 8:
            user = self.request.user
            if user.role == 8:
                return Order.objects.filter(machine__owner=user)

            return Order.objects.filter(customer=user)

    def perform_create(self, serializer):
        if self.request.user.role == 7 or self.request.user.role == 8:
            machine = serializer.validated_data['machine']
            machine.quantity -= 1
            machine.save()

            serializer.save(customer=self.request.user)


class OrderDetailView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer
    queryset = Order.objects.all()

    def update(self, request, *args, **kwargs):
        if self.request.user.role == 7 or self.request.user.role == 8:
            machine = self.get_object().machine
            if machine.owner != request.user:
                return Response(status=status.HTTP_403_FORBIDDEN)

            try:
                data = {"status": request.data['status']}
            except KeyError:
                raise ValidationError()

            order = self.get_object()
            serializer = self.get_serializer(order, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data)


class RentOrdersView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RentOrderSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'date']

    def get_queryset(self):
        if self.request.user.role == 7 or self.request.user.role == 8:
            user = self.request.user
            own = self.request.query_params.get('own')
            if own and own.lower() == 'true':
                return RentOrder.objects.filter(machine__owner=user)
            return RentOrder.objects.filter(customer=user)

    def perform_create(self, serializer):
        if self.request.user.role == 7 or self.request.user.role == 8:
            machine = serializer.validated_data['machine']
            machine.quantity -= 1
            machine.save()

            serializer.save(customer=self.request.user)


class RentOrderDetailView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RentOrderSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'date']

    def get_queryset(self):
        if self.request.user.role == 7 or self.request.user.role == 8:
            return RentOrder.objects.filter(machine__owner=self.request.user)

    def update(self, request, *args, **kwargs):
        if self.request.user.role == 7 or self.request.user.role == 8:
            rent_order = self.get_object()
            if rent_order.machine.owner != request.user:
                return Response(status=status.HTTP_403_FORBIDDEN)

            try:
                data = {"status": request.data['status']}
            except KeyError:
                raise ValidationError()

            serializer = self.get_serializer(
                rent_order, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data)


class ResiduesView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.user.role == 7 or self.request.user.role == 8:
            permission_classes = [IsAuthenticated]
            method = self.request.method

            if method == 'POST':
                permission_classes.append(IsFarmer)
            return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.request.user.role == 7 or self.request.user.role == 8:
            method = self.request.method
            if method == 'GET':
                return ResidueSerializer
            return ResidueCreateSerializer

    def get_queryset(self):
        if self.request.user.role == 7 or self.request.user.role == 8:
            user = self.request.user
            sold_residues = [order.residue.id for order in ResidueOrder.objects.all(
            ) if order.status == ResidueOrder.ACCEPTED]
            residues = Residue.objects.exclude(pk__in=sold_residues)

            if user.role == 8:
                return residues
            return residues.filter(owner=user)

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['type_of_residue']

    def perform_create(self, serializer):
        if self.request.user.role == 7 or self.request.user.role == 8:
            serializer.save(owner=self.request.user)


class ResidueTypeView(APIView):

    def get(self, request):
        if self.request.user.role == 7 or self.request.user.role == 8:
            types = [type[1] for type in Residue.CHOICES]
            return Response(types)


class ResidueDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Residue.objects.all()

    def get_serializer_class(self):
        if self.request.user.role == 7 or self.request.user.role == 8:
            method = self.request.method
            if method == 'GET':
                return ResidueSerializer
            return ResidueCreateSerializer

    def update(self, request, *args, **kwargs):
        if self.request.user.role == 7 or self.request.user.role == 8:
            residue = self.get_object()
            if residue.owner != request.user:
                return Response(status=status.HTTP_403_FORBIDDEN)

            partial = kwargs.pop('partial', False)
            serializer = self.get_serializer(
                residue, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

    def delete(self, request, **kwargs):
        if self.request.user.role == 7 or self.request.user.role == 8:
            residue = self.get_object()
            if residue.owner != request.user:
                return Response(status=status.HTTP_403_FORBIDDEN)

            residue.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class ResidueOrdersView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.user.role == 7 or self.request.user.role == 8:
            method = self.request.method
            if method == 'POST':
                return ResidueOrderCreateSerializer
            return ResidueOrderSerializer

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status']

    def get_queryset(self):
        if self.request.user.role == 7 or self.request.user.role == 8:
            user = self.request.user
            if user.role == 8:
                return ResidueOrder.objects.filter(customer=user)
            return ResidueOrder.objects.filter(residue__owner=user)

    def perform_create(self, serializer):
        if self.request.user.role == 7 or self.request.user.role == 8:
            serializer.save(customer=self.request.user)


class ResidueOrderDetailView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ResidueOrderCreateSerializer
    queryset = ResidueOrder.objects.all()

    # def get_queryset(self):
    #     user = self.request.user
    #     return ResidueOrder.objects.filter(residue__owner=user)

    def update(self, request, *args, **kwargs):
        if self.request.user.role == 7 or self.request.user.role == 8:
            residue = self.get_object().residue
            if residue.owner != request.user:
                return Response(status=status.HTTP_403_FORBIDDEN)

            try:
                data = {"status": request.data['status']}
            except KeyError:
                raise ValidationError()
            residue_order = self.get_object()
            serializer = self.get_serializer(
                residue_order, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


class CartView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.user.role == 7 or self.request.user.role == 8:
            user = self.request.user
            if user.role == 8:
                return CartResidueDetailSerializer
            rent = self.request.query_params.get('rent')
            if rent and rent.lower() == 'true':
                return CartRentDetailSerializer
            return CartItemDetailSerializer

    def get_queryset(self):
        if self.request.user.role == 7 or self.request.user.role == 8:
            user = self.request.user
            if user.role == 8:
                return CartResidueItem.objects.filter(cart__user=user)
            rent = self.request.query_params.get('rent')
            if rent and rent.lower() == 'true':
                return CartItem.objects.filter(cart__user=user, rent=True)
            return CartItem.objects.filter(cart__user=user, rent=False)

    def post(self, request, *args, **kwargs):
        if self.request.user.role == 7 or self.request.user.role == 8:
            cart = self.request.user
            items = request.data['items']

            user = self.request.user
            rent = self.request.query_params.get('rent', False)
            rent = rent and rent.lower() == 'true'
            if user.role == 8:
                for item in items:
                    existing_item = CartResidueItem.objects.filter(
                        residue__id=item['residue'])
                    if len(existing_item) > 0:
                        continue

                    item['cart'] = cart.id
                    serializer = CartResidueCreateSerializer(data=item)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()

            elif rent:
                for item in items:
                    existing_item = CartItem.objects.filter(
                        machine__id=item['machine'], rent=True)
                    if len(existing_item) > 0:
                        existing_item[0].num_of_days += item['num_of_days']
                        existing_item[0].save()
                        continue

                    item['cart'] = cart.id
                    serializer = CartRentCreateSerializer(data=item)
                    serializer.is_valid(raise_exception=True)
                    serializer.save(rent=True)
            else:
                for item in items:
                    existing_item = CartItem.objects.filter(
                        machine__id=item['machine'], rent=False)
                    if len(existing_item) > 0:
                        existing_item[0].quantity += item['quantity']
                        existing_item[0].save()
                        continue

                    item['cart'] = cart.id
                    serializer = CartItemCreateSerializer(data=item)

                    serializer.is_valid(raise_exception=True)
                    serializer.save(rent=False)

            return Response(status=status.HTTP_201_CREATED)


class CartItemView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CartItemDetailSerializer

    def get_queryset(self):
        if self.request.user.role == 7 or self.request.user.role == 8:
            user = self.request.user

            if user.role == 8:
                return CartResidueItem.objects.filter(cart__user=user)

            else:
                return CartItem.objects.filter(cart__user=user)

    def put(self, request, *args, **kwargs):
        if self.request.user.role == 7 or self.request.user.role == 8:
            item = self.get_object()
            cart = item.cart
            if cart != self.request.user:
                return Response(status=status.HTTP_403_FORBIDDEN)

            try:
                quantity = int(request.data["quantity"])
                if quantity < 1:
                    raise ValidationError()
            except (KeyError, TypeError, ValueError, ValidationError):
                return Response({'quantity': ['quantity should be a positive integer']}, status=status.HTTP_400_BAD_REQUEST)

            serializer = CartItemUpdateSerializer(
                instance=item, data={'quantity': quantity})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)


class CartCheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if self.request.user.role == 7 or self.request.user.role == 8:
            print(request.data)
            user = self.request.user
            cart = request.user.cart
            if user.role == 8:
                for item in cart.get_residueitems():
                    ResidueOrder.objects.create(customer=request.user, residue=item.residue,
                                                phone=request.data['phone'], pincode=request.data['pincode'])
                    item.delete()
            rent = self.request.query_params.get('rent')
            if rent and rent.lower() == 'true':
                for item in cart.get_rentitems():

                    RentOrder.objects.create(
                        customer=request.user, machine=item.machine, num_of_days=item.num_of_days)
                    item.delete()

            else:
                for item in cart.get_items():

                    Order.objects.create(customer=request.user, machine=item.machine, quantity=item.quantity,
                                         phone=request.data['phone'], pincode=request.data['pincode'])
                    item.delete()

            return Response(status=status.HTTP_200_OK)


class BookmarkView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BookmarkSerializer

    def get_serializer_class(self):
        if self.request.user.role == 7 or self.request.user.role == 8:
            method = self.request.method
            if method == 'GET':
                return BookmarkDetailSerializer
            return BookmarkSerializer

    def get_queryset(self):
        if self.request.user.role == 7 or self.request.user.role == 8:
            return Bookmark.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        if self.request.user.role == 7 or self.request.user.role == 8:

            serializer.save(user=self.request.user)


class BookmarkDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BookmarkSerializer
    queryset = Bookmark.objects.all()

    def delete(self, request, **kwargs):
        if self.request.user.role == 7 or self.request.user.role == 8:
            bookmark = self.get_object()
            if bookmark.user != request.user:
                return Response(status=status.HTTP_403_FORBIDDEN)

            bookmark.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class Connections(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if self.request.user.role == 7 or self.request.user.role == 8:
            user = request.user
            connections = user.get_connections()
            serializer = UserSerializer(connections, many=True)
            return Response(serializer.data)


class Reports(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        if self.request.user.role == 7 or self.request.user.role == 8:
            list = []
            report = request.GET.get('report', False)
            machine = request.GET.get('machine', False)
            order = request.GET.get('order', False)
            rent = request.GET.get('rent', False)
            start = request.GET.get('start', None)
            end = request.GET.get('end', None)

            start = datetime.datetime.strptime(
                start, '%Y-%m-%d').strftime('%Y-%m-%d')
            end = datetime.datetime.strptime(
                end, '%Y-%m-%d').strftime('%Y-%m-%d')
            user = self.request.user
            if user.role == 8:
                if report:
                    if order:
                        list1 = Order.objects.filter(
                            machine__owner=self.request.user,
                            date__range=[start, end]).order_by('-pk')
                        data = [
                            {"Report": 'machine ordered', "count": len(list1)}]
                        results = ReportSerializer(data, many=True).data

                    elif rent:
                        list1 = RentOrder.objects.filter(
                            machine__owner=self.request.user,
                            date__range=[start, end]).order_by('-pk')
                        data = [
                            {"Report": 'machine rented', "count": len(list1)}]
                        results = ReportSerializer(data, many=True).data

                    elif machine:
                        list1 = Machine.objects.filter(
                            owner=self.request.user,
                            date__range=[start, end]).order_by('-pk')
                        data = [
                            {"Report": 'machine created', "count": len(list1)}]
                        results = ReportSerializer(data, many=True).data

                    return Response(results)
                else:
                    if order:
                        list = Order.objects.filter(
                            machine__owner=self.request.user,
                            date__range=[start, end]).order_by('-pk')

                        serializer = OrderSerializer(
                            list, many=True, context={'request': request})
                    elif rent:
                        list = RentOrder.objects.filter(
                            machine__owner=self.request.user,
                            date__range=[start, end]).order_by('-pk')

                        serializer = RentOrderSerializer(
                            list, many=True, context={'request': request})
                    elif machine:
                        list = Machine.objects.filter(
                            owner=self.request.user,
                            date__range=[start, end]).order_by('-pk')

                        serializer = MachineSerializer(
                            list, many=True, context={'request': request})

                    return Response(serializer.data)
