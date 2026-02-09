from django.db import models


STATUS_NEW = 'NEW'
STATUS_IN_PROGRESS = 'IN_PROGRESS'
STATUS_DONE = 'DONE'

STATUS_CHOICES = [
    (STATUS_NEW, 'Новый'),
    (STATUS_IN_PROGRESS, 'В работе'),
    (STATUS_DONE, 'Готово'),
]


class ContactMessage(models.Model):
    name = models.CharField('Имя', max_length=150)
    phone = models.CharField('Телефон', max_length=50)
    message = models.TextField('Сообщение')
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default=STATUS_NEW)
    created_at = models.DateTimeField('Создано', auto_now_add=True)

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'{self.name} {self.created_at:%Y-%m-%d}'
