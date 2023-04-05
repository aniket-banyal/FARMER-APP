from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.utils import timezone
from django.core.validators import (
    FileExtensionValidator, RegexValidator
)
from app.models import (Order, RentOrder, ResidueOrder)


actions = (('chalaan', 'Challan'), ('FIR', 'FIR'))
flags = (('start', 'Start'), ('stop', 'Stop'))
choices_status = (('pending', 'pending'), ('ongoing',
                  'ongoing'), ('completed', 'completed'))
fire_choice = (('fire', 'Fire'), ('nofire', 'No Fire'))


class AppVersion(models.Model):
    version = models.CharField(max_length=200)

    class Meta:
        get_latest_by = 'version'

    def __str__(self):
        return str(self.version)


class State(models.Model):
    state = models.CharField(max_length=500, blank=True, unique=True)
    state_code = models.CharField(max_length=200, blank=True, unique=True)

    def save(self, *args, **kwargs):
        if self.state:
            self.state = self.state.upper()
        return super(State, self).save(*args, **kwargs)

    def __str__(self):
        return self.state


class Radius(models.Model):
    value = models.CharField(max_length=200)
    state = models.OneToOneField(
        State, on_delete=models.CASCADE, related_name='State_Radius', null=False)

    class Meta:
        get_latest_by = 'value'

    def __str__(self):
        return str(self.value)


class District(models.Model):
    district = models.CharField(max_length=500, blank=True, unique=True)
    district_code = models.CharField(max_length=200, blank=True)
    state = models.ForeignKey(
        State, on_delete=models.CASCADE, related_name='district_state', null=True)
    has_blocks = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if self.district:
            self.district = self.district.upper()
        return super(District, self).save(*args, **kwargs)

    def __str__(self):
        return self.district


class Block(models.Model):
    # cannot add unique true coz different cities may have similar block names
    block = models.CharField(max_length=500, blank=True)
    block_code = models.CharField(max_length=200, blank=True, unique=False)
    district = models.ForeignKey(
        District, on_delete=models.CASCADE, related_name='block_district')

    class Meta:
        unique_together = [['district', 'block']]

    def save(self, *args, **kwargs):
        if self.block:
            self.block = self.block.upper()
        return super(Block, self).save(*args, **kwargs)

    def __str__(self):
        return self.block


class User(AbstractUser):
    farmer = 1
    ado = 2
    block_admin = 3
    dda = 4
    state_admin = 5
    super_admin = 6
    farmer_ecom = 7
    industry_ecom = 8
    ROLE_CHOICES = (
        (farmer, 'farmer'),
        (ado, 'ado'),
        (block_admin, 'block_admin'),
        (dda, 'dda'),
        (state_admin, 'state_admin'),
        (super_admin, 'super_admin'),
        (farmer_ecom, 'farmer_ecom'),
        (industry_ecom, 'industry_ecom')

    )

    name = models.CharField(max_length=16, blank=True, default='')
    age = models.IntegerField(blank=True, default='1')
    role = models.IntegerField(choices=ROLE_CHOICES, blank=False, null=False)
    phone_number = models.CharField(max_length=10, blank=True, default='')
    address = models.CharField(max_length=128, blank=True, default='')
    image = models.ImageField(
        upload_to='profile_images/', default='profile_images/default.png', null=False)
    state = models.ForeignKey(
        State, on_delete=models.CASCADE, null=True, related_name='user_state')
    email = models.EmailField(blank=False, null=False)
    REQUIRED_FIELDS = ['role', 'email']

    def create_User(self, role, username, password, email):
        print(username)
        user = User.objects.create(
            username=username, password=password, email=email, role=role)
        user.save()
        return(user)

    def get_users_role(self, role):
        user = User.objects.filter(role=role)
        return(user)

    def get_user(self, username, password):
        user = User.objects.get(username=username, password=password)
        return(user)

    def get_connections(self):
        if self.role == 7 or self.role == 8:
            if self.role == 8:
                return self.get_industry_connections()
            return self.get_farmer_connections()

    def get_industry_connections(self):
        if self.role == 7 or self.role == 8:
            connections = set()

            orders = Order.objects.filter(machine__owner=self)
            for order in orders:
                if order.status == Order.ACCEPTED:
                    connections.add(order.customer)

            rent_orders = RentOrder.objects.filter(machine__owner=self)
            for rent_order in rent_orders:
                if rent_order.status == RentOrder.ACCEPTED:
                    connections.add(rent_order.customer)

            residues_orders = ResidueOrder.objects.filter(customer=self)
            for residue_order in residues_orders:
                if residue_order.status == ResidueOrder.ACCEPTED:
                    connections.add(residue_order.residue.owner)

            return connections

    def get_farmer_connections(self):
        if self.role == 7 or self.role == 8:
            connections = set()

            orders = Order.objects.filter(customer=self)
            for order in orders:
                if order.status == Order.ACCEPTED:
                    connections.add(order.machine.owner)

            rent_orders = RentOrder.objects.filter(customer=self)
            for rent_order in rent_orders:
                if rent_order.status == RentOrder.ACCEPTED:
                    connections.add(rent_order.machine.owner)

            rent_orders = RentOrder.objects.filter(machine__owner=self)
            for rent_order in rent_orders:
                if rent_order.status == RentOrder.ACCEPTED:
                    connections.add(rent_order.customer)

            residues_orders = ResidueOrder.objects.filter(residue__owner=self)
            for residue_order in residues_orders:
                if residue_order.status == ResidueOrder.ACCEPTED:
                    connections.add(residue_order.customer)

            return connections

    def __str__(self):
        return self.username


class ado(models.Model):
    role = 2
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    district = models.ForeignKey(
        District, on_delete=models.CASCADE, related_name='ado_district')
    #village = models.ManyToManyField(Village,blank= True, default='')
    # dda = models.ForeignKey(dda, on_delete = models.CASCADE, blank = True, null = True,default='',related_name='ado_dda')

    def create_ado_profile(self, user):
        if user.role == self.role:
            new_ado = ado.objects.create(user=user)
            new_ado.save()
            return new_ado
        else:
            return {"Error": "Invalid Authentication"}

    def __str__(self):
        return self.user.username


class Village(models.Model):
    village = models.CharField(max_length=500, blank=True, unique=False)
    village_code = models.CharField(max_length=200, blank=True, unique=False)
    village_subcode = models.CharField(max_length=200, blank=True)
    block = models.ForeignKey(
        Block, on_delete=models.CASCADE, related_name='village_block')  # null=True
    ado = models.ForeignKey(ado, on_delete=models.CASCADE,
                            blank=True, null=True, related_name='village_ado')

    def save(self, *args, **kwargs):
        if self.village:
            self.village = self.village.upper()
        return super(Village, self).save(*args, **kwargs)

    def __str__(self):
        return self.village


class farmer(models.Model):
    role = 1
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    subsidies = models.CharField(max_length=64, blank=True)
    #murabba_number = models.CharField(max_length=64,blank= True)
    farmer_code = models.CharField(max_length=64, blank=True)
    #khasra_number = models.CharField(max_length=64,blank=True)
    fathers_name = models.CharField(max_length=64, blank=True)
    farmer_code_status = models.BooleanField(default=True)
    #village = models.ForeignKey(Village, on_delete=models.CASCADE,null =True)

    def create_farmer_profile(self, user):
        if user.role == self.role:
            new_farmer = farmer.objects.create(user=user)
            new_farmer.save()
            return new_farmer
        else:
            return {"Error": "Invalid Authentication"}

    def __str__(self):
        return self.user.username

class farmer_ecom(models.Model):
    role = 7
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    def create_farmer_ecom_profile(self, user):
        if user.role == self.role:
            new_farmer = farmer_ecom.objects.create(user=user)
            new_farmer.save()
            return new_farmer
        else:
            return {"Error": "Invalid Authentication"}

    def __str__(self):
        return self.user.username    

class industry_ecom(models.Model):
    role = 8
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    def create_industry_ecom_profile(self, user):
        if user.role == self.role:
            new_industry = industry_ecom.objects.create(user=user)
            new_industry.save()
            return new_industry
        else:
            return {"Error": "Invalid Authentication"}

    def __str__(self):
        return self.user.username    


class dda(models.Model):
    role = 4
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    district = models.OneToOneField(District, on_delete=models.CASCADE,
                                    null=True, blank=True, related_name="dda_district")  # add dda_district

    def create_dda_profile(self, user):
        if self.user.role == self.role:
            new_dda = dda.objects.create(user=user)
            new_dda.save()
            return new_dda
        else:
            return {"Error": "Invalid Authentication"}

    def save(self, *args, **kwargs):
        if self.user.role == 4:
            print(self)
            return super(dda, self).save(*args, **kwargs)
        else:
            return({"error": "your user has some other role"})

    def __str__(self):
        return self.user.username


class block_admin(models.Model):
    role = 3
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    block = models.OneToOneField(Block, on_delete=models.CASCADE, null=True)

    def create_block_admin_profile(self, user):
        if user.role == self.role:
            new_block_admin = block_admin.objects.create(user=user)
            new_block_admin.save()
            return new_block_admin
        else:
            return {"Error": "Invalid Authentication"}

    def __str__(self):
        return self.user.username


class state_admin(models.Model):
    role = 5
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='StateAdminUser')
    state = models.OneToOneField(
        State, on_delete=models.CASCADE, null=True, related_name='admin_state')

    def create_state_admin_profile(self, user):
        if user.role == self.role:
            new_state_admin = state_admin.objects.create(user=user)
            new_state_admin.save()
            return new_state_admin
        else:
            return {"Error": "Invalid Authentication"}

    def __str__(self):
        return self.user.username


class super_admin(models.Model):
    role = 6
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def create_super_admin_profile(self, user):
        if user.role == self.role:
            new_super_admin = super_admin.objects.create(user=user)
            new_super_admin.save()
            return new_super_admin
        else:
            return {"Error": "Invalid Authentication"}


class NormalUserReport(models.Model):
    name = models.CharField(null=False, max_length=30)
    phone_number = models.CharField(max_length=10, blank=False, default='')
    longitude = models.CharField(max_length=100, null=False, default='')
    latitude = models.CharField(max_length=100, null=False, default='')


class ImageNormalUserReport(models.Model):
    NormalUserReport = models.ForeignKey(
        NormalUserReport, on_delete=models.CASCADE, related_name='normal_user_reported_image')
    image = models.ImageField(upload_to='NormalUserReportImages/')


class location(models.Model):
    # state = models.ForeignKey(State, on_delete = models.CASCADE, blank = True,null=True, default = None, related_name = 'location_state')
    district = models.ForeignKey(District, on_delete=models.CASCADE,
                                 blank=True, null=True, related_name='location_district')
    # block_name = models.ForeignKey(Block, on_delete = models.CASCADE, blank = True,null=True, default = None, related_name = 'location_block')
    village_name = models.ForeignKey(
        Village, on_delete=models.CASCADE, blank=True, null=True, related_name='location_village')
    longitude = models.CharField(max_length=100, blank=False, unique=False)
    latitude = models.CharField(max_length=100, blank=False, unique=False)
    acq_date = models.DateField(default=timezone.now)
    acq_time = models.TimeField(default=timezone.now)
    dda = models.ForeignKey(dda, on_delete=models.CASCADE,
                            blank=True, null=True, related_name='location_dda')
    ado = models.ForeignKey(ado, on_delete=models.CASCADE,
                            blank=True, null=True, related_name='location_ado')
    #previous_ado = models.ForeignKey(ada, on_delete = models.CASCADE, blank = True, null = True, default = None, related_name = 'location_ado_previous')
    status = models.CharField(
        max_length=10, choices=choices_status, default='pending')
    created_on = models.DateField(default=timezone.now)
    source = models.ForeignKey(
        NormalUserReport, on_delete=models.CASCADE, null=True)

    def __str__(self):
        if self.district:
            return self.district.district + ' ' + self.district.state.state
        return 'Location('+str(self.id)+')'


class AdoReport(models.Model):
    #village_code = models.CharField(max_length = 50, blank = True, null = True, unique = False)
    # village = models.ForeignKey(Village, on_delete = models.CASCADE, blank = True, null = True, default = None, related_name = 'report_village')#location has village in it
    #farmer = models.ForeignKey(farmer, on_delete = models.CASCADE, blank = True, null = True, default = None, related_name = 'report_farmer')
    location = models.OneToOneField(
        location, on_delete=models.CASCADE, null=True)
    farmer_code = models.CharField(
        max_length=50, blank=True, unique=False, default="")
    farmer_name = models.CharField(
        max_length=50, blank=True, unique=False, default="")
    father_name = models.CharField(
        max_length=50, blank=True, unique=False, default="")
    # longitude = models.CharField(max_length = 100, blank = True, null = True, unique = False)these will be in location
    #latitude = models.CharField(max_length = 100, blank = True, null = True, unique = False)
    report_longitude = models.CharField(max_length=200, blank=True, default="")
    report_latitude = models.CharField(max_length=100, blank=True, default="")

    kila_num = models.CharField(
        max_length=50, blank=True, default="", unique=False)
    murrabba_num = models.CharField(
        max_length=50, blank=True, default="", unique=False)
    khasra_number = models.CharField(max_length=64, blank=True, default="")
    incident_reason = models.CharField(
        max_length=500, blank=True, default="", unique=False)
    remarks = models.CharField(
        max_length=500, blank=True, default="", unique=False)
    amount = models.CharField(
        max_length=500, blank=True, default="", unique=False)
    ownership = models.CharField(
        max_length=250, blank=True, default="", unique=False)
    action = models.CharField(
        max_length=50, choices=actions, blank=True, unique=False, default='FIR')
    fir = models.BooleanField(default=False, blank=True)
    challan = models.BooleanField(default=False, blank=True)
    flag = models.CharField(max_length=50, choices=flags,
                            blank=True, default="", unique=False)
    fire = models.CharField(
        max_length=30, choices=fire_choice, blank=True, default="")
    created_on_ado = models.DateTimeField(default=timezone.now)

    def __str__(self):
        if self.location.village_name != None:
            return self.location.village_name.village+' report'
        return 'AdoReport('+str(self.id)+')'


class Image(models.Model):
    report = models.ForeignKey(AdoReport, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/')
# new


class DC(models.Model):
    name = models.CharField(max_length=200, blank=True, default="")
    email = models.CharField(max_length=100, blank=True, default="",
                             validators=[RegexValidator(regex='^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$', message='Email not valid')])
    district = models.ForeignKey(
        District, on_delete=models.CASCADE, blank=True, null=True, related_name='dc_district')

    def __str__(self):
        return str(self.name)


class SP(models.Model):
    name = models.CharField(max_length=200, blank=True, default="")
    email = models.CharField(max_length=100, blank=True, default="",
                             validators=[RegexValidator(regex='^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$', message='Email not valid')])

    def __str__(self):
        return str(self.name)


def path_file_name(instance, filename):
    return '/'.join(filter(None, ("firedata", instance.date.strftime("%Y-%m-%d"), "harsac", "file.xlsx")))


def path_file_name_one(instance, filename):
    return '/'.join(filter(None, ("firedata", instance.date.strftime("%Y-%m-%d"), "modis", "file.csv")))


def path_file_name_two(instance, filename):
    return '/'.join(filter(None, ("firedata", instance.date.strftime("%Y-%m-%d"), "viirs_npp1", "file.csv")))


def path_file_name_three(instance, filename):
    return '/'.join(filter(None, ("firedata", instance.date.strftime("%Y-%m-%d"), "viirs_noaa", "file.csv")))
# Model to store the data files to be compared.


class CompareData(models.Model):
    date = models.DateField()
    harsac_file = models.FileField(upload_to=path_file_name)
    modis_file = models.FileField(upload_to=path_file_name_one)
    viirs_npp1_file = models.FileField(upload_to=path_file_name_two)
    viirs_noaa_file = models.FileField(upload_to=path_file_name_three)

    def __str__(self):
        return str(self.date)


class NASALocationData(models.Model):
    state = models.CharField(max_length=100, blank=True, null=True)
    district = models.CharField(max_length=100, blank=True, null=True)
    block_name = models.CharField(max_length=100, blank=True, null=True)
    village_name = models.CharField(max_length=100, blank=True, null=True)
    longitude = models.CharField(max_length=100, blank=False, unique=False)
    latitude = models.CharField(max_length=100, blank=False, unique=False)
    acq_date = models.DateField(default=timezone.now)
    acq_time = models.TimeField(default=timezone.now)
    satellite = models.CharField(max_length=100, blank=False, unique=False)


class LocationGeoData(models.Model):
    location = models.OneToOneField(
        location, on_delete=models.CASCADE, null=False, related_name='geo_data')
    murrabba_num = models.CharField(
        max_length=50, blank=True, default="", unique=False)
    khasra_number = models.CharField(max_length=64, blank=True, default="")
    ownership = models.CharField(
        max_length=2000, blank=True, default="", unique=False)
