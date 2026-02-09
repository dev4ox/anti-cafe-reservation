from django.db import models


class BoardGame(models.Model):
    title = models.CharField('Название', max_length=200)
    description = models.TextField('Описание', blank=True)
    players_min = models.PositiveIntegerField('Игроков минимум', null=True, blank=True)
    players_max = models.PositiveIntegerField('Игроков максимум', null=True, blank=True)
    play_time_min = models.PositiveIntegerField('Длительность (мин.)', null=True, blank=True)
    age = models.PositiveIntegerField('Возраст', null=True, blank=True)
    image = models.ImageField('Изображение', upload_to='games/', blank=True)
    is_available = models.BooleanField('Доступна', default=True)

    class Meta:
        verbose_name = 'Настольная игра'
        verbose_name_plural = 'Настольные игры'

    def __str__(self) -> str:
        return self.title


class Product(models.Model):
    title = models.CharField('Название', max_length=200)
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    description = models.TextField('Описание', blank=True)
    image = models.ImageField('Изображение', upload_to='products/', blank=True)
    is_available = models.BooleanField('Доступен', default=True)

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'

    def __str__(self) -> str:
        return self.title
