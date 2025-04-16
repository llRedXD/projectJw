from django.db import models


class Session(models.Model):
    name = models.CharField(max_length=255, unique=True)


class Designation(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    session = models.ForeignKey(
        Session, on_delete=models.CASCADE, related_name="designations"
    )

    def __str__(self):
        return self.name
