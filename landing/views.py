from django.views.generic import TemplateView


class HomeView(TemplateView):
    """Главная страница лендинга."""
    template_name = 'landing/home.html'


class AboutView(TemplateView):
    """Страница о заведении на лендинге."""
    template_name = 'landing/about.html'


class PricingView(TemplateView):
    """Страница с ценами/тарифами."""
    template_name = 'landing/pricing.html'


class RulesView(TemplateView):
    """Страница правил посещения."""
    template_name = 'landing/rules.html'
