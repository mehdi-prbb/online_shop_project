from django.db import models


class PublishedCommentsManger(models.Manager):
    def get_queryset(self):
        return super(PublishedCommentsManger, self).get_queryset().all().filter(status='p')