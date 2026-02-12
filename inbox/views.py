from django.contrib import messages
from django.shortcuts import redirect, render

from integrations.telegram import send_telegram_message

from .forms import ContactForm


def contact(request):
    """Обрабатывает страницу контактов и сохраняет сообщения клиентов."""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            message = form.save()
            send_telegram_message(
                f'Новое сообщение: {message.name}, телефон: {message.phone}, '
                f'сообщение: {message.message}'
            )
            messages.success(request, 'Спасибо! Мы свяжемся с вами.')
            return redirect('inbox:contact')
    else:
        form = ContactForm()

    return render(request, 'inbox/contact.html', {'form': form})
