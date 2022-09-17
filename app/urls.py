from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from rest_framework.authtoken import views as auth_views

from app.views import (CartCheckoutView, CartItemView, CartView,
                       ChangePasswordView, Connections, MachineDetailView,
                       Machine_modelsView, Machine_modelsDetailView,
                       MachinesView, OrderDetailView, OrdersView, ProfileView,
                       RentOrderDetailView, RentOrdersView, ResidueDetailView,
                       ResidueOrderDetailView, ResidueOrdersView, ResiduesView,
                       ResidueTypeView, UsersView, registerUser)

urlpatterns = [
    path('register/', registerUser.as_view(), name='register'),
    path('users/<int:pk>', UsersView.as_view(), name='user'),
    path('users/change-password',
         ChangePasswordView.as_view(), name='change-password'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('machines/', MachinesView.as_view(), name='machines'),
    path('machines/<int:pk>', MachineDetailView.as_view(), name='machine'),
    path('machine_models/', Machine_modelsView.as_view(), name='machine_models'),
    path('machine_models/<int:pk>',
         Machine_modelsDetailView.as_view(), name='machine_model'),
    path('residues/', ResiduesView.as_view(), name='residues'),
    path('residues/type', ResidueTypeView.as_view(), name='residue-type'),
    path('residues/<int:pk>', ResidueDetailView.as_view(), name='residue'),
    path('cart/', CartView.as_view(), name='cart'),
    path('cart-items/<int:pk>', CartItemView.as_view(), name='cart-items'),
    path('cart/checkout', CartCheckoutView.as_view(), name='cart-checkout'),
    path('orders/', OrdersView.as_view(), name='orders'),
    path('orders/<int:pk>', OrderDetailView.as_view(), name='order-detail'),
    path('rent-orders/', RentOrdersView.as_view(), name='rent-orders'),
    path('rent-orders/<int:pk>', RentOrderDetailView.as_view(), name='rent-order'),
    path('residue-orders/', ResidueOrdersView.as_view(), name='residue-orders'),
    path('residue-orders/<int:pk>',
         ResidueOrderDetailView.as_view(), name='residue-order'),
    path('connections/', Connections.as_view(), name='connections'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [
    path('token/', auth_views.obtain_auth_token)
]
