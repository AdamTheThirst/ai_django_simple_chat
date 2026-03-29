from django.db import models


class Message(models.Model):
    ROLE_USER = 'user'
    ROLE_AI = 'ai'

    ROLE_CHOICES = [
        (ROLE_USER, 'Пользователь'),
        (ROLE_AI, 'AI'),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at', 'id']

    def __str__(self):
        return f'{self.created_at.isoformat()} [{self.role}] {self.content[:40]}'
