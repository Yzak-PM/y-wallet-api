from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name or ''}".strip()
    
    def __str__(self):
        return self.email or str(self.pk)