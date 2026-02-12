from django import forms

from .models import ContactMessage


class ContactForm(forms.ModelForm):
    """Форма обратной связи для клиентов."""
    website = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        """Мета-настройки модели или формы."""
        model = ContactMessage
        fields = ['name', 'phone', 'message', 'website']

    def clean_website(self):
        """Проверяет honeypot-поле и блокирует спам-ботов."""
        value = self.cleaned_data.get('website', '')
        if value:
            raise forms.ValidationError('Спам защита сработала.')
        return value
