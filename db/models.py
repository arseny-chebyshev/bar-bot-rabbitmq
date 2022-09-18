import json
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models
from manage import init_django

init_django()
# Create your models here.
class Dish(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(decimal_places=2, max_digits=8)
    
    def get_summary(self):
        dish_quant = DishQuantity.objects.filter(dish=self).aggregate(total=models.Sum('quantity'))
        return dish_quant['total']

    def __str__(self) -> str:
        return f"{self.name}, {self.price}LKR"
    class Meta:
        ordering = ['id']

class Guest(models.Model):
    id = models.BigIntegerField(primary_key=True, null=False, blank=False)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=50)
    username = models.CharField(blank=True, null=True, max_length=255)
    debt = models.DecimalField(decimal_places=2, max_digits=8, default=0)

    def __str__(self) -> str:
        return f"{self.name}, кредит: {self.debt}LKR"

class Order(models.Model):
    dish = models.ManyToManyField(to='Dish', through='DishQuantity', related_name='orders_with_dish')
    guest = models.ForeignKey(to=Guest, related_name='orders_from_guest', on_delete=models.DO_NOTHING)
    is_ready = models.BooleanField(default=False)
    total = models.DecimalField(decimal_places=2, max_digits=8, default=0)
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.id} {self.guest.name}, {self.total}LKR, {'ГОТОВ' if self.is_ready else 'НЕ ГОТОВ'}"
        
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
