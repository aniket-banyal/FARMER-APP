from re import search
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from users.models import *


class StateSerializerLite(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ['state']


class UserSerializerLite(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'name']


class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    password = serializers.CharField(min_length=8, write_only=True)

    role = serializers.IntegerField()
    image = serializers.ImageField()
    state = StateSerializerLite()
    # def create(self, validated_data):
    #     user = User.objects.create_user(
    #         username=validated_data['username'],
    #         email=validated_data['email'],
    #         password=validated_data['password'],
    #         role=validated_data['role']
    #     )
    #     return user

    # image = serializers.SerializerMethodField('get_image_url')

    # def get_image_url(self, user):
    #     request = self.context.get('request')
    #     photo_url = user.image.url
    #     return request.build_absolute_uri(photo_url)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'role',
                  'name', 'image', 'state', 'phone_number']
# post


class AddLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = location
        fields = '__all__'


class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = '__all__'


class DistrictSerializer(serializers.ModelSerializer):
    state = StateSerializer()

    class Meta:
        model = District
        fields = ['id', 'district', 'district_code', 'state', 'has_blocks']


class DistrictSerializerlite(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = ['id', 'district', 'district_code', 'has_blocks']


class DistrictSerializerProlite(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = ['id', 'district']


class AddDistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = '__all__'


class AddDdaSerializer(serializers.ModelSerializer):
    class Meta:
        model = dda
        fields = '__all__'


class AddBlock_adminSerializer(serializers.ModelSerializer):
    class Meta:
        model = block_admin
        fields = '__all__'


class AddAdoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ado
        fields = '__all__'


class AddSuperadminSerializer(serializers.ModelSerializer):
    class Meta:
        model = super_admin
        fields = '__all__'


class AddFarmer_ecomSerializer(serializers.ModelSerializer):
    class Meta:
        model = farmer_ecom
        fields = '__all__'


class AddIndustry_ecomSerializer(serializers.ModelSerializer):
    class Meta:
        model = industry_ecom
        fields = '__all__'


class Addstate_admin_serializer(serializers.ModelSerializer):
    class Meta:
        model = state_admin
        fields = '__all__'


class AddVillageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Village
        fields = '__all__'


class AddBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Block
        fields = '__all__'


class AddFarmerSerializer(serializers.ModelSerializer):
    class Meta:
        model = farmer
        fields = '__all__'


class AddAdoReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdoReport
        fields = '__all__'


class AddImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = '__all__'


class AddImageNormalUserReport(serializers.ModelSerializer):
    class Meta:
        model = ImageNormalUserReport
        fields = '__all__'


class CompareDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompareData
        fields = '__all__'


class AddNASALocationDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = NASALocationData
        fields = '__all__'


class AddLocationGeoDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocationGeoData
        fields = '__all__'


class DCSerializer(serializers.ModelSerializer):
    class Meta:
        model = DC
        fields = '__all__'


class SPSerializer(serializers.ModelSerializer):
    class Meta:
        model = SP
        fields = '__all__'


"""
class ImageSerializer(serializers.HyperlinkedModelSerializer):
     class Meta:
         model = Image
         fields = ('image','report')
"""


class AdoSerializerLite(serializers.ModelSerializer):
    user = UserSerializerLite()

    class Meta:
        model = ado
        fields = ['id', 'user']

class farmer_ecomSerializerLite(serializers.ModelSerializer):
    user = UserSerializerLite()

    class Meta:
        model = farmer_ecom
        fields = ['id', 'user']        

class industry_ecomSerializerLite(serializers.ModelSerializer):
    user = UserSerializerLite()

    class Meta:
        model = industry_ecom
        fields = ['id', 'user']        


class DdaSerializerLite(serializers.ModelSerializer):
    user = UserSerializerLite()

    class Meta:
        model = dda
        fields = ['id', 'user']


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ('image', 'report')


class AppVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppVersion
        fields = '__all__'


class StateAdminSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    state = StateSerializer()

    class Meta:
        model = state_admin
        fields = ['id', 'state', 'user']


class BlockSerializer(serializers.ModelSerializer):
    district = DistrictSerializer()

    class Meta:
        model = Block
        fields = ['id', 'block', 'block_code', 'district']


class BlockSerializerLite(serializers.ModelSerializer):
    class Meta:
        model = Block
        fields = ['id', 'block']


class VillageSerializer(serializers.ModelSerializer):
    district = serializers.SerializerMethodField('get_district_name')
    block = serializers.SerializerMethodField('get_block_name')
    ado = AdoSerializerLite()

    def get_district_name(self, obj):
        return obj.block.district.district

    def get_block_name(self, obj):
        return obj.block.block

    class Meta:
        model = Village
        fields = ['id', 'village', 'village_code',
                  'village_subcode', 'block', 'district', 'ado']


class VillageSerializerLite(serializers.ModelSerializer):

    class Meta:
        model = Village
        fields = ['id', 'village']


class VillageSerializerSpecific(serializers.ModelSerializer):
    district = serializers.SerializerMethodField('get_district_name')
    ado = AdoSerializerLite()
    block = BlockSerializerLite()

    def get_district_name(self, obj):
        return obj.block.district.district

    class Meta:
        model = Village
        fields = ['id', 'village', 'village_code',
                  'village_subcode', 'block', 'district', 'ado']


class SuperadminSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = super_admin
        fields = ['id', 'user']


class DdaSerializer(serializers.ModelSerializer):

    user = UserSerializer()
    district = DistrictSerializer()

    class Meta:
        model = dda
        fields = ['id', 'district', 'user']


class BlockAdminSerializer(serializers.ModelSerializer):

    user = UserSerializer()
    block = BlockSerializer()

    class Meta:
        model = block_admin
        fields = ['id', 'user', 'block']
class farmer_ecomSerializer(serializers.ModelSerializer):

    user = UserSerializer()

    class Meta:
        model = farmer_ecom
        fields = ['id', 'user']
        
class industry_ecomSerializer(serializers.ModelSerializer):

    user = UserSerializer()
   

    class Meta:
        model = industry_ecom
        fields = ['id', 'user']


class AdoSerializer(serializers.ModelSerializer):

    village_ado = VillageSerializer(many=True, read_only=True)
    user = UserSerializer()
    # district=serializers.SerializerMethodField('get_district_name')
    dda = serializers.SerializerMethodField('get_dda_name')
    # dda_district=DdaSerializerLite()
    district = DistrictSerializerlite()

    # def get_district_name(self, obj):
    #     try:
    #         return obj.district.district
    #     except Exception as e:
    #         return ''

    def get_dda_name(self, obj):
        # if obj.district!=None and obj.district.dda_district!=None:
        try:
            addr = dict()
            addr['id'] = obj.district.dda_district.id
            addr['username'] = obj.district.dda_district.user.username
            addr['name'] = obj.district.dda_district.user.name
            addr['phone_number'] = obj.district.dda_district.user.phone_number
            addr['email'] = obj.district.dda_district.user.email
            return addr
        except Exception as e:
            return ""
        # else:
        #     return ''

    class Meta:
        model = ado
        fields = ['id', 'user', 'village_ado', 'district', 'dda']


class FarmerSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = farmer
        fields = ['id', 'user', 'subsidies', 'farmer_code',
                  'fathers_name', 'farmer_code_status']


class NormalUserReportSerializer(serializers.ModelSerializer):
    normal_user_reported_image = AddImageNormalUserReport(many=True)

    class Meta:
        model = NormalUserReport
        fields = ['id', 'name', 'phone_number', 'normal_user_reported_image']


class LocationSerializer(serializers.ModelSerializer):
    ado = AdoSerializerLite(read_only=True)
    dda = DdaSerializerLite(read_only=True)
    # district=serializers.SerializerMethodField('get_district_name')
    district = DistrictSerializerProlite()
    village_name = VillageSerializerLite()
    # village_name = serializers.SerializerMethodField('get_village_name')
    state = serializers.SerializerMethodField('get_state_name')
    block = serializers.SerializerMethodField('get_block_name')
    source = NormalUserReportSerializer()

    # def get_village_name(self, obj):
    #     try:
    #         return obj.village_name.village
    #     except Exception as e:
    #         return ''

    # def get_district_name(self, obj):
    #     try:
    #         return obj.district.district
    #     except Exception as e:
    #         return ''

    def get_state_name(self, obj):
        try:
            return obj.district.state.state
        except Exception as e:
            return ""

    def get_block_name(self, obj):
        try:
            return obj.village_name.block.block
        except Exception as e:
            return ""

    class Meta:
        model = location
        fields = ['id', 'state', 'district', 'block', 'village_name', 'longitude',
                  'latitude', 'dda', 'ado', 'acq_date', 'acq_time', 'status', 'created_on', 'source']


class SuperAdminSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = super_admin
        fields = ['id', 'user']


class AdoReportSerializer(serializers.ModelSerializer):

    # farmer=AddFarmerSerializer()
    location = AddLocationSerializer()

    class Meta:
        model = AdoReport
        fields = ['id', 'farmer_code', 'farmer_name', 'father_name', 'location', 'report_longitude', 'report_latitude', 'kila_num',
                  'murrabba_num', 'incident_reason', 'amount', 'remarks', 'ownership', 'action', 'fir', 'challan', 'flag', 'fire', 'created_on_ado']
