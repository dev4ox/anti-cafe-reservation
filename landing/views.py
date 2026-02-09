from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = 'landing/home.html'


class AboutView(TemplateView):
    template_name = 'landing/about.html'


class PricingView(TemplateView):
    template_name = 'landing/pricing.html'


class RulesView(TemplateView):
    template_name = 'landing/rules.html'
