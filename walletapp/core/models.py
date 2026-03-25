from django.conf import settings
from django.db import models
from django.utils import timezone

class SoftDeleteQuerySet(models.QuerySet):
    """
    Custom QuerySet that overrides the delete method to perform a soft delete.
    Instead of deleting records from the database, it updates the `is_deleted` field to True
    """

    def delete(self):
        return super().update(
            is_deleted=True,
            deleted_at=timezone.now(),
        )

    def restore(self):
        return super().update(is_deleted=True, deleted_at=None)

    def hard_delete(self):
        return super().delete()

    def alive(self):
        return self.filter(is_deleted=False)

    def deleted(self):
        return self.filter(is_deleted=True)


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).alive()

    def all_with_deleted(self):
        return SoftDeleteQuerySet(self.model, using=self._db)

    def deleted_only(self):
        return SoftDeleteQuerySet(self.model, using=self._db).deleted()

class BaseSoftDeleteModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_created",
    )

    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_updated"
    )

    delete_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="%(app_label)s_%(class)s_deleted",
    )

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True
    
    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.delete_by = (
            self.updated_by
        )
        self.save(update_fields=["is_deleted", "deleted_at", "delete_by"])

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.delete_by = None
        self.save(update_fields=["is_deleted", "deleted_at", "delete_by"])

    def hard_delete(self, using=None, keep_parents=False):
        super().delete(using=using, keep_parents=keep_parents)