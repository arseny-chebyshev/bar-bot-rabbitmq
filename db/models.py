import json
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models
from manage import init_django

init_django()
# Create your models here.
class Dish(models.Model):
    name = models.CharField(max_length=255)
    price = models.FloatField(max_length=255)

    def __str__(self) -> str:
        return f"{self.name}, {self.price}"

class Guest(models.Model):
    id = models.BigIntegerField(primary_key=True, null=False, blank=False)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=50)
    debt = models.FloatField(default=0.0)

    def __str__(self) -> str:
        return f"{self.name}, {self.debt}"

class Order(models.Model):
    dish = models.ManyToManyField(to='Dish', through='DishQuantity', related_name='orders_with_dish')
    guest = models.ForeignKey(to=Guest, related_name='orders_from_guest', on_delete=models.DO_NOTHING)
    is_ready = models.BooleanField(default=False)
    total = models.FloatField(null=True, blank=True)
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.id} {self.guest.name}, {self.total}, {'ГОТОВ' if self.is_ready else 'НЕ ГОТОВ'}"
        
    def get_summary(self):
        total = self.dish.all().aggregate(total=models.Sum('price'))
        return total['total']

    def save(self, *args, **kwargs):
        self.guest.debt += self.total
        self.guest.save()
        super(Order, self).save(*args, **kwargs)



class DishQuantity(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.dish}: {self.quantity}"

@receiver(post_save, sender=Order)
def send_notification(sender, instance, created, **kwargs):
    pass