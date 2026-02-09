from django.urls import path

from .views import AboutView, HomeView, PricingView, RulesView

app_name = 'landing'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('about/', AboutView.as_view(), name='about'),
    path('pricing/', PricingView.as_view(), name='pricing'),
    path('rules/', RulesView.as_view(), name='rules'),
]
