from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
# from . import views
from users import views

urlpatterns = [
    #     path('api/register/', views.user_create.as_view(), name='register'),
    #     path('api/login/', views.user_login.as_view(), name='login'),
    # path('api/profile/', views.user_profile.as_view(), name='profile'),
    # path('api/state/', views.state.as_view(), name='add_state'),
    # path('api/district/<int:state_id>/', views.district.as_view(), name='add_district'),
    # path('api/block/<int:district_id>/', views.block.as_view(), name='add_block'),
    # path('api/village/<int:block_id>/', views.village.as_view(), name='add_village'),


    path('api/user/', views.UserList.as_view(), name='user-list'),

    path('api/get-user/', views.GetUser.as_view(), name='get-user'),
    path('api/user/<int:pk>/', views.UserDetail.as_view(), name='user-detail'),

    path('api/state/', views.StateList.as_view(), name='state-list'),
    path('api/state/<int:pk>/', views.StateDetail.as_view(), name='state-detail'),

    path('api/district/', views.DistrictList.as_view(),
         name='district-list'),  # new state wise districts added
    path('api/district/<int:pk>/',
         views.DistrictDetail.as_view(), name='district-detail'),
    path('api/district-list/',
         views.DistrictViewSet.as_view({'get': 'list'}), name='district-list'),

    path('api/block/', views.BlockList.as_view(),
         name='block-list'),  # new state wise blocks added
    path('api/block/<int:pk>/', views.BlockDetail.as_view(), name='block-detail'),
    path('api/blocks-list/district/<int:pk>/',
         views.BlocksDistrictWiseViewSet.as_view({'get': 'list'}), name='block-district-list'),

    path('api/village/', views.VillageList.as_view(),
         name='village-view'),  # new state wise village added
    path('api/village/<int:pk>/',
         views.VillageDetail.as_view(), name='village-detail'),
    path('api/villages-list/', views.VillageViewSet.as_view(
        {'get': 'list'}), name='village-list'),  # should i add or not??
    path('api/users-list/admin/',
         views.AdminViewSet.as_view({'get': 'list'}), name='admin-list'),
    path('api/users-list/dda/',
         views.DdaViewSet.as_view({'get': 'list'}), name='dda-list'),
    # added state wise
    path('api/users-list/ado/',
         views.AdosViewSet.as_view({'get': 'list'}), name='ado-list'),
    path('api/users-list/ado/<int:pk>',
         views.Adoddalist.as_view({'get': 'list'}), name='adodda-list'),
    path('api/user/dda/', views.DDAList.as_view(),
         name='user-list-dda'),  # state added

    path('api/villages-list/district/<int:pk>/',
         views.VillagesDistrictWiseViewSet.as_view({'get': 'list'}), name='village-district-list'),

    path('api/upload/locations/', views.LocationList.as_view(),
         name='upload-locations'),

    # Appversion
    path('api/checkVersion/', views.CheckVersion.as_view(), name='checkVersion'),
    # mail
    path('api/upload/mail/', views.MailView.as_view(),
         name='upload-fir-csv'),  # to be tested
    path('api/location/<int:pk>/',
         views.LocationDetail.as_view(), name='location-detail'),

    path('api/locations/<str:status>', views.LocationViewSet.as_view(
        {'get': 'list'}), name='admin-location-list'),  # state added to this
    path('api/locations/ado/<str:status>',
         views.LocationViewSetAdo.as_view({'get': 'list'}), name='ado-location-list'),
    path('api/locations/dda/<str:status>',
         views.LocationViewSetDda.as_view({'get': 'list'}), name='dda-location-list'),
    path('api/admin/ado/<int:pk>/<str:status>',
         views.LocationViewSetAdoForAdmin.as_view({'get': 'list'}), name='admin-ado-location-list'),
    path('api/admin/dda/<int:pk>/<str:status>',
         views.LocationViewSetDdaForAdmin.as_view({'get': 'list'}), name='admin-dda-location-list'),
    path('api/location/district/<int:pk>/<str:status>',
         views.LocationDistrictWiseViewSet.as_view({'get': 'list'}), name='location-district-location-list'),

    path('api/ado/',
         views.AdoViewSet.as_view({'get': 'list'}), name='ado-list'),

    # Ado report and image views
    path('api/report-ado/<int:pk>/',
         views.AdoReportDetail.as_view(), name='ado-report-detail'),
    path('api/report-ado/add/', views.AddAdoReport.as_view(),
         name='add-ado-report'),  # changes with selenium

    path('api/upload/images/', views.ImagesView.as_view(), name='upload-images'),

    path('api/report/images/<int:pk>/',
         views.ReportImageView.as_view(), name='Report-images'),

    # Bulk add village
    path('api/upload/villages/', views.BulkAddVillage.as_view(),
         name='upload-villages'),  # tested working

    path('api/upload/districts/', views.BulkAddDistrict.as_view(),
         name='upload-districts'),  # tested working
    # Bulk add ado
    path('api/upload/ado/', views.BulkAddAdo.as_view(), name='upload-ado'),  # test
    # Bulk add ado
    path('api/upload/dda/', views.BulkAddDda.as_view(), name='upload-dda'),  # test

    # Trigger sms
    path('api/trigger/sms/<str:status>',
         views.TriggerSMS.as_view(), name='trigger-sms'),  # test


    path('api/ado/csv/', views.GetListAdo.as_view(), name='print-ado'),
    path('api/ado-export-pdf/', views.ExportAdoPdf),
    path('api/count-reports/', views.CountOfReports.as_view()),
    path('api/countReportBtwDates/', views.CountOfReportsbtwdates.as_view()),
    path('api/generate-passwords-ado/', views.GeneratePasswordsForAdo.as_view()),

    path('api/generate-location-report/',
         views.GenerateLocationReport.as_view()),
    path('api/generate-report/', views.GenerateReport.as_view()),


    # path('api/compare-data-file/', views.CompareFireDataReportFile.as_view()),#test

    path('api/Radius/', views.RadiusList.as_view(), name='Radiuslist'),  # new
    path('api/Radius/<str:state>/', views.RadiusDetail.as_view(),
         name='Radiusdetail'),  # new you cant change state but only value
    path('api/report-user/add/', views.AddUserReport.as_view(),
         name='add-normal-user-report'),  # new #tested
    path('api/report-user/images/', views.AddUserReportImage.as_view(),
         name='upload-userReport-images'),  # new
    path('api/upload/locations/map/', views.LocationList_map.as_view(),
         name='upload-locations_map'),  # new tested
    # path('api/long-lat/', views.longlat.as_view(), name='longlat'), #now under location-land-data
    path('api/address/', views.location_data.as_view(),
         name='address_from_long_lat'),  # new but tested

    path('api/change/StateAdmin/', views.StateAdminChange.as_view(),
         name='StateAdminChange'),  # new
    path('api/change/Dda/', views.DDAChange.as_view(), name='DDAChange'),  # new
    path('api/change/Ado/', views.ADOChange.as_view(), name='ADOChange'),
    path('api/change/village/', views.VillageChange.as_view(), name='ADOChange'),
    path('api/NasaData/', views.GetNASAData.as_view(), name='GetNASAData'),
    path('api/compare-data/', views.CompareFireDataReport.as_view()),
    path('api/comparison-report/', views.ComparisonReport.as_view()),
    path('api/location-land-data/',
         views.LocationLandData.as_view(), name='LocationLandData'),
    path('api/reset-password/', views.ResetPass.as_view()),
    path('api/reset-password/<int:uid>/<str:Token>', views.confirmpass.as_view()),
    path('api/change-password/<int:uid>/<str:Token>', views.changepass.as_view()),
    path('api/change-password/<int:uid>/', views.changepassandroid.as_view()),
    path('api/address/<str:lat>/<str:lon>', views.latlong_data.as_view()),
    path('api/update/users', views.multipleuser.as_view()),
    path('api/update/location/<int:pk>', views.Adoassign.as_view()),
]
# urlpatterns = format_suffix_patterns(urlpatterns)location_data
