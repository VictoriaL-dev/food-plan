from django.db import models

class Review(models.Model):
    user_name = models.CharField('Имя автора', max_length=100)
    text = models.TextField('Текст отзыва')
    rating = models.IntegerField('Рейтинг (1-5)', default=5)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'

    def __str__(self):
        return f"Отзыв от {self.user_name}"
