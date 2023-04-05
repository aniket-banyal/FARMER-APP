from email.message import EmailMessage
from rest_framework_temporary_tokens.models import TemporaryToken
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core import mail
from django.shortcuts import render
from django.http import JsonResponse, Http404, HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.forms.models import model_to_dict
from django.contrib.auth.models import User

from agriculture2.settings import EMAIL_HOST_USER
from .models import *
from .serializers import *
from rest_framework import viewsets, filters
from .paginators import *
from django_filters.rest_framework import DjangoFilterBackend
from datetime import timedelta
from agriculture2.settings import MEDIA_ROOT, DOMAIN
import os
import http.client
import uuid
import datetime
from datetime import timedelta
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.storage import FileSystemStorage
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from time import sleep
from openpyxl import Workbook
from openpyxl import load_workbook
from openpyxl.utils import get_column_letter
from os import path
import requests
import csv
import pandas as pd
import shutil
from django.db import IntegrityError
from django.core.exceptions import ValidationError

# logger = logging.getLogger(__name__)
Types = ['FARMER', 'ADO', 'BLOCK_ADMIN', 'DDA',
         'STATE_ADMIN', 'SUPER_ADMIN', 'farmer_ecom']

# Helper function to send email


def send_email(subject, content, recipient_list, path=None):
    email_from = EMAIL_HOST_USER
    mail = EmailMessage(subject, content, email_from, recipient_list)
    mail.content_subtype = 'html'
    if path:
        mail.attach_file(path)
    mail.send()


class CheckVersion(APIView):
    permission_classes = []

    def get(self, request, format=None):
        version = AppVersion.objects.latest('version')
        serializer = AppVersionSerializer(version)
        return Response(serializer.data)


class RadiusList(APIView):
    permission_classes = []

    def post(self, request, format=None):
        value = request.data['radius']
        state = request.data['state']
        state_obj = State.objects.get(state=state.upper())
        obj = Radius.objects.create(value=value, state=state_obj)
        obj.save()
        return Response({
            "Radius": obj.value,
            "State": obj.state.state
        })


class RadiusDetail(APIView):
    permission_classes = []

    def get_object(self, state):
        try:
            return State.objects.get(state=state.upper())
        except State.DoesNotExist:
            raise Http404

    def get(self, request, state, format=None):
        state = self.get_object(state)
        obj = Radius.objects.get(state=state)
        return Response({
            "Radius": obj.value,
            "State": obj.state.state
        })

    def put(self, request, state, format=None):
        state = self.get_object(state)
        value = request.data['radius']
        obj = Radius.objects.get(state=state)
        obj.value = value
        obj.save()
        return Response({
            "Radius": obj.value,
            "State": obj.state.state
        })


# class user_create(APIView):

#     def post(self, request, format='json'):
#         serializer = UserSerializer(data=request.data)
#         if serializer.is_valid():
#             user = serializer.save()
#             if user:
#                 token = Token.objects.create(user=user)
#                 json = serializer.data
#                 json['token'] = token.key
#                 return Response(json, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class user_login(APIView):

#     def post(self, request, format='json'):
#         data = request.data
#         user = authenticate(
#             request, username=data['username'], password=data['password'])
#         if user:
#             token = Token.objects.get(user=user)
#             json = {'token': token.key}
#             return Response(json, status=status.HTTP_200_OK)
#         return Response({'error': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)
# state_Admin will be added at the same time?
# class state(APIView):

#     def post(self, request):
#         serializer = state_serializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StateList(APIView):
    # permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        states = State.objects.all().order_by('-pk')
        serializer = StateSerializer(states, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        # state_obj = State.objects.get(pk=state_id)
        serializer = StateSerializer(data=request.data)
        if serializer.is_valid():
            # serializer.validated_data['state'] = state_obj
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StateDetail(APIView):
    def get_object(self, pk):
        try:
            return State.objects.get(pk=pk)
        except State.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        state = self.get_object(pk)
        serializer = StateSerializer(state)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        state = self.get_object(pk)
        serializer = StateSerializer(state, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        state = self.get_object(pk)
        state.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


'''#dda will be addded wiht this?
class district(APIView):

    def post(self, request, state_id):
        state_obj = State.objects.get(pk=state_id)
        serializer = district_serializer(data=request.data)
        if serializer.is_valid():
            serializer.validated_data['state'] = state_obj
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
'''


class DistrictList(APIView):

    def get(self, request, format=None):
        districts = District.objects.filter(
            state=request.user.state).order_by('-pk')
        serializer = DistrictSerializer(districts, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        # state_obj = State.objects.get(pk=state_id)
        serializer = AddDistrictSerializer(data=request.data)
        if serializer.is_valid():
            # serializer.validated_data['state'] = state_obj
            dic = {}
            serializer.save()
            dic.update(serializer.data)
            if request.data.get('has_blocks', None) == False:
                district_created = District.objects.get(
                    id=serializer.data['id'])
                try:
                    b = Block.objects.create(
                        district=district_created, block=serializer.data['district'], block_code=serializer.data['district_code'])
                    dic['block'] = b.id
                except:
                    dic['block'] = None
                    return Response(serializer.data, status=status.HTTP_201_CREATED)

            return Response(dic, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DistrictDetail(APIView):
    def get_object(self, pk):
        try:
            return District.objects.get(pk=pk)
        except District.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        district = self.get_object(pk)
        serializer = DistrictSerializer(district)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        district = self.get_object(pk)
        serializer = AddDistrictSerializer(
            district, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        district = self.get_object(pk)
        district.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DistrictViewSet(viewsets.ReadOnlyModelViewSet):
    model = District
    serializer_class = DistrictSerializer
    pagination_class = StandardResultsSetPagination
    # Making endpoint searchable
    filter_backends = (filters.SearchFilter, DjangoFilterBackend, )
    search_fields = ('district', 'district_code',)
    filterset_fields = ['district', 'has_blocks']

    def get_queryset(self):
        # districts = District.objects.filter(state=self.request.user.state).order_by('-pk')
        """change order alphabatically """
        districts = District.objects.filter(
            state=self.request.user.state).order_by('district')
        return districts


'''
class block(APIView):

    def post(self, request, district_id):
        district_obj = District.objects.get(pk=district_id)
        serializer = block_serializer(data=request.data)
        if serializer.is_valid():
            serializer.validated_data['district'] = district_obj
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
ado?????????????
class village(APIView):

    def post(self, request, block_id):
        block_obj = Block.objects.get(pk=block_id)
        serializer = village_serializer(data=request.data)
        if serializer.is_valid():
            serializer.validated_data['block'] = block_obj
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        '''


class BlockList(APIView):

    def get(self, request, format=None):
        blocks = Block.objects.filter(
            district__state=request.user.state).order_by('pk')
        serializer = BlockSerializer(blocks, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):

        district_id = request.data.get("district")
        district = District.objects.get(id=district_id)
        serializer = AddBlockSerializer(data=request.data)
        if district.has_blocks:
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"Error": "Provided District has has_blocks field set to False"}, status=status.HTTP_400_BAD_REQUEST)


class BlockDetail(APIView):
    def get_object(self, pk):
        try:
            return Block.objects.get(pk=pk)
        except Block.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        block = self.get_object(pk)
        serializer = BlockSerializer(block)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        block = self.get_object(pk)
        serializer = AddBlockSerializer(block, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        block = self.get_object(pk)
        block.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BlocksDistrictWiseViewSet(viewsets.ReadOnlyModelViewSet):
    model = Block
    serializer_class = BlockSerializer
    # permission_classes = ( )
    pagination_class = StandardResultsSetPagination
    # Making endpoint searchable
    filter_backends = (filters.SearchFilter, )
    search_fields = ('block', 'id', 'block_code',)

    def get_queryset(self):
        try:
            district = District.objects.get(id=self.kwargs['pk'])
        except District.DoesNotExist:
            raise Http404
        blocks = Block.objects.filter(district=district).order_by('block')
        return blocks


class VillageList(APIView):

    def get(self, request, format=None):
        villages = Village.objects.filter(
            block__district__state=request.user.state).order_by('village')
        serializer = VillageSerializer(villages, many=True)

        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = AddVillageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VillageDetail(APIView):
    def get_object(self, pk):
        try:
            return Village.objects.get(pk=pk)
        except Village.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        village = self.get_object(pk)
        serializer = VillageSerializerSpecific(village)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        village = self.get_object(pk)
        serializer = AddVillageSerializer(
            village, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        village = self.get_object(pk)
        village.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class VillageViewSet(viewsets.ReadOnlyModelViewSet):
    model = Village
    serializer_class = VillageSerializer
    pagination_class = StandardResultsSetPagination
    # Making endpoint searchable
    filter_backends = (filters.SearchFilter, DjangoFilterBackend, )
    search_fields = ('village', 'village_code', 'block__district__district')
    filterset_fields = ['block__district__district', 'ado', 'village']

    def get_queryset(self):
        villages = Village.objects.filter(
            block__district__state=self.request.user.state).order_by('-pk')
        return villages


class VillagesDistrictWiseViewSet(viewsets.ReadOnlyModelViewSet):
    model = Village
    serializer_class = VillageSerializer
    # permission_classes = ( )
    pagination_class = StandardResultsSetPagination
    # Making endpoint searchable
    filter_backends = (filters.SearchFilter, )
    search_fields = ('village',)

    def get_queryset(self):
        try:
            district = District.objects.get(id=self.kwargs['pk'])
        except District.DoesNotExist:
            raise Http404
        villages = Village.objects.filter(
            block__district=district).order_by('village')
        return villages


'''
class user_profile(APIView):

    def get(self, request):
        if request.user.role == 1:
            farmer_set = farmer.objects.get(user=request.user)
            serializer = farmer_serializer(farmer_set)
            if serializer.data is not None:
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return JsonResponse({"ALERT": "Profile is not yet created"}, status=status.HTTP_400_BAD_REQUEST)

        elif request.user.role == 2:
            ado_set = ado.objects.get(user=request.user)
            serializer = ado_serializer(ado_set)
            if serializer.data is not None:
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return JsonResponse({"ALERT": "Profile is not yet created"}, status=status.HTTP_400_BAD_REQUEST)

        elif request.user.role == 3:
            block_admin_set = block_admin.objects.get(user=request.user)
            serializer = block_admin_serializer(block_admin_set)
            if serializer.data is not None:
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return JsonResponse({"ALERT": "Profile is not yet created"}, status=status.HTTP_400_BAD_REQUEST)

        elif request.user.role == 4:
            dda_set = dda.objects.get(user=request.user)
            serializer = dda_serializer(dda_set)
            if serializer.data is not None:
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return JsonResponse({"ALERT": "Profile is not yet created"}, status=status.HTTP_400_BAD_REQUEST)

        elif request.user.role == 5:
            state_admin_set = state_admin.objects.get(user=request.user)
            serializer = state_admin_serializer(state_admin_set)
            if serializer.data is not None:
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return JsonResponse({"ALERT": "Profile is not yet created"}, status=status.HTTP_400_BAD_REQUEST)

        elif request.user.role == 6:
            return JsonResponse({"ERROR": "super admin does not have a profile"})
        
      
    def post(self, request):
        serializer = 0

        if request.user.role == 1:
            serializer = farmer_serializer(data=request.data)

        # //could cause error
        elif request.user.role == 2:
            serializer = ado_serializer(data=request.data)

        elif request.user.role == 3:
            serializer = block_admin_serializer(data=request.data)


        # //could cause error
        elif request.user.role == 4:
            serializer = dda_serializer(data=request.data)

        elif request.user.role == 5:
            serializer = state_admin_serializer(data=request.data)

        elif request.user.role == 6:
            return JsonResponse({"ERROR": "super admin does not have a profile"})
        
       
        
        
        if serializer.is_valid():
            serializer.validated_data['user'] = request.user
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
'''


class GetUser(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        # request.user= User.objects.get(username="i")

        data = []
        serializer = []
        if request.user.role == 1:
            data = farmer.objects.get(user=request.user)
            serializer = FarmerSerializer(data)

        elif request.user.role == 2:
            data = ado.objects.get(user=request.user)
            serializer = AdoSerializer(data)

        elif request.user.role == 3:
            data = block_admin.objects.get(user=request.user)
            serializer = BlockAdminSerializer(data)

        elif request.user.role == 4:
            data = dda.objects.get(user=request.user)
            serializer = DdaSerializer(data)

        elif request.user.role == 5:
            data = state_admin.objects.get(user=request.user)
            serializer = StateAdminSerializer(data)

        elif request.user.role == 6:
            data = super_admin.objects.get(user=request.user)
            serializer = SuperAdminSerializer(data)

        elif request.user.role == 7:
            data = farmer_ecom.objects.get(user=request.user)
            serializer = farmer_ecomSerializer(data)

        elif request.user.role == 8:
            data = industry_ecom.objects.get(user=request.user)
            serializer = industry_ecomSerializer(data)

        return Response(serializer.data)


class DDAList(APIView):
    # permission_classes = []
    def get(self, request, format=None):
        ddas = dda.objects.filter(
            district__state=request.user.state).order_by('user__name')
        serializer = DdaSerializer(ddas, many=True)
        return Response(serializer.data)


class UserList(APIView):
    permission_classes = []

    def get(self, request, format=None):
        users = User.objects.all().order_by('-pk')
        serializer = UserSerializer(
            users, many=True, context={"request": request})
        return Response(serializer.data)

    def post(self, request, format=None):

        data = request.data.copy()
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        phone = data.get('phone_number')
        role = int(data.get('role', 1))
        name = data.get('name')
        image = data.get('image', None)
        state = data.get('state', None)
        s = None
        # if state is none
        if state != '' and state != None:
            s = State.objects.get(state=state.upper())

        try:
            user_obj = User.objects.create(
                username=username, role=role, email=email, name=name, state=s, phone_number=phone)
            if image != None:
                user_obj.image = image
        except IntegrityError as e:
            raise ValidationError(str(e))
        user_obj.set_password(password)
        user_obj.save()
        data['user'] = user_obj.pk

        del data['role']
        del data['username']
        del data['password']
        del data['name']
        if request.data.get('state', None) != None:
            del data['state']
        if image != None:
            del data['image']
        del data['phone_number']

        if role == 1:
            serializer = AddFarmerSerializer(data=data)

        elif role == 2:
            serializer = AddAdoSerializer(data=data)

        elif role == 3:
            serializer = AddBlock_adminSerializer(data=data)

        elif role == 4:
            serializer = AddDdaSerializer(data=data)

        elif role == 5:
            serializer = Addstate_admin_serializer(data=data)

        elif role == 6:
            serializer = AddSuperadminSerializer(data=data)

        elif role == 7:
            serializer = AddFarmer_ecomSerializer(data=data)

        elif role == 8:
            serializer = AddIndustry_ecomSerializer(data=data)

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data)
        user_obj.delete()
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetail(APIView):

    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        user = self.get_object(pk)
        data = []
        serializer = []
        if user.role == 1:
            data = farmer.objects.get(user=user)
            serializer = FarmerSerializer(data)

        elif user.role == 2:
            data = ado.objects.get(user=user)
            serializer = AdoSerializer(data)

        elif user.role == 3:
            data = block_admin.objects.get(user=user)
            serializer = BlockAdminSerializer(data)

        elif user.role == 4:
            data = dda.objects.get(user=user)
            serializer = DdaSerializer(data)

        elif user.role == 5:
            data = state_admin.objects.get(user=user)
            serializer = StateAdminSerializer(data)

        elif user.role == 6:
            data = super_admin.objects.get(user=user)
            serializer = SuperadminSerializer(data)

        elif user.role == 7:
            data = farmer_ecom.objects.get(user=user)
            serializer = UserSerializer(data)

        elif user.role == 8:
            data = industry_ecom.objects.get(user=user)
            serializer = UserSerializer(data)

        return Response(serializer.data)

    def put(self, request, pk, format=None):

        user = self.get_object(pk)
        data = []
        serializer = []
        basic_data = dict()
        output_data = dict()

        for x in ['name', 'age', 'phone_number', 'address', 'image']:
            if request.data.get(x, None) != None:
                basic_data[x] = request.data[x]
                del request.data[x]

        user_serializer_data = UserSerializer(user, basic_data, partial=True)
        if user_serializer_data.is_valid():
            user_serializer_data.save()

        if user.role == 1:
            data = farmer.objects.get(user=user)
            serializer = AddFarmerSerializer(data, request.data, partial=True)

        elif user.role == 2:
            data = ado.objects.get(user=user)
            serializer = AddAdoSerializer(data, request.data, partial=True)

        elif user.role == 3:
            data = block_admin.objects.get(user=user)
            serializer = AddBlock_adminSerializer(
                data, request.data, partial=True)

        elif user.role == 4:
            data = dda.objects.get(user=user)
            serializer = AddDdaSerializer(data, request.data, partial=True)

        elif user.role == 5:
            data = state_admin.objects.get(user=user)
            serializer = Addstate_admin_serializer(
                data, request.data, partial=True)

        elif user.role == 6:
            data = super_admin.objects.get(user=user)
            serializer = AddSuperadminSerializer(
                data, request.data, partial=True)

        elif user.role == 7:
            data = farmer_ecom.objects.get(user=user)
            serializer = farmer_ecomSerializer(
                data, request.data, partial=True)

        elif user.role == 8:
            data = industry_ecomSerializer.objects.get(user=user)
            serializer = industry_ecomSerializer(
                data, request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            output_data.update(serializer.data)
            output_data['user'] = user_serializer_data.data
            return Response(output_data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        user = self.get_object(pk)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DdaViewSet(viewsets.ReadOnlyModelViewSet):
    model = dda
    serializer_class = DdaSerializer
    # permission_classes = []
    pagination_class = StandardResultsSetPagination
    # Making endpoint searchable
    filter_backends = (filters.SearchFilter, )
    search_fields = ('district__district')

    def get_queryset(self):
        ddas = dda.objects.filter(
            district__state=self.request.user.state).order_by('-pk')
        return ddas
# Shows list of ado for specific dda logged in


class AdoViewSet(viewsets.ReadOnlyModelViewSet):
    model = ado
    serializer_class = AdoSerializer
    # permission_classes = (IsAuthenticated, )
    # permission_classes = []
    pagination_class = StandardResultsSetPagination
    # Making endpoint searchable
    filter_backends = (filters.SearchFilter, DjangoFilterBackend, )
    filterset_fields = ['village_ado__block__district__district', 'user__name']
    search_fields = ('village_ado__block__district__district', 'village_ado__village',
                     'user__phone_number', 'user__username', 'user__email', 'user__name',)

    def get_queryset(self):
        try:
            Dda = dda.objects.get(user=self.request.user)

        except dda.DoesNotExist:
            raise Http404
        ados = ado.objects.filter(village_ado__block__district=Dda.district).order_by(
            'user__name').distinct()

        return ados
# problem wiht ordering according to district


class AdosViewSet(viewsets.ReadOnlyModelViewSet):
    model = ado
    serializer_class = AdoSerializer
    # permission_classes = (IsAuthenticated, )
    # permission_classes = []
    pagination_class = StandardResultsSetPagination
    # Making endpoint searchable
    filter_backends = (filters.SearchFilter, DjangoFilterBackend, )
    filterset_fields = ['district__district', ]
    search_fields = ('district__district', 'user__phone_number',
                     'user__username', 'user__email', 'user__name',)

    def get_queryset(self):
        # ados = ado.objects.filter(village_ado__block__district__state=self.request.user.state).order_by('village_ado__block__district__district','user__name').distinct()
        ados = ado.objects.filter(user__state=self.request.user.state).order_by(
            'village_ado__block__district__district', 'user__name').distinct()
        return ados


class Adoddalist(viewsets.ReadOnlyModelViewSet):
    model = ado
    serializer_class = AdoSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        try:
            ddas = dda.objects.get(id=self.kwargs['pk'])
        except dda.DoesNotExist:
            raise Http404
        District = ddas.district
        ados = ado.objects.filter(district=District).order_by(
            'village_ado__block__district__district', 'user__name').distinct()
        return ados


class AdminViewSet(viewsets.ReadOnlyModelViewSet):
    model = super_admin
    serializer_class = SuperAdminSerializer
    # permission_classes = (IsAuthenticated, )
    pagination_class = StandardResultsSetPagination
    # Making endpoint searchable
    # filter_backends = (filters.SearchFilter, )
    # search_fields = ('centre__location', 'course__title', 'first_name', 'last_name', '=contact_number', 'user__email')

    def get_queryset(self):
        admins = state_admin.objects.all().order_by('-pk')
        return admins


class DCList(APIView):
    permission_classes = []

    def get(self, request, format=None):
        dcs = DC.objects.all().order_by('name')
        serializer = DCSerializer(dcs, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = DCSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DCDetail(APIView):
    def get_object(self, pk):
        try:
            return DC.objects.get(pk=pk)
        except DC.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        dc = self.get_object(pk)
        serializer = DCSerializer(dc)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        dc = self.get_object(pk)
        serializer = DCSerializer(dc, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        dc = self.get_object(pk)
        dc.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
# SP VIEWS


class SPList(APIView):
    permission_classes = []

    def get(self, request, format=None):
        sps = SP.objects.all().order_by('name')
        serializer = SPSerializer(sps, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = SPSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# SP VIEWS


class SPDetail(APIView):
    def get_object(self, pk):
        try:
            return SP.objects.get(pk=pk)
        except SP.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        sp = self.get_object(pk)
        serializer = SPSerializer(sp)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        sp = self.get_object(pk)
        serializer = SPSerializer(sp, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        sp = self.get_object(pk)
        sp.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class LocationViewSet(viewsets.ReadOnlyModelViewSet):
    model = location
    serializer_class = LocationSerializer
    permission_classes = [IsAuthenticated]
    # permission_classes= []
    pagination_class = StandardResultsSetPagination
    # Making endpoint searchable

    filter_backends = (filters.SearchFilter, DjangoFilterBackend,)
    filterset_fields = ['dda', 'ado', 'status',
                        'district__district', 'village_name__village', 'acq_date']
    # search_fields = ('state', 'block_name', 'village_name', 'dda__name', 'ado__name', 'status', 'district',)
    search_fields = ('district__state__state', 'village_name__block__block', 'village_name__village',
                     'ado__user__username', 'status', 'district__district', 'ado__user__name',)

    def get_queryset(self):
        stat = self.kwargs['status']
        state_admin_obj = state_admin.objects.get(user=self.request.user)

        if stat == 'unassigned':
            locations = location.objects.filter(status='pending', ado=None, district__state=state_admin_obj.state).order_by(
                '-acq_date', 'district__district', 'village_name__block__block', 'village_name__village')
        elif stat == 'assigned':
            locations = location.objects.filter(status='pending', district__state=state_admin_obj.state).exclude(
                ado=None).order_by('-acq_date', 'district__district', 'village_name__block__block', 'village_name__village')
        else:
            locations = location.objects.filter(status=stat, district__state=state_admin_obj.state).order_by(
                '-acq_date', 'district__district', 'village_name__block__block', 'village_name__village')

        return locations


class LocationViewSetAdo(viewsets.ReadOnlyModelViewSet):
    model = location
    serializer_class = LocationSerializer
    # permission_classes = (IsAuthenticated, )
    # permission_classes=[]
    pagination_class = StandardResultsSetPagination
    # Making endpoint searchable
    filter_backends = (filters.SearchFilter, DjangoFilterBackend, )
    filterset_fields = ['village_name__village']
    # search_fields = ('state', 'block_name', 'village_name', 'ado__name', 'status', 'district',)
    search_fields = ('district__state__state', 'village_name__block__block',
                     'village_name__village', 'ado__user__username', 'status', 'district__district',)

    def get_queryset(self):
        try:
            user = ado.objects.get(user=self.request.user)
            # user = ado.objects.get(id=1)
        except ado.DoesNotExist:
            raise Http404
        stat = self.kwargs['status']
        locations = []
        if stat == 'pending':
            locations = location.objects.filter(status=stat, ado=user).order_by(
                '-acq_date', 'district__district', 'village_name__block__block', 'village_name__village')
        elif stat == 'completed':
            locations = location.objects.filter(status__in=['completed', 'ongoing'], ado=user).order_by(
                '-acq_date', 'district__district', 'village_name__block__block', 'village_name__village')
        return locations


class LocationViewSetDda(viewsets.ReadOnlyModelViewSet):
    model = location
    serializer_class = LocationSerializer
    # permission_classes = (IsAuthenticated, )
    # permission_classes=[]
    pagination_class = StandardResultsSetPagination
    # Making endpoint searchable
    filter_backends = (filters.SearchFilter, DjangoFilterBackend, )
    filterset_fields = ['ado', 'status', 'village_name__village', ]
    search_fields = ('district__state__state', 'village_name__block__block', 'village_name__village',
                     'ado__user__username', 'ado__user__name', 'status', 'district__district',)

    def get_queryset(self):

        try:
            user = dda.objects.get(user=self.request.user.pk)
            # user = dda.objects.get(id=1)
            print(user)
        except dda.DoesNotExist:
            raise Http404
        stat = self.kwargs['status']
        locations = []
        if stat == 'unassigned':
            locations = location.objects.filter(status='pending', dda=user, ado=None).order_by(
                '-acq_date', 'district__district', 'village_name__block__block', 'village_name__village')
        elif stat == 'assigned':
            locations = location.objects.filter(status='pending', dda=user).exclude(ado=None).order_by(
                '-acq_date', 'district__district', 'village_name__block__block', 'village_name__village')
        else:
            locations = location.objects.filter(status=stat, dda=user).order_by(
                '-acq_date', 'district__district', 'village_name__block__block', 'village_name__village')
        return locations


class LocationViewSetAdoForAdmin(viewsets.ReadOnlyModelViewSet):
    model = location
    serializer_class = LocationSerializer
    # permission_classes = (IsAuthenticated, )
    # permission_classes=[]
    pagination_class = StandardResultsSetPagination
    # Making endpoint searchable
    filter_backends = (filters.SearchFilter, DjangoFilterBackend, )
    filterset_fields = ['dda', 'ado', 'status', 'district__district',
                        'village_name__village', 'district__state__state']
    # search_fields = ('state', 'block_name', 'village_name', 'ado__name', 'status', 'district',)
    search_fields = ('district__state__state', 'village_name__block__block', 'village_name__village',
                     'ado__user__username', 'ado__user__name', 'status', 'district__district',)

    def get_queryset(self):
        try:
            user = ado.objects.get(id=self.kwargs['pk'])
        except ado.DoesNotExist:
            raise Http404
        stat = self.kwargs['status']
        locations = []
        if stat == 'pending':
            locations = location.objects.filter(district__state=self.request.user.state, status=stat, ado=user).order_by(
                '-acq_date', 'district__district', 'village_name__block__block', 'village_name__village')  # ('-acq_date', 'district', 'block_name', 'village_name')
        elif stat == 'completed':
            locations = location.objects.filter(district__state=self. request.user.state, status__in=['completed', 'ongoing'], ado=user).order_by(
                '-acq_date', 'district__district', 'village_name__block__block', 'village_name__village')
        return locations


class LocationViewSetDdaForAdmin(viewsets.ReadOnlyModelViewSet):
    model = location
    serializer_class = LocationSerializer
    # permission_classes = (IsAuthenticated, )
    # permission_classes = ()
    pagination_class = StandardResultsSetPagination
    # Making endpoint searchable
    filter_backends = (filters.SearchFilter, DjangoFilterBackend, )
    filterset_fields = ['dda', 'ado', 'status', 'district__district']
    # search_fields = ('state', 'block_name', 'village_name', 'ado__name', 'status', 'district',)
    search_fields = ('district__state__state', 'village_name__block__block', 'village_name__village',
                     'ado__user__name', 'ado__user__username', 'status', 'district__district',)

    def get_queryset(self):
        try:
            user = dda.objects.get(id=self.kwargs['pk'])
        except dda.DoesNotExist:
            raise Http404
        stat = self.kwargs['status']
        locations = []
        if stat == 'unassigned':
            locations = location.objects.filter(district__state=self.request.user.state, status='pending', dda=user, ado=None).order_by(
                '-acq_date', 'district__district', 'village_name__block__block', 'village_name__village')
        elif stat == 'assigned':
            locations = location.objects.filter(district__state=self.request.user.state, status='pending', dda=user).exclude(
                ado=None).order_by('-acq_date', 'district__district', 'village_name__block__block', 'village_name__village')
        elif stat == 'ongoing':
            locations = location.objects.filter(district__state=self.request.user.state, status=stat, dda=user).order_by(
                '-acq_date', 'district__district', 'village_name__block__block', 'village_name__village')
        elif stat == 'completed':
            locations = location.objects.filter(district__state=self.request.user.state, status=stat, dda=user).order_by(
                '-acq_date', 'district__district', 'village_name__block__block', 'village_name__village')

        return locations


class LocationDistrictWiseViewSet(viewsets.ReadOnlyModelViewSet):
    model = location
    serializer_class = LocationSerializer
    # permission_classes = ( )
    pagination_class = StandardResultsSetPagination
    # Making endpoint searchable
    filter_backends = (filters.SearchFilter, )
    # search_fields = ('state', 'block_name', 'village_name', 'ado__name', 'status', 'district',)
    search_fields = ('district__state__state', 'village_name__block__block', 'village_name__village',
                     'ado__user__name', 'ado__user__username', 'status', 'district__district',)

    def get_queryset(self):
        try:
            district = District.objects.get(id=self.kwargs['pk'])
        except District.DoesNotExist:
            raise Http404
        stat = self.kwargs['status']
        locations = []
        if stat == 'unassigned':
            locations = location.objects.filter(status='pending', ado=None, district=district).order_by(
                '-acq_date', 'district__district', 'village_name__block__block', 'village_name__village')
        elif stat == 'assigned':
            locations = location.objects.filter(status='pending', district=district).exclude(ado=None).order_by(
                '-acq_date', 'district__district', 'village_name__block__block', 'village_name__village')
        elif stat == 'ongoing':
            locations = location.objects.filter(status=stat, district=district).order_by(
                '-acq_date', 'district__district', 'village_name__block__block', 'village_name__village')
        elif stat == 'completed':
            locations = location.objects.filter(status=stat, district=district).order_by(
                '-acq_date', 'district__district', 'village_name__block__block', 'village_name__village')
        return locations


class LocationList(APIView):

    def get(self, request, format=None):
        locations = []
        start = request.GET.get('start', None)
        end = request.GET.get('end', None)
        district = request.GET.get('district', None)
        status = request.GET.get('status', None)
        dda = request.GET.get('dda', None)
        if dda:
            if start and end:
                start = datetime.datetime.strptime(
                    start, '%Y-%m-%d').strftime('%Y-%m-%d')
                end = datetime.datetime.strptime(
                    end, '%Y-%m-%d').strftime('%Y-%m-%d')
                if district:
                    if status:
                        locations = location.objects.filter(district__state=request.user.state, district__district=district.upper(
                        ), status=status, acq_date__range=[start, end], dda__pk=int(dda)).order_by('-pk')
                    else:
                        locations = location.objects.filter(district__state=request.user.state, district__district=district.upper(
                        ), acq_date__range=[start, end], dda__pk=int(dda)).order_by('-pk')
                else:
                    if status:
                        locations = location.objects.filter(district__state=request.user.state, status=status, acq_date__range=[
                                                            start, end], dda__pk=int(dda)).order_by('-pk')
                    else:
                        locations = location.objects.filter(district__state=request.user.state, acq_date__range=[
                                                            start, end], dda__pk=int(dda)).order_by('-pk')
            else:
                if district:
                    if status:
                        locations = location.objects.filter(district__state=request.user.state, district__district=district.upper(
                        ), status=status, dda__pk=int(dda)).order_by('-pk')
                    else:
                        locations = location.objects.filter(
                            district__state=request.user.state, district__district=district.upper(), dda__pk=int(dda)).order_by('-pk')
                else:
                    if status:
                        locations = location.objects.filter(
                            district__state=request.user.state, status=status, dda__pk=int(dda)).order_by('-pk')
                    else:
                        locations = location.objects.filter(
                            district__state=request.user.state, dda__pk=int(dda)).order_by('-pk')
        else:
            if start and end:
                start = datetime.datetime.strptime(
                    start, '%Y-%m-%d').strftime('%Y-%m-%d')
                end = datetime.datetime.strptime(
                    end, '%Y-%m-%d').strftime('%Y-%m-%d')
                if district:
                    if status:
                        locations = location.objects.filter(district__state=request.user.state, district__district=district.upper(
                        ), status=status, acq_date__range=[start, end]).order_by('-pk')
                    else:
                        locations = location.objects.filter(district__state=request.user.state, district__district=district.upper(
                        ), acq_date__range=[start, end]).order_by('-pk')
                else:
                    if status:
                        locations = location.objects.filter(
                            district__state=request.user.state, status=status, acq_date__range=[start, end]).order_by('-pk')
                    else:
                        locations = location.objects.filter(
                            district__state=request.user.state, acq_date__range=[start, end]).order_by('-pk')
            else:
                if district:
                    if status:
                        locations = location.objects.filter(
                            district__state=request.user.state, district__district=district.upper(), status=status).order_by('-pk')
                    else:
                        locations = location.objects.filter(
                            district__state=request.user.state, district__district=district.upper()).order_by('-pk')
                else:
                    if status:
                        locations = location.objects.filter(
                            district__state=request.user.state, status=status).order_by('-pk')
                    else:
                        locations = location.objects.filter(
                            district__state=request.user.state).order_by('-pk')

        serializer = LocationSerializer(
            locations, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request, format=None):

        directory = MEDIA_ROOT + '/locationCSVs/'
        if not os.path.exists(directory):
            os.makedirs(directory)

        locations = []
        count = 0
        if 'location_csv' in request.data:
            if not request.data['location_csv'].name.endswith('.csv'):
                return Response({'location_csv': ['Please upload a valid document ending with .csv']},
                                status=status.HTTP_400_BAD_REQUEST)
            fs = FileSystemStorage()
            fs.save(
                directory + request.data['location_csv'].name, request.data['location_csv'])

            csvFile = open(
                directory + request.data['location_csv'].name, 'r', encoding="utf8")

            for line in csvFile.readlines():
                locations.append(line)

            try:
                data_format = locations[0].split(',')
                if ((data_format[0].strip().upper() != 'STATE') or
                    (data_format[1].strip().upper() != 'DISTRICT') or
                    (data_format[2].strip().upper() != 'BLOCK NAME') or
                    (data_format[3].strip().upper() != 'VILLAGE NAME') or
                    (data_format[4].strip().upper() != 'LONGITUDE') or
                    (data_format[5].strip().upper() != 'LATITUDE') or
                    (data_format[6].strip().upper() != 'ACQ_DATE') or
                        (data_format[7].strip().upper() != 'ACQ_TIME')):

                    return Response({'location_csv': ['Incorrect file format \n VALID FORMAT: \n State,District,Block Name,Village Name,Longitude,Latitude,Acq_Date,Acq_Time']},
                                    status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({'location_csv': ['Incorrect file format \n VALID FORMAT: \n State,District,Block Name,Village Name,Longitude,Latitude,Acq_Date,Acq_Time']},
                                status=status.HTTP_400_BAD_REQUEST)

            locations.pop(0)
            MAILING_LIST = {}
            directory = MEDIA_ROOT + '/mailing/'
            if not os.path.exists(directory):
                os.makedirs(directory)
            for data in locations:

                request.data.clear()
                print(data)
                index = locations.index(data)
                data = data.split(',')
                dis = District.objects.filter(
                    state__state=data[0].upper(), district=data[1].upper())
                request.data['district'] = dis[0].pk

                vil = Village.objects.filter(
                    village=data[3].upper(), block__district__district=data[1].upper())
                if(len(vil) == 1):
                    request.data['village_name'] = vil[0].pk

                request.data['longitude'] = data[4]
                request.data['latitude'] = data[5]
                print(data[6])
                try:
                    request.data['acq_date'] = datetime.datetime.strptime(
                        data[6], '%Y-%m-%d').strftime('%Y-%m-%d')
                except:
                    try:
                        request.data['acq_date'] = datetime.datetime.strptime(
                            data[6], '%d/%m/%Y').strftime('%Y-%m-%d')
                    except:
                        return Response({'location_csv': ['Incorrect date format \n VALID FORMAT: \n %m/%d/%Y ']},
                                        status=status.HTTP_400_BAD_REQUEST)

                request.data['acq_time'] = data[7].split('.')[0]
                Dda = []
                Dda = dda.objects.filter(
                    district__district=data[1].rstrip().upper())
                if(len(Dda) == 1):
                    request.data['dda'] = Dda[0].pk
                else:
                    request.data['dda'] = None

                Ado = []
                # , dda__district__district=data[1].rstrip().upper())
                Ado = ado.objects.filter(
                    village_ado__village=data[3].rstrip().upper())
                if len(Ado) == 1:
                    request.data['ado'] = Ado[0].pk
                else:
                    request.data['ado'] = None

                serializer = AddLocationSerializer(data=request.data)
                print(request.data)
                if serializer.is_valid():
                    print(serializer.data)
                    serializer.save()
                    count = count + 1
            return Response({'status': 'success', 'count': count}, status=status.HTTP_201_CREATED)
        return Response({'error': 'invalid'}, status=status.HTTP_400_BAD_REQUEST)


class LocationDetail(APIView):
    # permission_classes = []
    def get_object(self, pk):
        try:
            return location.objects.get(pk=pk)
        except location.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        location = self.get_object(pk)
        serializer = LocationSerializer(location)
        return Response(serializer.data)

    def post(self, request, pk, format=None):
        location = self.get_object(pk)
        serializer = AddLocationSerializer(
            location, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        location = self.get_object(pk)
        location.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ImagesView(APIView):

    def get(self, request, format=None):
        images = Image.objects.all().order_by('-pk')
        serializer = ImageSerializer(
            images, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = AddImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReportImageView(APIView):
    def get_object(self, pk):
        try:
            return AdoReport.objects.get(pk=pk)
        except AdoReport.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        report = self.get_object(pk)
        images = Image.objects.filter(report=report)
        serializer = ImageSerializer(
            images, many=True, context={'request': request})
        return Response(serializer.data)


class BulkAddVillage(APIView):

    def post(self, request, format=None):
        directory = MEDIA_ROOT + '/villageCSV/'
        if not os.path.exists(directory):
            os.makedirs(directory)

        villages = []
        count = 0
        if 'village_csv' in request.data:
            if not request.data['village_csv'].name.endswith('.csv'):
                return Response({'village_csv': ['Please upload a valid document ending with .csv']},
                                status=status.HTTP_400_BAD_REQUEST)
            fs = FileSystemStorage()
            fs.save(
                directory + request.data['village_csv'].name, request.data['village_csv'])
            csvFile = open(directory + request.data['village_csv'].name, 'r')
            for line in csvFile.readlines():
                villages.append(line)

            villages.pop(0)

            for data in villages:
                data = data.split(',')
                village = []
                village = data[0].split('(')
                request.data['village'] = village[0].strip()
                if len(village) > 1:
                    request.data['village_subcode'] = village[1].split(')')[
                        0].strip()
                else:
                    request.data['village_subcode'] = ''
                request.data['village_code'] = data[1].strip()
                block = Block.objects.filter(
                    district__district_code=data[2].rstrip())
                if len(block) == 1:
                    request.data['block'] = block[0].pk

                    serializer = AddVillageSerializer(data=request.data)
                    if serializer.is_valid():
                        serializer.save()
                        count = count + 1
            return Response({'status': 'success', 'count': count}, status=status.HTTP_201_CREATED)
        return Response({'error': 'invalid'}, status=status.HTTP_400_BAD_REQUEST)


class BulkAddDistrict(APIView):

    def post(self, request, format=None):
        directory = MEDIA_ROOT + '/districtCSV/'
        if not os.path.exists(directory):
            os.makedirs(directory)

        districts = []
        count = 0
        if 'district_csv' in request.data:
            if not request.data['district_csv'].name.endswith('.csv'):
                return Response({'district_csv': ['Please upload a valid document ending with .csv']},
                                status=status.HTTP_400_BAD_REQUEST)
            fs = FileSystemStorage()
            fs.save(
                directory + request.data['district_csv'].name, request.data['district_csv'])
            csvFile = open(directory + request.data['district_csv'].name, 'r')
            for line in csvFile.readlines():
                districts.append(line)

            districts.pop(0)

            for data in districts:
                data = data.split(',')
                request.data['district'] = data[1].strip().upper()
                request.data['district_code'] = data[2].strip()
                if int(data[3].strip()) == 0:
                    request.data['has_blocks'] = False
                else:
                    request.data['has_blocks'] = True

                state = State.objects.filter(state_code=data[0].strip())

                if len(state) == 1:
                    request.data['state'] = state[0].id
                    serializer = AddDistrictSerializer(data=request.data)

                    if serializer.is_valid():
                        serializer.save()
                        # if no blocks are available then we will create one here
                        if request.data['has_blocks'] == False:
                            Block.objects.create(block=data[1].strip().upper(
                            ), block_code=data[2].strip(), district_id=serializer.data['id'])
                        count = count + 1
            return Response({'status': 'success', 'count': count}, status=status.HTTP_201_CREATED)
        return Response({'error': 'invalid'}, status=status.HTTP_400_BAD_REQUEST)


class BulkAddDda(APIView):

    def post(self, request, format=None):
        directory = MEDIA_ROOT + '/ddaCSVs/'
        if not os.path.exists(directory):
            os.makedirs(directory)

        ddas = []
        count = 0
        if 'dda_csv' in request.data:
            if not request.data['dda_csv'].name.endswith('.csv'):
                return Response({'dda_csv': ['Please upload a valid document ending with .csv']},
                                status=status.HTTP_400_BAD_REQUEST)
            fs = FileSystemStorage()
            fs.save(
                directory + request.data['dda_csv'].name, request.data['dda_csv'])
            csvFile = open(directory + request.data['dda_csv'].name, 'r')
            for line in csvFile.readlines():
                ddas.append(line)

            ddas.pop(0)
            # Create a unique filename
            filename = 'filename.csv'
            csvFile = open(directory + filename, 'w')
            csvFile.write('Name,Username,Password\n')
            for data in ddas:

                data = data.split(',')
                # request.data['name']  = data[0]
                # request.data['number'] = data[1]
                # request.data['email'] = data[2]
                district = None
                try:
                    district = District.objects.get(
                        state__state_code=data[0], district=data[1].upper().strip())
                except District.DoesNotExist:
                    pass

                if district != None:
                    request.data['district'] = district.id

                existing = [user['username']
                            for user in User.objects.values('username')]
                username = data[2].strip()
                if username in existing:
                    # Provide random username if username
                    # of the form Ado<pk> already exists
                    username = uuid.uuid4().hex[:8]
                    while username in existing:
                        username = uuid.uuid4().hex[:8]

                # Create user of type student
                state = State.objects.get(state_code=data[0])
                user = User.objects.create(username=username, role=4, phone_number=data[3].strip(
                ), email=data[4].strip(), name=data[2].strip(), state=state)

                password = uuid.uuid4().hex[:8].lower()
                user.set_password(password)
                user.save()
                request.data['user'] = user.pk
                serializer = AddDdaSerializer(data=request.data)
                if serializer.is_valid():
                    serializer.save()

                    csvFile.write(data[2] + ',' + username +
                                  ',' + password + '\n')
                    count = count + 1
                else:
                    print(serializer.errors)
            csvFile.close()
            absolute_path = DOMAIN + 'media/ddaCSVs/' + filename
            return Response({'status': 'success', 'count': count, 'csvFile': absolute_path}, status=status.HTTP_201_CREATED)
        return Response({'error': 'invalid'}, status=status.HTTP_400_BAD_REQUEST)


class BulkAddAdo(APIView):
    def post(self, request, format=None):
        directory = MEDIA_ROOT + '/adoCSVs/'
        if not os.path.exists(directory):
            os.makedirs(directory)

        ados = []
        count = 0
        if 'ado_csv' in request.data:
            if not request.data['ado_csv'].name.endswith('.csv'):
                return Response({'ado_csv': ['Please upload a valid document ending with .csv']},
                                status=status.HTTP_400_BAD_REQUEST)
            fs = FileSystemStorage()
            fs.save(
                directory + request.data['ado_csv'].name, request.data['ado_csv'])
            csvFile = open(directory + request.data['ado_csv'].name, 'r')
            for line in csvFile.readlines():
                ados.append(line)

            ados.pop(0)
            # Create a unique filename
            filename = 'filename.csv'
            csvFile = open(directory + filename, 'w')
            csvFile.write('Name,Username,Password\n')
            for data in ados:
                data = data.split(',')
                district_name = data[0].split('(')[1].split(')')[0]
                user_state = None

                user_state = District.objects.get(district=district_name).state

                # request.data['name']  = data[0]
                # request.data['number'] = data[2]
                # request.data['email'] = data[3]
                # dda = None
                # try:
                #     dda = Dda.objects.get(district__district_code=data[4].rstrip())
                # except Dda.DoesNotExist:
                #     pass
                # if dda != None:
                #     request.data['dda'] = dda.id
                existing = [user['username']
                            for user in User.objects.values('username')]
                username = data[0].split('(')[0].rstrip()
                if(len(username) < 1):
                    username = uuid.uuid4().hex[:8]
                if username in existing:
                    # Provide random username if username
                    # of the form Ado<pk> already exists
                    username = uuid.uuid4().hex[:8]
                    while username in existing:
                        username = uuid.uuid4().hex[:8]

                # Create user of type ado
                # user = User.objects.create(username=username, type_of_user="ado")

                user = User.objects.create(
                    username=username, role=2, phone_number=data[2], email=data[3], name=data[0].split('(')[0], state=user_state)
                password = uuid.uuid4().hex[:8].lower()
                user.set_password(password)
                user.save()
                request.data['user'] = user.pk
                serializer = AddAdoSerializer(data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    # print(serializer.data)
                    try:
                        aado = ado.objects.get(id=serializer.data['id'])
                    except ado.DoesNotExist:
                        aado = None
                    if aado:
                        arr = []
                        villages = []
                        villages = data[1].split('|')
                        for village in villages:
                            obj = []

                            if len(village.split('(')) > 1:
                                obj = Village.objects.filter(village_subcode=village.split('(')[1].split(')')[
                                                             0].upper().strip(), block__district__district=district_name.strip())
                            if len(obj) != 1:
                                obj = Village.objects.filter(village=village.split(
                                    '(')[0].upper().strip(), block__district__district=district_name.strip())
                            if(len(obj) == 1):
                                # arr.append(int(obj[0].id))
                                print(obj[0].village)
                                obj[0].ado = aado
                                obj[0].save()
                        # ado.village.set(arr)
                        # ado.save()
                    csvFile.write(data[0].split(
                        '(')[0] + ',' + username + ',' + password + '\n')
                    count = count + 1
                else:
                    print(serializer.errors)
            csvFile.close()
            absolute_path = DOMAIN + 'media/adoCSVs/' + filename
            return Response({'status': 'success', 'count': count, 'csvFile': absolute_path}, status=status.HTTP_201_CREATED)
        return Response({'error': 'invalid'}, status=status.HTTP_400_BAD_REQUEST)


class GetListAdo(APIView):

    def get(self, request, format=None):
        directory = MEDIA_ROOT + '/list/'
        if not os.path.exists(directory):
            os.makedirs(directory)
        filename = 'list.csv'
        csvFile = open(directory + filename, 'w')
        csvFile.write('Username,Name,Email,Number, DDA, Villages\n')
        ados = ado.objects.all().order_by(
            'village_ado__block__district__district', 'user__name').distinct('id')
        # print(ados)
        # village= village.objects.all()
        for a in ados:
            villages = Village.objects.filter(ado=a.pk)
            username = a.user.username
            name = a.user.name
            email = a.user.email
            number = a.user.phone_number
            dda_name = ''
            district = ''
            d = ''
            if len(villages) > 0:
                dda = villages[0].block.district.dda_district
                if dda:
                    dda_name = dda.user.name
                    district = dda.district.district
                    d = dda_name + '(' + district + ')'

                # if ado.dda.district:
                #     district = ado.dda.district.district
            villa = []

            # objects = ado.village.all()
            for village in villages:
                villa.append(village.village)
            villa = '|'.join(villa)
            csvFile.write(username + ','+name + ',' + email +
                          ',' + number + ',' + d + ',' + villa + '\n')
        csvFile.close()
        absolute_path = DOMAIN + 'media/list/' + filename
        return Response({'status': 200, 'csvFile': absolute_path})


class GeneratePasswordsForAdo(APIView):

    def get(self, request, format=None):
        directory = MEDIA_ROOT + '/password/'
        if not os.path.exists(directory):
            os.makedirs(directory)
        filename = 'password.csv'
        csvFile = open(directory + filename, 'w')
        csvFile.write('District,Username,Name,Number,Password\n')
        ados = ado.objects.all()
        for a in ados:
            user = a.user
            password = uuid.uuid4().hex[:8].lower()
            user.set_password(password)
            user.save()
            district = ''
            village = Village.objects.filter(ado=a)

            if len(village) > 0:
                district = village[0].block.district.district
                # district = ado.dda.district.district
            csvFile.write(district + ','+a.user.username + ',' +
                          a.user.name+','+a.user.phone_number + ',' + password + '\n')
        csvFile.close()
        absolute_path = DOMAIN + 'media/password/' + filename
        return Response({'status': 200, 'csvFile': absolute_path})


class GenerateLocationReport(APIView):
    def get(self, request, format=None):

        directory = MEDIA_ROOT + '/status_report/'
        if not os.path.exists(directory):
            os.makedirs(directory)

        # get params district and range
        try:
            start = datetime.datetime.strptime(request.GET.get(
                'start'), '%Y-%m-%d').strftime('%Y-%m-%d')
        except Exception as e:
            return Response({'error': 'start date not in right format %Y-%m-%d'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            end = datetime.datetime.strptime(request.GET.get(
                'end'), '%Y-%m-%d').strftime('%Y-%m-%d')
        except Exception as e:
            return Response({'error': 'end date not in right format %Y-%m-%d'}, status=status.HTTP_400_BAD_REQUEST)

        district_raw = request.GET.get('district', None)
        location_status_raw = request.GET.get('status', None)
        village_raw = request.GET.get('village', None)
        ado_raw = request.GET.get('Ado', None)

        district = None
        if district_raw:
            d = District.objects.filter(district=district_raw.upper())
            if(len(d) == 1):
                district = d[0]

        village = None
        if village_raw:
            v = Village.objects.filter(village=village_raw.upper())
            if(len(v) == 1):
                village = v[0]

        Ado = None
        if ado_raw:
            aa = ado.objects.filter(user__username=ado_raw)
            if(len(aa) == 1):
                Ado = aa[0]

        location_status = None
        if location_status_raw:
            location_status = location_status_raw.lower()

        locations = []
        if district:
            # district = District.objects.get(district=district_raw.upper())
            if location_status and village:
                # village= Village.objects.get(village_name=village_raw.upper())
                locations = location.objects.filter(
                    created_on__range=[start, end],
                    district=district,
                    status=location_status,
                    village_name=village
                )
                filename = 'location_report_' + location_status + '_' + \
                    district.district + '_' + village.village + '.csv'
            elif location_status and Ado:
                locations = location.objects.filter(
                    created_on__range=[start, end],
                    status=location_status,
                    district=district,
                    ado=Ado,
                )
                filename = 'location_report_' + location_status + '_' + district.district + \
                    '_' + Ado.user.username+'('+Ado.user.name+')' + '.csv'
            elif location_status:
                locations = location.objects.filter(
                    created_on__range=[start, end],
                    district=district,
                    status=location_status
                )
                filename = 'location_report_' + location_status + '_' + district.district + '.csv'
            elif village:
                locations = location.objects.filter(
                    created_on__range=[start, end],
                    district=district,
                    village_name=village,
                )
                filename = 'location_report_' + district.district + '_' + village.village + '.csv'
            elif Ado:
                locations = location.objects.filter(
                    created_on__range=[start, end],
                    district=district,
                    ado=Ado,
                )
                filename = 'location_report_' + district.district + \
                    '_' + Ado.user.username+'('+Ado.user.name+')' + '.csv'
            else:
                locations = location.objects.filter(
                    created_on__range=[start, end],
                    district=district,
                )
                filename = 'location_report_' + district.district + '.csv'
        elif location_status and village:
            locations = location.objects.filter(
                created_on__range=[start, end],
                status=location_status,
                village_name=village,
            )
            filename = 'location_report_' + location_status + '_' + village.village + '.csv'
        elif location_status and Ado:
            locations = location.objects.filter(
                created_on__range=[start, end],
                status=location_status,
                ado=Ado,
            )
            filename = 'location_report_' + location_status + '_' + \
                Ado.user.username+'('+Ado.user.name+')' + '.csv'
        elif location_status:
            locations = location.objects.filter(
                created_on__range=[start, end],
                status=location_status
            )
            filename = 'location_report_' + location_status + '.csv'
        else:
            locations = location.objects.filter(
                created_on__range=[start, end],
            )
            filename = 'location_report_all.csv'
        if len(locations) == 0:
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            csvFile = open(directory + filename, 'w')
            csvFile.write(
                'Sno, District, Block, Village, Longitude, Latitude, Acquired Date, Dda Details, Ado Details\n')
            sno = 0
            for loc in locations:
                sno += 1
                dis = ''
                if loc.district:
                    dis = str(loc.district.district)

                block = ''
                if loc.village_name and loc.village_name.block and loc.village_name.block.block:
                    block = str(loc.village_name.block.block)

                village = ''
                if loc.village_name and loc.village_name.village:
                    village = str(loc.village_name.village)

                longitude = ''
                if loc.longitude:
                    longitude = str(loc.longitude)

                latitude = ''
                if loc.latitude:
                    latitude = str(loc.latitude)

                acq_date = ''
                if loc.acq_date:
                    acq_date = str(loc.acq_date)

                dda = ''
                if loc.dda:
                    dda = str(loc.dda.user.username) + \
                        '('+str(loc.dda.user.name)+')'

                Ado = ''
                if loc.ado:
                    Ado = str(loc.ado.user.username) + \
                        '('+str(loc.ado.user.name)+')'

                csvFile.write(
                    str(sno) + ','
                    + str(dis) + ','
                    + str(block) + ','
                    + str(village) + ','
                    + str(longitude) + ','
                    + str(latitude) + ','
                    + str(acq_date) + ','
                    + str(dda) + ','
                    + str(Ado) + ','
                    + '\n')
            csvFile.close()
            absolute_path = DOMAIN + 'media/status_report/' + filename
            return Response({'status': 200, 'csvFile': absolute_path})


class GenerateReport(APIView):

    def get(self, request, format=None):
        directory = MEDIA_ROOT + '/reports/'
        if not os.path.exists(directory):
            os.makedirs(directory)
        # get params district and range
        start = datetime.datetime.strptime(request.GET.get(
            'start'), '%Y-%m-%d').strftime('%Y-%m-%d')
        end = datetime.datetime.strptime(request.GET.get(
            'end'), '%Y-%m-%d').strftime('%Y-%m-%d')
        district = request.GET.get('district', None)
        status = request.GET.get('status', None)
        village = request.GET.get('village', None)
        ado = request.GET.get('ado', None)
        reports = []
        if district:
            if status and village:
                reports = AdoReport.objects.filter(
                    created_on_ado__range=[start, end],
                    location__district__district=district.upper(),
                    location__status=status,
                    location__village_name__village=village.upper()
                )
                filename = 'report_' + status + '_' + district + '_' + village + '.csv'
            elif status and ado:
                reports = AdoReport.objects.filter(
                    created_on_ado__range=[start, end],
                    location__status=status,
                    location__district__district=district.upper(),
                    location__ado__user__name=ado.upper(),
                )
                filename = 'report_' + status + '_' + district + '_' + ado + '.csv'
            elif status:
                reports = AdoReport.objects.filter(
                    created_on_ado__range=[start, end],
                    location__district__district=district.upper(),
                    location__status=status
                )
                filename = 'report_all_' + status + '_' + district + '.csv'
            elif village:
                reports = AdoReport.objects.filter(
                    created_on_ado__range=[start, end],
                    location__district__district=district.upper(),
                    location__village_name__village=village.upper(),
                )
                filename = 'report_all_' + district + '_' + village + '.csv'
            elif ado:
                reports = AdoReport.objects.filter(
                    created_on_ado__range=[start, end],
                    location__district__district=district.upper(),
                    location__ado__user__name=ado.upper(),
                )
                filename = 'report_all_' + district + '_' + ado + '.csv'
            else:
                reports = AdoReport.objects.filter(
                    created_on_ado__range=[start, end],
                    location__district=district.upper(),
                )
                filename = 'report_all_' + district + '.csv'
        elif status and village:
            reports = AdoReport.objects.filter(
                created_on_ado__range=[start, end],
                location__status=status,
                location__village_name__village=village.upper(),
            )
            filename = 'report_' + status + '_' + village + '.csv'
        elif status and ado:
            reports = AdoReport.objects.filter(
                created_on_ado__range=[start, end],
                location__status=status,
                location__ado__user__name=ado.upper(),
            )
            filename = 'report_' + status + '_' + ado + '.csv'
        elif status:
            reports = AdoReport.objects.filter(
                created_on_ado__range=[start, end],
                location__status=status
            )
            filename = 'report_all_' + status + '.csv'
        else:
            reports = AdoReport.objects.filter(
                created_on_ado__range=[start, end],
            )
            filename = 'report_all.csv'

        if len(reports) == 0:
            return Response({'status': 204})
        else:
            csvFile = open(directory + filename, 'w')
            csvFile.write('Sno,District, Block Name, Village Name, Village Code, Longitude, Latitude, Acquired Date, Acquired Time, DDA Details, ADO Details, Farmer Name, Father Name, Kila Number, Murabba Number, Incident Reason, Remarks, Ownership/Lease, Action, Images\n')
            sno = 0
            for report in reports:
                sno += 1
                dis = ''
                if report.location.district:
                    dis = str(report.location.district.district)

                block = ''
                if report.location.village_name.block:
                    block = str(report.location.village_name.block.block)

                village = ''
                if report.location.village_name:
                    village = str(report.location.village_name.village)
                village_code = ''
                if report.location.village_name.village_code:
                    village_code = str(
                        report.location.village_name.village_code)

                longitude = ''
                if report.location.longitude:
                    longitude = str(report.location.longitude)

                latitude = ''
                if report.location.latitude:
                    latitude = str(report.location.latitude)

                acq_date = ''
                if report.location.acq_date:
                    acq_date = str(report.location.acq_date)

                acq_time = ''
                if report.location.acq_time:
                    acq_time = str(report.location.acq_time)

                dda = ''
                if report.location.dda:
                    dda = str(report.location.dda.user.name)

                ado = ''
                if report.location.ado:
                    ado = str(report.location.ado.user.name)

                farmer_name = ''
                if report.farmer_name:
                    farmer_name = str(report.farmer_name)

                father_name = ''
                if report.father_name:
                    father_name = str(report.father_name)

                kila_num = ''
                if report.kila_num:
                    kila_num = str(report.kila_num)

                murrabba_num = ''
                if report.murrabba_num:
                    murrabba_num = str(report.murrabba_num)

                incident_reason = ''
                if report.incident_reason:
                    incident_reason = str(report.incident_reason)

                remarks = ''
                if report.remarks:
                    remarks = str(report.remarks)

                ownership = ''
                if report.ownership:
                    ownership = str(report.ownership)

                action = ''
                if report.action:
                    action = str(report.action)

                images = Image.objects.filter(report=report).order_by('-pk')
                if len(images) > 0:
                    img = [DOMAIN + 'media/' + str(i.image) for i in images]
                else:
                    img = []
                csvFile.write(
                    str(sno) + ','
                    + str(dis) + ','
                    + str(block) + ','
                    + str(village) + ','
                    + str(village_code) + ','
                    + str(longitude) + ','
                    + str(latitude) + ','
                    + str(acq_date).replace(',', '/') + ','
                    + str(acq_time).replace(',', '/') + ','
                    + str(dda) + ','
                    + str(ado) + ','
                    + str(farmer_name) + ','
                    + str(father_name) + ','
                    + str(kila_num).replace(',', '/') + ','
                    + str(murrabba_num).replace(',', '/') + ','
                    + str(incident_reason).replace(',', '/') + ','
                    + str(remarks).replace(',', '/') + ','
                    + str(ownership).replace(',', '/') + ','
                    + str(action).replace(',', '/') + ','
                    + str(' | '.join(img)) + ','
                    + '\n')
            csvFile.close()
            absolute_path = DOMAIN + 'media/reports/' + filename
            return Response({'status': 200, 'csvFile': absolute_path})


class CountOfReports(APIView):
    def get(self, request, format=None):
        data = {}
        date = request.GET.get('date', None)  # parameter data

        if date:
            date = datetime.datetime.strptime(
                date, '%Y-%m-%d').strftime('%Y-%m-%d')
            pending_count = location.objects.filter(
                district__state=request.user.state, status='pending', acq_date=date).count()
            ongoing_count = location.objects.filter(
                district__state=request.user.state, status='ongoing', acq_date=date).count()
            completed_count = location.objects.filter(
                district__state=request.user.state, status='completed', acq_date=date).count()
            districts = District.objects.filter(state=request.user.state)
            for district in districts:
                data[str(district.district)] = {}
                data[str(district.district)]['pending'] = location.objects.filter(
                    district=district, acq_date=date, status='pending').count()
                data[str(district.district)]['ongoing'] = location.objects.filter(
                    district=district, acq_date=date, status='ongoing').count()
                data[str(district.district)]['completed'] = location.objects.filter(
                    district=district, acq_date=date, status='completed').count()
        else:
            pending_count = location.objects.filter(
                district__state=request.user.state, status='pending').count()
            ongoing_count = location.objects.filter(
                district__state=request.user.state, status='ongoing').count()
            completed_count = location.objects.filter(
                district__state=request.user.state, status='completed').count()
            districts = District.objects.filter(state=request.user.state)
            for district in districts:
                data[str(district.district)] = {}
                data[str(district.district)]['pending'] = location.objects.filter(
                    district=district, status='pending').count()
                data[str(district.district)]['ongoing'] = location.objects.filter(
                    district=district, status='ongoing').count()
                data[str(district.district)]['completed'] = location.objects.filter(
                    district=district, status='completed').count()
        return Response({
            'status': 200,
            'pending_count': pending_count,
            'ongoing_count': ongoing_count,
            'completed_count': completed_count,
            'results': data
        })


class CountOfReportsbtwdates(APIView):

    def get(self, request, format=None):
        data = {}
        startdate = request.GET.get('start_date', None)
        enddate = request.GET.get('end_date', None)
        points_to_plot = int(request.GET.get('points', 8))

        if startdate and enddate:

            a = datetime.datetime.strptime(startdate, "%Y-%m-%d")
            b = datetime.datetime.strptime(enddate, "%Y-%m-%d")
            days_per_point = int((b-a).days+1)/points_to_plot

            if days_per_point < 1:
                days_per_point = 1
                points_to_plot = int((b-a).days+1)*days_per_point

            startdate = datetime.datetime.strptime(
                startdate, '%Y-%m-%d').strftime('%Y-%m-%d')
            enddate = datetime.datetime.strptime(
                enddate, '%Y-%m-%d').strftime('%Y-%m-%d')

            pending_count = location.objects.filter(
                district__state=request.user.state, status='pending', acq_date__range=[startdate, enddate])
            ongoing_count = location.objects.filter(
                district__state=request.user.state, status='ongoing', acq_date__range=[startdate, enddate])
            completed_count = location.objects.filter(
                district__state=request.user.state, status='completed', acq_date__range=[startdate, enddate])
            p = []
            o = []
            c = []
            print("penfidnnfafds")
            print(pending_count.count())
            for x in range(0, points_to_plot):

                s = a+timedelta(days=days_per_point*x)
                e = s+timedelta(days=days_per_point-1)
                s = s.strftime('%Y-%m-%d')
                e = e.strftime('%Y-%m-%d')

                p.append({'start': s, 'end': e, 'data': pending_count.filter(
                    status='pending', acq_date__range=[s, e]).count()})
                o.append({'start': s, 'end': e, 'data': ongoing_count.filter(
                    status='ongoing', acq_date__range=[s, e]).count()})
                c.append({'start': s, 'end': e, 'data': completed_count.filter(
                    status='completed', acq_date__range=[s, e]).count()})

            districts = District.objects.filter(state=request.user.state)
            for district in districts:
                data[str(district.district)] = {}
                data[str(district.district)]['pending'] = location.objects.filter(
                    district=district, acq_date__range=[startdate, enddate], status='pending').count()
                data[str(district.district)]['ongoing'] = location.objects.filter(
                    district=district, acq_date__range=[startdate, enddate], status='ongoing').count()
                data[str(district.district)]['completed'] = location.objects.filter(
                    district=district, acq_date__range=[startdate, enddate], status='completed').count()

            return Response({
                'status': 200,
                'pending_count': p,
                'ongoing_count': o,
                'completed_count': c,
                'results': data
            })
        else:
            return Response({
                'Error': "Dates not provided"
            })


def ExportAdoPdf(request):
    ados = ado.objects.all()

    ls = []
    for a in ados:
        obj = {}
        villages = Village.objects.filter(ado=a.pk)
        obj['id'] = a.pk
        obj['username'] = a.user.username
        obj['name'] = a.user.name
        obj['email'] = a.user.email
        obj['number'] = a.user.phone_number
        obj['d'] = ''
        obj['district'] = ''
        dda_name = ''
        if len(villages) > 0:
            dda = villages[0].block.district.dda_district
            if dda:
                dda_name = dda.user.name
                district = dda.district.district
                obj['d'] = dda_name + '(' + district + ')'
            else:
                obj['d'] = "None"
        else:
            obj['d'] = "None"

        villa = []
        for village in villages:
            villa.append(village.village)
        obj['villages'] = villa
        ls.append(obj)

    content = render_to_pdf('AdoExportPdf.html', {'objects': ls})
    # dictV ={}
    # AdoObjects = ado.objects.all()
    # dictV['objects'] = AdoObjects
    # print('starting')
    # content = render_to_pdf('AdoExportPdf.html',dictV)
    # print('ending')
    return HttpResponse(content, content_type="application/pdf")


class AddAdoReport(APIView):

    def post(self, request, format=None):
        # Now it is done by frontend
        # longitude= request.data['report_longitude']
        # latitude=request.data['report_latitude']
        # result = None
        # coordinates = latitude+" ,"+longitude
        # x=0;
        # while result == None and x<1:
        #     try:
        #         result = getDetails(coordinates)
        #     except:
        #         x+=1
        #         pass
        # if(result!=None):
        #     request.data['murrabba_num']=result['Murabba No']
        #     request.data['khasra_number']=result['Khasra No']
        #     request.data['ownership']=result['Owners Name']

        serializer = AddAdoReportSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            loc = location.objects.get(pk=request.data['location'])
            loc.status = 'ongoing'
            loc.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdoReportDetail(APIView):
    # Helper function
    def get_object(self, pk):
        try:
            return AdoReport.objects.get(pk=pk)
        except AdoReport.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        # sending data according to location
        try:
            report = AdoReport.objects.get(location__id=pk)
        except AdoReport.DoesNotExist:
            raise Http404
        # report = self.get_object(pk)
        serializer = AdoReportSerializer(report, context={'request': request})
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        report = self.get_object(pk)

        if(request.data['report_longitude'] or request.data['report_latitude']):
            # longitude= request.data['report_longitude'] if request.data['report_longitude'] else report.report_longitude
            # latitude=request.data['report_latitude'] if request.data['report_latitude'] else report.report_latitude
            # result = None
            # coordinates = latitude+" ,"+longitude
            # x=0;
            # while result == None and x<1:
            #     try:
            #         result = getDetails(coordinates)
            #     except:
            #         x+=1
            #         pass
            # if result!=None:
            #     request.data['murrabba_num']=result['Murabba No']
            #     request.data['khasra_number']=result['Khasra No']
            #     request.data['ownership']=result['Owners Name']
            return Response({"error": "you cannot change these"})

        serializer = AddAdoReportSerializer(
            report, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        report = self.get_object(pk)
        report.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MailView(APIView):
    # permission_classes = []

    def post(self, request, format=None):
        directory = MEDIA_ROOT + '/FIR/'
        if not os.path.exists(directory):
            os.makedirs(directory)

        locations = []
        count = 0
        if 'location_csv' in request.data:
            if not request.data['location_csv'].name.endswith('.xlsx') and not request.data['location_csv'].name.endswith('.xls'):
                return Response({'location_csv': ['Please upload a valid document ending with .xlsx or xls']},
                                status=status.HTTP_400_BAD_REQUEST)
            fs = FileSystemStorage()
            fs.save(
                directory + request.data['location_csv'].name, request.data['location_csv'])
            wb = xlrd.open_workbook(
                directory + request.data['location_csv'].name)
            sheet = wb.sheet_by_index(0)
            rows = sheet.nrows
            locations = []
            for index in range(rows):
                locations.append(sheet.row_values(index))

            locations.pop(0)
            MAILING_LIST = {}
            directory = MEDIA_ROOT + '/mailing/'
            if not os.path.exists(directory):
                os.makedirs(directory)
            mail_data = {}
            for data in locations:
                del data[0]
                owners = str(data[9]).rstrip()
                data[9] = owners
                # Create mail data district wise
                count += 1
                district = data[0].rstrip().upper()
                dt = datetime.datetime.fromordinal(datetime.datetime(
                    1900, 1, 1).toordinal() + int(data[5]) - 2)
                hour, minute, second = floatHourToTime(data[5] % 1)
                dt = dt.replace(hour=hour, minute=minute, second=second)
                data[5] = str(dt).split(' ')[0]
                if str(district) in mail_data:
                    mail_data[str(district)].append(data)
                else:
                    mail_data[str(district)] = []
                    mail_data[str(district)].append(data)
            index = -1
            for mail in mail_data:
                logger.info("The value of var is %s", mail)
                index += 1
                new_table = {}
                owners = []
                officers_mail_id = DC.objects.filter(
                    district__district=str(mail).upper()).values('email')
                email = []
                for e in officers_mail_id:
                    email.append(e['email'])
                for row in mail_data[str(mail)]:
                    owners.append(row[9])
                    ind = mail_data[str(mail)].index(row)
                    del mail_data[str(mail)][ind][9]
                table = mail_data[str(mail)]
                new_table = []
                for row in table:
                    obj = {
                        "data": row,
                        "owners": owners[table.index(row)]
                    }
                    new_table.append(obj)
                district_mail_data = {
                    'data': new_table,
                    'date': str(datetime.date.today().strftime("%d / %m / %Y")),
                    'sno': '00' + str(index + 1)
                }
                content = render_to_pdf(
                    'mail_dc.html', district_mail_data, encoding='utf-8')
                with open(directory + str(mail) + '.pdf', 'wb') as f:
                    f.write(content)

                # Send mail to DC
                subject = "Stubble Burning Reporting"
                content = """
                    Respected Sir/Madam,<br><br>
                    Please find the attachment(s) containing data of AFL detected by HARSAC and list of owners and details of their Land.<br><br>
                    <b>Thank you</b><br>
                    <b>Department of Agriculture and Farmers Welfare, Haryana</b><br>
                """
                # email += ['akash.akashdepsharma@gmail.com']
                logger.info("The value of var is ", email)
                send_email(subject, content, email, directory +
                           str(mail) + '.pdf')   # Send mail
            return Response({'status': 'success', 'count': index+1}, status=status.HTTP_201_CREATED)
        return Response({'error': 'invalid'}, status=status.HTTP_400_BAD_REQUEST)


class TriggerSMS(APIView):

    def get(self, request, status, format=None):
        locations = location.objects.filter(status=status)

        for loc in locations:

            if loc.dda:
                conn = http.client.HTTPSConnection("api.msg91.com")
                conn.request(
                    "GET",
                    "/api/sendhttp.php?mobiles=" + loc.dda.user.phone_number + "&authkey=296120Ad3QCLsOkZI5d8d6bd5&route=4" +
                    "&sender=GNSCOA&message=You have some pending locations Please check the app for more details" + "&country=91"
                )
                res = conn.getresponse()
            if loc.ado:
                conn = http.client.HTTPSConnection("api.msg91.com")
                conn.request(
                    "GET",
                    "/api/sendhttp.php?mobiles=" + loc.ado.user.phone_number + "&authkey=296120Ad3QCLsOkZI5d8d6bd5&route=4" +
                    "&sender=GNSCOA&message=You have some pending locations Please check the app for more details" + "&country=91"
                )
                res = conn.getresponse()
        return Response()


'''
def return_excel_data_points(initial_date):
    file_path = os.path.join(MEDIA_ROOT, "firedata",
                             initial_date, "harsac", "file.xlsx")
    df_one = pd.read_excel(file_path)
    date = initial_date.split('-')
    date = date[2]+"-"+date[1]+"-"+date[0]
    df_two = df_one[df_one['Acq_Date']==date]
    df_two = df_two.query(
        'Latitude >=27.616667 and Latitude<=30.583333 and Longitude>74.46667 and Longitude<77.6')
    df_two = df_two[['Latitude', 'Longitude']]
    df_two.columns = ['latitude', 'longitude']
    df_two.to_csv(os.path.join(MEDIA_ROOT, "firedata",
                  initial_date, "harsac", "report.csv"))
    return [tuple(x) for x in df_two.values]

def return_data_points(date, dataset):
    file_path = os.path.join(MEDIA_ROOT, "firedata", date, dataset, "file.csv")
    df_one = pd.read_csv(file_path)
    df_two = df_one[df_one['acq_date']==date]
    df_two = df_two.query(
        'latitude >=27.616667 and latitude<=30.583333 and longitude>74.46667 and longitude<77.6')
    df_two = df_two[['latitude', 'longitude']]
    df_two.to_csv(os.path.join(MEDIA_ROOT, "firedata",
                  date, dataset, "report.csv"))
    return [tuple(x) for x in df_two.values]

def generate_report(date):
    datasets = ['harsac', 'modis', 'viirs_noaa', 'viirs_npp1']
    report_data = {}
    for dataset in datasets:
        file_path = os.path.join(
            MEDIA_ROOT, "firedata", date, dataset, "report.csv")
        df_one = pd.read_csv(file_path)
        df_one = df_one[['latitude', 'longitude']]
        df_one.columns = [dataset+'_latitude', dataset+'_longitude']
        report_data[dataset+'_points'] = [tuple(x) for x in df_one.values]
    return report_data

class CompareFireDataReportFile(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = []

    def get(self, request, *args, **kwargs):
        date = request.query_params.get('date', None)
        if date:
            if (os.path.isdir(os.path.join(MEDIA_ROOT, "firedata", date))):
                report = generate_report(date)
                return Response(report, status=status.HTTP_200_OK)
            return Response("Files for this date NOT FOUND", status=status.HTTP_404_NOT_FOUND)
        return Response("Invalid Date", status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):
        serializer = CompareDataSerializer(data=request.data)
        try:
            if (request.POST['force-update'] == "True"):
                if (os.path.isdir(os.path.join(MEDIA_ROOT, "firedata", serializer.initial_data['date']))):
                    shutil.rmtree(os.path.join(
                        MEDIA_ROOT, "firedata",serializer.initial_data['date']))
        except:
            pass

        if serializer.is_valid() and not (os.path.isdir(os.path.join(MEDIA_ROOT, "firedata",serializer.initial_data['date']))):
            serializer.save()
            harsac_points = return_excel_data_points(
                initial_date=serializer.initial_data['date'])
            modis_points = return_data_points(
                date=serializer.initial_data['date'], dataset="modis")
            viirs_noaa_points = return_data_points(
                date=serializer.initial_data['date'], dataset="viirs_noaa")
            virrs_npp1_points = return_data_points(
                date=serializer.initial_data['date'], dataset="viirs_npp1")
            return Response({"harsac_points": harsac_points, "modis_points": modis_points, "viirs_noaa_points": viirs_noaa_points, "viirs_npp1_points": virrs_npp1_points}, status=200)
        return Response({"error": "data already exists"}, status=400)
   '''


class LocationList_map(APIView):

    def get(self, request, format=None):
        locations = []
        start = request.GET.get('start', None)
        end = request.GET.get('end', None)
        status = request.GET.get('status', None)
        district = request.GET.get('district', None)
        if district != None:
            district = district.upper()
        role = request.user.role

        if(role == 2):
            if start and end:
                start = datetime.datetime.strptime(
                    start, '%Y-%m-%d').strftime('%Y-%m-%d')
                end = datetime.datetime.strptime(
                    end, '%Y-%m-%d').strftime('%Y-%m-%d')
                if status:
                    locations = location.objects.filter(status=status, acq_date__range=[
                                                        start, end], ado__user=request.user).order_by('-pk')
                else:
                    locations = location.objects.filter(
                        acq_date__range=[start, end], ado__user=request.user).order_by('-pk')
            else:
                if status:
                    locations = location.objects.filter(
                        status=status, ado__user=request.user).order_by('-pk')
                else:
                    locations = location.objects.filter(
                        ado__user=request.user).order_by('-pk')

        if(role == 4):
            if start and end:
                start = datetime.datetime.strptime(
                    start, '%Y-%m-%d').strftime('%Y-%m-%d')
                end = datetime.datetime.strptime(
                    end, '%Y-%m-%d').strftime('%Y-%m-%d')
                if status:
                    locations = location.objects.filter(status=status, acq_date__range=[
                                                        start, end], dda__user=request.user).order_by('-pk')
                else:
                    locations = location.objects.filter(
                        acq_date__range=[start, end], dda__user=request.user).order_by('-pk')
            else:
                if status:
                    locations = location.objects.filter(
                        status=status, dda__user=request.user).order_by('-pk')
                else:
                    locations = location.objects.filter(
                        dda__user=request.user).order_by('-pk')

        if(role == 5):

            if district:
                if start and end:
                    start = datetime.datetime.strptime(
                        start, '%Y-%m-%d').strftime('%Y-%m-%d')
                    end = datetime.datetime.strptime(
                        end, '%Y-%m-%d').strftime('%Y-%m-%d')
                    if status:
                        locations = location.objects.filter(status=status, acq_date__range=[
                                                            start, end], district__district=district, district__state=request.user.state).order_by('-pk')
                    else:
                        locations = location.objects.filter(acq_date__range=[
                                                            start, end], district__district=district, district__state=request.user.state).order_by('-pk')
                else:
                    if status:
                        locations = location.objects.filter(
                            status=status, district__district=district, district__state=request.user.state).order_by('-pk')
                    else:
                        locations = location.objects.filter(
                            district__district=district, district__state=request.user.state).order_by('-pk')
            else:
                if start and end:
                    start = datetime.datetime.strptime(
                        start, '%Y-%m-%d').strftime('%Y-%m-%d')
                    end = datetime.datetime.strptime(
                        end, '%Y-%m-%d').strftime('%Y-%m-%d')
                    if status:
                        locations = location.objects.filter(status=status, acq_date__range=[
                                                            start, end], district__state=request.user.state).order_by('-pk')
                    else:
                        locations = location.objects.filter(
                            acq_date__range=[start, end], district__state=request.user.state).order_by('-pk')
                else:
                    if status:
                        locations = location.objects.filter(
                            status=status, district__state=request.user.state).order_by('-pk')
                    else:
                        locations = location.objects.filter(
                            district__state=request.user.state).order_by('-pk')

        ls = list()
        for loc in locations:
            dic = dict()
            dic['id'] = loc.id
            dic['longitude'] = loc.longitude
            dic['latitude'] = loc.latitude
            if loc.village_name != None:
                dic['village_name'] = loc.village_name.village
            else:
                dic['village_name'] = ''
            ls.append(dic)
        return Response(ls)


def getDetails(coordinates):

    # print(coordinates)
    chrome_options = webdriver.ChromeOptions()
    # Starting webdriver with disable images option to save bandwidth.
    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('blink-settings=imagesEnabled=false')
    # Running chrome without showing window (headless mode)
    # Comment this line to stop headless mode (for debugging)
    chrome_options.add_argument("headless")
    driver = webdriver.Chrome(options=chrome_options)
    actions = ActionChains(driver)
    driver.get("https://hsac.org.in/eodb/")  # Opening website
    # This function waits and checks if a dynamic element is present or not before countinuing the script
    # If element is not found after a given timeout , it raises an exception.

    def checkElementPresence(timeout, xpath):
        try:
            element_present = EC.presence_of_element_located((By.XPATH, xpath))
            WebDriverWait(driver, timeout).until(element_present)
        except TimeoutException:
            print(f"Timed out waiting for [{xpath[-10:]}] to load")
            driver.quit()  # Quit the opened browser before ending the script.
            raise Exception("Time out error")

    checkElementPresence(
        10, '//*[@id="map"]/div[1]/div[3]/div[2]/div[2]/div/div/div[3]/form/input')

    # Find searchbox and enter coordinates.

    searchbox = driver.find_element_by_xpath(
        '//*[@id="map"]/div[1]/div[3]/div[2]/div[2]/div/div/div[3]/form/input')
    searchbox.send_keys(coordinates)
    # Find search button and click.
    searchbutton = driver.find_element_by_xpath(
        '//*[@id="map"]/div[1]/div[3]/div[2]/div[2]/div/div/div[4]')
    searchbutton.click()

    # Click on zoom button for accuracy
    checkElementPresence(
        10, '//*[@id="map"]/div[1]/div[3]/div[1]/div[2]/div[1]/div/div/div/span[1]')
    sleep(1)
    zoombutton = driver.find_element_by_xpath(
        '//*[@id="map"]/div[1]/div[3]/div[1]/div[2]/div[1]/div/div/div/span[1]')
    zoombutton.click()

    checkElementPresence(
        10, '//*[@id="map"]/div[1]/div[3]/div[1]/div[2]/div[2]/div')

    # Find the pointer pointing at the coordinates and click near it to get the details.

    pointer = driver.find_element_by_xpath(
        '//*[@id="map"]/div[1]/div[3]/div[1]/div[2]/div[2]/div')
    actions.move_to_element_with_offset(pointer, 13, 20)
    actions.click()
    actions.perform()

    checkElementPresence(
        13, '/html/body/div[1]/div[2]/div[1]/div[3]/div[1]/div[2]/div[1]/article/div/div/div/div/div/div[1]/table')

    # Reading details table

    data = driver.find_element_by_xpath(
        '/html/body/div[1]/div[2]/div[1]/div[3]/div[1]/div[2]/div[1]/article/div/div/div/div/div/div[1]/table')
    # get all of the rows in the table
    rows = data.find_elements(By.TAG_NAME, "tr")
    output_data = {}

    for row in rows:
        th = row.find_element(By.TAG_NAME, "th")
        td = row.find_element(By.TAG_NAME, "td")
        # Adding to output_data dictionary
        output_data.update({th.text: td.text})

    # Making a list for owners name.
    owner_list = []
    try:
        element_present = EC.presence_of_element_located(
            (By.XPATH, '/html/body/div[1]/div[2]/div[1]/div[3]/div[1]/div[2]/div[1]/article/div/div/div/div/div/div[2]/b/table/tbody'))
        # Wait for owners name to appear
        WebDriverWait(driver, 7).until(element_present)
        # The table containing owners name
        data = driver.find_element_by_xpath(
            '/html/body/div[1]/div[2]/div[1]/div[3]/div[1]/div[2]/div[1]/article/div/div/div/div/div/div[2]/b/table/tbody')
        # get all of the rows in the table
        rows = data.find_elements(By.TAG_NAME, "tr")
        for row in rows:
            owner_list.append(row.text)
        # Adding to dictionary as a list.
        output_data.update({"Owners Name": owner_list})
    except TimeoutException:  # If timed out
        print("Owner List Empty")
        # Adding to dictionary as a list.
        output_data.update({"Owners Name": ['No Owner Names']})

    driver.quit()  # Closing the browser
    return(output_data)


"""
class longlat(APIView):

    def get(self, request, format = None):
        longitude= request.data['longitude']
        latitude=str(request.data['latitude'])
        result = None
        coordinates = latitude+" ,"+longitude
        x=0;
        while result == None and x<1:
            try:
                result = getDetails(coordinates)
            except:
                x+=1
                pass
        if(result==None):
            return Response({"Error":"Script Not working"})
        return Response({
            "Murabba No":result['Murabba No'],
            "Khasra No":result['Khasra No'],
            "Owners Name":result['Owners Name']
            })
"""


class AddUserReport(APIView):
    permission_classes = []

    def post(self, request, format=None):
        longitude = request.data['longitude']
        latitude = request.data['latitude']
        name = request.data['name']
        phone_number = request.data['phone_number']
        response = requests.get()
        geo = response.json()

        district = None
        state = None
        village = None
        for x in range(len(geo['results'][0]['address_components'])):
            if geo['results'][0]['address_components'][x]['types'][0] == "administrative_area_level_1":
                state = geo['results'][0]['address_components'][x]['long_name']
            elif geo['results'][0]['address_components'][x]['types'][0] == "administrative_area_level_2":
                district = geo['results'][0]['address_components'][x]['long_name']
            elif geo['results'][0]['address_components'][x]['types'][0] == "locality":
                village = geo['results'][0]['address_components'][x]['long_name']
        '''
        try:
            village=geo['results'][0]['address_components'][1]['long_name']
        except Exception as e:
            village=None

        try:
            district=geo['results'][0]['address_components'][2]['long_name']
        except Exception as e:
            district =None

        try:
            state=geo['results'][0]['address_components'][3]['long_name']
        except Exception as e:
            state=None
        '''
        # source=NormalUserReport.objects.filter(phone_number=phone_number,name=name,longitude=longitude,latitude=latitude)[0]

        # if len(source)==0:
        source = NormalUserReport.objects.create(
            phone_number=phone_number, name=name, longitude=longitude, latitude=latitude)
        # else:
        #     source=source[0]
        try:
            loc = []
            loc = location.objects.filter(
                longitude=longitude, latitude=latitude, status='pending')

            if len(loc) == 0:

                d = []
                if district != None and state != None:
                    d = District.objects.filter(
                        state__state=state.upper(), district=district.upper())
                if(len(d) == 1):
                    district = d[0]
                else:
                    district = None

                dda_final = None
                if district != None:
                    dda_final = district.dda_district

                v = []
                if district != None and village != None:
                    v = Village.objects.filter(
                        block__district=d[0], village=village.upper())
                if(len(v) == 1):
                    village = v[0]
                else:
                    village = None

                ado_final = None
                if village != None:
                    ado_final = village.ado

                new_location = location.objects.create(
                    district=district, village_name=village, longitude=longitude, latitude=latitude, dda=dda_final, ado=ado_final, source=source)
                # print(new_location)
                new_location.save()
                return Response({
                    'location_id': new_location.pk,
                    'NormalUserReport_id': source.pk})
            else:
                loc = loc[0]
                loc.source = source
                loc.status = 'pending'
                loc.save()
                return Response({
                    'location_id': loc.pk,
                    'NormalUserReport_id': source.pk
                })
        except Exception as e:
            source.delete()
            print(e)
            return Response({
                'Error': 'Some error occured'
            })


class AddUserReportImage(APIView):
    permission_classes = []

    def post(self, request, format=None):
        serializer = AddImageNormalUserReport(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class location_data(APIView):  # 31.1451,76.1008
    permission_classes = []

    def get(self, request, format=None):

        latitude = str(request.data['latitude'])
        longitude = str(request.data['longitude'])
        response = requests.get()
        geo = response.json()

        district = None
        state = None
        village = None
        for x in range(len(geo['results'][0]['address_components'])):
            if geo['results'][0]['address_components'][x]['types'][0] == "administrative_area_level_1":
                state = geo['results'][0]['address_components'][x]['long_name']
            elif geo['results'][0]['address_components'][x]['types'][0] == "administrative_area_level_2":
                district = geo['results'][0]['address_components'][x]['long_name']
            elif geo['results'][0]['address_components'][x]['types'][0] == "locality":
                village = geo['results'][0]['address_components'][x]['long_name']
        return Response({
            'District': district,
            'State': state,
            'village': village
        })


class latlong_data(APIView):  # 31.1451,76.1008
    permission_classes = []

    def get(self, request, lat, lon, format=None):

        latitude = str(lat)
        longitude = str(lon)
        response = requests.get()
        geo = response.json()

        district = None
        state = None
        village = None
        for x in range(len(geo['results'][0]['address_components'])):
            if geo['results'][0]['address_components'][x]['types'][0] == "administrative_area_level_1":
                state = geo['results'][0]['address_components'][x]['long_name']
            elif geo['results'][0]['address_components'][x]['types'][0] == "administrative_area_level_2":
                district = geo['results'][0]['address_components'][x]['long_name']
            elif geo['results'][0]['address_components'][x]['types'][0] == "locality":
                village = geo['results'][0]['address_components'][x]['long_name']
        return Response({
            'District': district,
            'State': state,
            'village': village
        })
# to appoint new state_admin of some state


class StateAdminChange(APIView):

    def post(self, request, format=None):
        s_id = request.data['state_id']
        sa_id = request.data.get('state_admin_id', None)

        try:
            state = State.objects.get(pk=s_id)
        except Exception as e:
            return Response({
                'Error': "State does not exist"
            })

        if sa_id != None:  # in case of transfer

            try:
                state_admin_new = state_admin.objects.get(pk=sa_id)
            except Exception as e:
                return Response({
                    'Error': "STATE_ADMIN does not exist for passed state_Admin_id"
                })
            # remove previous state admin
            state_admin_old = state_admin.objects.filter(state=state)
            if(len(state_admin_old) != 0):
                state_admin_old[0].state = None
                state_admin_old[0].save()
            # add new state admin
            state_admin_new.state = state
            state_admin_new.save()

            serializer = StateAdminSerializer(
                state_admin_new, context={'request': request})
            return Response(serializer.data)

        else:  # in case of retirement
            # remove previous state admin
            state_admin_old = state_admin.objects.filter(state=state)
            if(len(state_admin_old) != 0):
                state_admin_old[0].state = None
                state_admin_old[0].save()

                serializer = StateAdminSerializer(
                    state_admin_old[0], context={'request': request})
                return Response(serializer.data)

            return Response({
                'Error': "State didnt had an Admin"
            })


class DDAChange(APIView):

    def post(self, request, format=None):
        d_id = request.data['District_id']
        dda_id = request.data.get('dda_id', None)

        try:
            district = District.objects.get(pk=d_id)
        except Exception as e:
            return Response({
                'Error': "District does not exist"
            })

        if dda_id != None:
            try:
                dda_new = dda.objects.get(pk=dda_id)
            except Exception as e:
                return Response({
                    'Error': "DDA does not exist for passed dda_id"
                })
            # remove previous dda
            dda_old = dda.objects.filter(district=district)
            if(len(dda_old) != 0):
                dda_old[0].district = None
                dda_old[0].save()
            # add new state admin
            dda_new.district = district
            dda_new.save()

            serializer = DdaSerializer(dda_new, context={'request': request})
            return Response(serializer.data)

        else:                                               # no dda given in the request implies remove the current dda
            # extract current dda of the district
            dda_old = dda.objects.filter(district=district)

            if(len(dda_old) != 0):
                dda_old[0].district = None
                dda_old[0].save()
                serializer = DdaSerializer(
                    dda_old[0], context={'request': request})
                return Response(serializer.data)

            else:
                return Response({
                    'Error': "This district does not have a DDA"
                })


class ADOChange(APIView):

    def post(self, request, format=None):
        vill_id = request.data['Village_id']
        ado_id = request.data.get('ado_id', None)
        try:
            village = Village.objects.get(pk=vill_id)
        except Exception as e:
            return Response({
                'Error': "Village does not exist"
            })

        if ado_id != None:
            try:
                ado_new = ado.objects.get(pk=ado_id)
            except Exception as e:
                return Response({
                    'Error': "ADO does not exist for passed ado_id"
                })

            # we can assign ado_new only when it belongs to the same district as
            if(ado_new.district == village.block.district):
                # the district under which the village is present
                village.ado = ado_new
                village.save()
                serializer = VillageSerializer(
                    village, context={'request': request})
                return Response(serializer.data)

            else:
                return Response({
                    'Error': "The ADO doesnot came under the same district as the village"
                })
        else:                                          # just remove the ado from the village
            village.ado = None
            village.save()
            serializer = VillageSerializer(
                village, context={'request': request})
            return Response(serializer.data)


class VillageChange(APIView):
    def post(self, request, format=None):

        villages_id = []
        villages = dict()
        villages_id = request.data.get('Villages_id')
        ado_id = request.data.get('ado_id', None)
        try:
            ado_new = ado.objects.get(pk=ado_id)
        except Exception as e:
            return Response({'Error': "ado for " + ado_id + " does not exist"})

        # make ado of each village in under given ado as null.
        adovillages = Village.objects.filter(ado=ado_new)
        for vill in adovillages:
            vill.ado = None
            vill.save()

        for vill_id in villages_id:
            try:
                village = Village.objects.get(pk=vill_id)
            except Exception as e:
                return Response({'Error': "Village for " + vill_id + " does not exist"})

            village.ado = ado_new  # change ado of given villages.
            village.save()
            dic = dict()
            dic['id'] = village.id
            dic['village'] = village.village
            dic['ado'] = village.ado.id
            villages[village.id] = dic
        return Response(villages)


class multipleuser(APIView):
    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404

    def delete(self, request, format=None):
        user_ids = []
        user_ids = request.data.get('user_ids')
        for id in user_ids:
            user = self.get_object(id)
            user.delete()
            # user = self.get_object(id)
            # print(user.password)
        return Response(status=status.HTTP_204_NO_CONTENT)


class GetNASAData(APIView):

    # permission_classes=[]
    def get(self, request, format=None):

        date = request.GET.get('date', None)
        if(date == None):
            return Response({'error': 'Date not passed'}, status=status.HTTP_400_BAD_REQUEST)
        directory = MEDIA_ROOT + '/NASADATA/'+date+'/'
        if not os.path.exists(directory):
            return Response({'error': 'Requested date data is not available'}, status=status.HTTP_400_BAD_REQUEST)

        ppath_VIIRS_375_S_NPP = 'NOT AVAILABLE'
        ppath_VIIRS_375m_NOAA = 'NOT AVAILABLE'
        ppath_MODIS_1km = 'NOT AVAILABLE'
        ppath_HARSAC = 'NOT AVAILABLE'
        if(os.path.isfile(os.path.join(directory, 'VIIRS_375_S-NPP_'+date+'.csv'))):
            ppath_VIIRS_375_S_NPP = DOMAIN+'media/NASADATA/' + \
                date+'/'+'VIIRS_375_S-NPP_'+date+'.csv'
        if(os.path.isfile(os.path.join(directory, 'VIIRS_375m_NOAA_'+date+'.csv'))):
            ppath_VIIRS_375m_NOAA = DOMAIN+'media/NASADATA/' + \
                date+'/'+'VIIRS_375m_NOAA_'+date+'.csv'
        if(os.path.isfile(os.path.join(directory, 'MODIS_1km_'+date+'.csv'))):
            ppath_MODIS_1km = DOMAIN+'media/NASADATA/'+date+'/'+'MODIS_1km_'+date+'.csv'
        if(os.path.isfile(os.path.join(directory, 'HARSAC_'+date+'.csv'))):
            ppath_HARSAC = DOMAIN+'media/NASADATA/'+date+'/'+'HARSAC_'+date+'.csv'

        return Response({'VIIRS_375_S-NPP': ppath_VIIRS_375_S_NPP, 'VIIRS_375m_NOAA': ppath_VIIRS_375m_NOAA, 'MODIS_1km': ppath_MODIS_1km, 'HARSAC': ppath_HARSAC}, status=status.HTTP_200_OK)


class CompareFireDataReport(APIView):
    parser_classes = (MultiPartParser, FormParser)
    # permission_classes = []

    def get(self, request, *args, **kwargs):
        date = request.query_params.get('date', None)
        try:
            date = datetime.datetime.strptime(
                date, '%Y-%m-%d').strftime('%Y-%m-%d')
        except Exception as e:
            return Response("Invalid Date", status=status.HTTP_400_BAD_REQUEST)

        if date:
            datasets = ['HARSAC', 'MODIS', 'NOAA', 'NPP']
            report = {}
            for dataset in datasets:
                report[dataset+'_points'] = [tuple([x.latitude, x.longitude])
                                             for x in NASALocationData.objects.filter(satellite=dataset, acq_date=date)]
            return Response(report, status=status.HTTP_200_OK)
        return Response("Invalid Date", status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, *args, **kwargs):

        directory = os.path.join(MEDIA_ROOT, 'HARSAC_DATA')

        if 'harsac_file' in request.data:
            if not request.data['harsac_file'].name.endswith('.xlsx') and not request.data['harsac_file'].name.endswith('.xls'):
                return Response({'harsac_file': ['Please upload a valid document ending with .xlsx']},
                                status=status.HTTP_400_BAD_REQUEST)
            # storing raw data in HARSAC_DATA
            st = str(uuid.uuid1())
            fs = FileSystemStorage()
            fs.save(os.path.join(directory, 'HARSAC_RAW'+request.data['harsac_file'].name+str(
                datetime.datetime.now()).split()[0]+st), request.data['harsac_file'])

            # reading file with pandas
            try:
                df_one = pd.read_excel(os.path.join(
                    directory, 'HARSAC_RAW'+request.data['harsac_file'].name+str(datetime.datetime.now()).split()[0]+st))
            except Exception as e:
                return Response({'harsac_file': ['Corrupted file']},
                                status=status.HTTP_400_BAD_REQUEST)

            # in snpp data longitude is written first then latitude so swapped them
            checker = 0
            try:
                df_one = df_one[['State', 'District', 'Block Name',
                                 'Village Name', 'longitude', 'latitude', 'acq_date', 'acq_time']]
                checker = 1
            except Exception as e:
                print(e)
            try:
                df_one = df_one[['State', 'District', 'Block Name',
                                 'Village Name', 'Longitude', 'Latitude', 'Acq_Date', 'Acq_Time']]
                checker = 1
            except Exception as e:
                print(e)

            # incase header does not match any format
            if checker == 0:
                return Response({'harsac_file': ['Invalid Content.Columns required- State , District , Block Name , Village Name , Longitude , Latitude , Acq_Date , Acq_Time']}, status=status.HTTP_400_BAD_REQUEST)

            # camel casing
            df_one.columns = ['State', 'District', 'Block Name',
                              'Village Name', 'Longitude', 'Latitude', 'Acq_Date', 'Acq_Time']

            # convertig datetime object to string
            try:
                df_one['Acq_Date'] = df_one['Acq_Date'].dt.date
                df_one['Acq_Date'] = df_one['Acq_Date'].apply(
                    lambda x: x.strftime('%d-%m-%Y'))
            except Exception as e:
                print(e)
            # changing format of date
            for fmt in ('%d-%m-%Y', '%d/%m/%Y', '%d.%m.%Y'):
                try:
                    df_one['Acq_Date'] = df_one['Acq_Date'].apply(
                        lambda x: datetime.datetime.strptime(x, fmt).strftime('%Y-%m-%d'))
                    break
                except Exception as e:
                    if fmt == '%d.%m.%Y':
                        return Response({'harsac_file': ['Invalid date format, required format %d-%m-%Y']},
                                        status=status.HTTP_400_BAD_REQUEST)
                    print(e)
            # opening csv file
            dt_file = df_one['Acq_Date'][0]
            directory = os.path.join(MEDIA_ROOT, 'NASADATA', dt_file)
            filename = 'HARSAC_'+dt_file+'.csv'

            csvFile = None
            if not os.path.exists(directory):
                os.makedirs(directory)
            if(os.path.isfile(os.path.join(directory, filename))):
                csvFile = open(os.path.join(directory, filename), 'a')
            else:
                csvFile = open(os.path.join(directory, filename), 'w')
                csvFile.write(
                    'State,District,Block,Village,longitude,latitude,acq_date,acq_time\n')

            # adding new data
            new = 0
            present = 0
            for data in df_one[0:].values:
                if not (float(data[5]) <= 30.58333 and float(data[5]) >= 27.39 and float(data[4]) <= 77.6 and float(data[4]) >= 74.28):
                    print(data[5], data[4])
                    continue
                dat = {}
                dat['state'] = data[0].upper()
                dat['district'] = data[1].upper()
                dat['block_name'] = data[2].upper()
                dat['village_name'] = data[3].upper()
                dat['longitude'] = data[4]
                dat['latitude'] = data[5]
                dat['acq_date'] = data[6]
                dat['acq_time'] = data[7].split('.')[0]
                dat['satellite'] = 'HARSAC'

                if len(NASALocationData.objects.filter(longitude=dat['longitude'], latitude=dat['latitude'], acq_date=dat['acq_date'], satellite='HARSAC')) > 0:
                    present = present+1
                    continue
                try:
                    serializer = AddNASALocationDataSerializer(data=dat)
                    if serializer.is_valid():
                        new = new+1
                        serializer.save()
                        csvFile.write(
                            str(data[0]) + ','
                            + str(data[1]) + ','
                            + str(data[2]) + ','
                            + str(data[3]) + ','
                            + str(data[4]) + ','
                            + str(data[5]) + ','
                            + str(dat['acq_date']) + ','
                            + str(dat['acq_time']) + ','
                            + '\n')
                except Exception as e:
                    print(e)

            csvFile.close()
            return Response({"NEW ADDED": new, "ALREADY EXIST": present}, status=status.HTTP_200_OK)
        return Response({'harsac_file': ['No file attached']}, status=status.HTTP_400_BAD_REQUEST)


class ComparisonReport(APIView):
    parser_classes = (MultiPartParser, FormParser)
    # permission_classes = []

    def get(self, request, *args, **kwargs):
        start_date = request.query_params.get('Start date', None)
        end_date = request.query_params.get('End date', None)

        try:
            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
        except Exception as e:
            print(e)
            return Response("Invalid Date", status=status.HTTP_400_BAD_REQUEST)

        delta = int((end_date-start_date).days)
        arr = [str(start_date+timedelta(days=i)).split()[0]
               for i in range(delta+1)]  # date as string

        if(delta < 0):
            return Response("Invalid Date", status=status.HTTP_400_BAD_REQUEST)

        m_path = os.path.join(MEDIA_ROOT, 'ComparisonReport')
        try:
            os.mkdir(m_path)
        except:
            pass
        path_repo = os.path.join(MEDIA_ROOT, 'ComparisonReport', str(
            start_date).split()[0]+'_'+str(end_date).split()[0]+'report.csv')
        csvFile = open(path_repo, 'w')
        csvFile.write('DataSet Name,Date,No of Exact Matches,No of extra locations,Matches upto 1 decimal place,Matches upto 2 decimal places,Matches upto 3 decimal places,Matches upto 4 decimal places,Matches upto 5 decimal places,Max Lat_Diff,Min Lat_Diff,Max Long_Diff,Min Long_Diff\n')

        for date in arr:
            df2 = pd.DataFrame(list(NASALocationData.objects.filter(
                satellite='HARSAC', acq_date=date).values()))
            datasets = ['NPP', 'NOAA', 'MODIS']

            for j in datasets:
                df1 = pd.DataFrame(list(NASALocationData.objects.filter(
                    satellite=j, acq_date=date).values()))
                df1.drop_duplicates(
                    subset=['longitude', 'latitude'], inplace=True)

                l1 = []  # List to store data for report
                l1.append(j)
                l1.append(date)
                l1.append(len(df1))
                l1.append(len(df2))
                latitude = []
                longitude = []
                acq_date = []
                acq_time = []
                lat_diff = []
                long_diff = []
                source = []
                mis_matches = 0

                for x in range(df2.shape[0]):
                    row1 = df2.iloc[x]
                    source.append('HARSAC')
                    min_lat = float('inf')
                    min_long = float('inf')
                    min_index = -1
                    latitude.append(row1['latitude'])
                    longitude.append(row1['longitude'])  # harsac
                    acq_date.append(row1['acq_date'])
                    acq_time.append(row1['acq_time'])
                    lat_diff.append(None)
                    long_diff.append(None)

                    for y in range(df1.shape[0]):
                        row2 = df1.iloc[y]  # npp
                        # print(row1['latitude'],type(row1['latitude']))
                        # diff_lat=abs(row1['latitude']-pd.to_numeric(row2['latitude']))
                        # diff_long=abs(row1['longitude']-pd.to_numeric(row2['longitude']))
                        diff_lat = abs(
                            float(row1['latitude'])-float(row2['latitude']))
                        diff_long = abs(
                            float(row1['longitude'])-float(row2['longitude']))
                        if diff_lat <= min_lat and diff_long <= min_long and diff_lat < 0.1 and diff_long < 0.1:  # Threshold for match
                            min_lat = diff_lat
                            min_long = diff_long
                            min_index = y

                    if min_index != -1:
                        source.append(j)
                        row3 = df1.iloc[min_index]  # npp
                        latitude.append(row3['latitude'])
                        longitude.append(row3['longitude'])
                        acq_date.append(row3['acq_date'])
                        acq_time.append(row3['acq_time'])
                        lat_diff.append(min_lat)
                        long_diff.append(min_long)
                    else:
                        mis_matches += 1

                data = {'source': source, 'latitude': latitude, 'longitude': longitude,
                        'lat_diff': lat_diff, 'long_diff': long_diff, 'acq_date': acq_date, 'acq_time': acq_time}
                df5 = pd.DataFrame(data)
                matches_upto_3 = len(
                    df5[(df5['lat_diff'] < 0.001) & (df5['long_diff'] < 0.001)])
                matches_upto_2 = len(
                    df5[(df5['lat_diff'] < 0.01) & (df5['long_diff'] < 0.01)])
                matches_upto_1 = len(
                    df5[(df5['lat_diff'] < 0.1) & (df5['long_diff'] < 0.1)])
                matches_upto_4 = len(
                    df5[(df5['lat_diff'] < 0.0001) & (df5['long_diff'] < 0.0001)])
                matches_upto_5 = len(
                    df5[(df5['lat_diff'] < 0.00001) & (df5['long_diff'] < 0.00001)])
                exact_matches = len(
                    df5[(df5['lat_diff'] == 0) & (df5['long_diff'] == 0)])
                max_lat_diff = df5['lat_diff'].max(axis=0, skipna=True)
                min_lat_diff = df5['lat_diff'].min(axis=0, skipna=True)
                max_long_diff = df5['long_diff'].max(axis=0, skipna=True)
                min_long_diff = df5['long_diff'].min(axis=0, skipna=True)
                l1.append(exact_matches)
                l1.append(mis_matches)
                l1.append(matches_upto_1)
                l1.append(matches_upto_2)
                l1.append(matches_upto_3)
                l1.append(matches_upto_4)
                l1.append(matches_upto_5)
                l1.append(max_lat_diff)
                l1.append(min_lat_diff)
                l1.append(max_long_diff)
                l1.append(min_long_diff)

                csvFile.write(
                    str(l1[0]) + ','
                    + str(l1[1]) + ','
                    + str(l1[4]) + ','
                    + str(l1[5]) + ','
                    + str(l1[6]) + ','
                    + str(l1[7]) + ','
                    + str(l1[8]) + ','
                    + str(l1[9]) + ','
                    + str(l1[10]) + ','
                    + str(l1[11]) + ','
                    + str(l1[12]) + ','
                    + str(l1[13]) + ','
                    + str(l1[14])
                    + '\n')
        csvFile.close()
        return Response({'ComparisonReport': DOMAIN+'media/ComparisonReport/'+str(start_date).split()[0]+'_'+str(end_date).split()[0]+'report.csv'}, status=status.HTTP_200_OK)


class LocationLandData(APIView):

    def get(self, request, format=None):

        loc = request.data.get('location')
        Location = location.objects.filter(id=loc)
        print(len(Location))
        if len(Location) == 0:
            return Response({'Error': ['No location for provided id']}, status=status.HTTP_400_BAD_REQUEST)

        res = LocationGeoData.objects.filter(location=Location[0])
        print(len(res))
        if len(res) == 1:
            serializer = AddLocationGeoDataSerializer(
                res[0], context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            result = None
            coordinates = Location[0].latitude+" ,"+Location[0].longitude
            x = 0
            while result == None and x < 5:
                try:
                    result = getDetails(coordinates)
                except:
                    x += 1
                    pass
            if(result == None):
                return Response({"Error": "No data available"})

            geodata = dict()
            geodata['location'] = loc
            geodata['murrabba_num'] = result['Murabba No']
            geodata['khasra_number'] = result['Khasra No']
            geodata['ownership'] = '|'.join(result['Owners Name'])
            try:
                serializer1 = AddLocationGeoDataSerializer(data=geodata)
                if serializer1.is_valid():
                    serializer1.save()
                    return Response(serializer1.data, status=status.HTTP_200_OK)
                else:
                    print(serializer1.errors)
            except:
                pass
            return Response({
                "id": None,
                "Murabba No": result['Murabba No'],
                "Khasra No": result['Khasra No'],
                "Owners Name": '|'.join(result['Owners Name']),
                "location": loc
            })


class ResetPass(APIView):
    permission_classes = []

    def post(self, request, format=None):
        username = request.data.get('username')
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise Http404
        token = TemporaryToken.objects.get_or_create(user=user)
        print(token[0])
        uid = user.pk
        data = {
            'uid': uid,
            'token': token[0]
        }
        email = [user.email]
        subject = "change password"
        html_message = render_to_string('mail_password.html', data)
        plain_message = strip_tags(html_message)
        from_email = 'aflmangement@gmail.com'
        mail.send_mail(subject, plain_message, from_email,
                       email, html_message=html_message)
        return Response({'status': 'success'}, status=status.HTTP_201_CREATED)


class confirmpass(APIView):
    permission_classes = []

    def get(self, request, uid, Token, format=None):
        user = User.objects.get(id=uid)
        try:
            token = TemporaryToken.objects.get(user=user)
            print(token)
            print(Token)
        except token.DoesNotExist:
            raise Http404
        if str(Token) == str(token):
            return Response({"uid": user.pk, "status": "success"})
        else:
            return Response({"error": "different tokens"})


class changepass(APIView):
    permission_classes = []

    def post(self, request, uid, Token, format=None):
        user = User.objects.get(id=uid)
        new_pass = request.data.get('password')
        try:
            token = TemporaryToken.objects.get(user=user)
        except Exception as e:
            return Response({'Error': "invalid token"})
        if str(Token) == str(token):
            user.set_password(new_pass)
            user.save()
            return Response({"status": "success"})
        else:
            return Response({
                "error": "token expired"
            })


class changepassandroid(APIView):
    permission_classes = []

    def post(self, request, uid, format=None):
        try:
            user = User.objects.get(id=uid)
        except Exception as e:
            return Response({"status": "invalid user-id"})
        new_pass = request.data.get('password')
        user.set_password(new_pass)
        user.save()
        return Response({"status": "success"})


class Adoassign(APIView):
    def get_object(self, pk):
        try:
            return location.objects.get(pk=pk)
        except location.DoesNotExist:
            raise Http404

    def put(self, request, pk, format=None):
        location = self.get_object(pk)
        serializer = AddLocationSerializer(
            location, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
