from django.db import models
from django.conf import settings
from walletapp.core.models import BaseSoftDeleteModel

class Tag(BaseSoftDeleteModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, 
        related_name="tags"
    )

    name = models.CharField(max_length=50, db_index=True)
    color = models.CharField(max_length=7, default="#0F5DC9")
    
    class Meta:
        unique_together = ("user", "name")
        ordering = ["name"]
    
    def __str__(self):
        return self.name