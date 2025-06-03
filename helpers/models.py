import uuid
from django.db import models


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_by = models.ForeignKey(
        "accounts.CustomUser",
        on_delete=models.DO_NOTHING,
        null=True,
        # Use unique related name for created_by
        related_name="created_%(class)s_set",
    )
    last_updated_by = models.ForeignKey(
        "accounts.CustomUser",
        on_delete=models.DO_NOTHING,
        null=True,
        # Use unique related name for last_updated_by
        related_name="updated_%(class)s_set",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]

        