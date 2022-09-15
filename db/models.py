import asyncio
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.db import models
from manage import init_django
from admin.utils import notify_admin

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
    phone = models.CharField(max_length=255)

    
    def __str__(self) -> str:
        return f"{self.name}, {self.phone}"

class Order(models.Model):
    dish = models.ManyToManyField(to='Dish', through='DishQuantity', related_name='orders_with_dish')
    guest = models.ForeignKey(to=Guest, related_name='orders_from_guest', on_delete=models.DO_NOTHING)
    is_ready = models.BooleanField(default=False)
    total = models.FloatField(null=True, blank=True)
    
    def __str__(self) -> str:
        return f"{self.id} {self.guest.name}, {self.total}, {'ГОТОВ' if self.is_ready else 'НЕ ГОТОВ'}"
        
    def get_summary(self):
        total = self.dish.all().aggregate(total=models.Sum('price'))
        return total['total']


class DishQuantity(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.dish}: {self.quantity}"

@receiver(pre_save, sender=Order)
def send_notification(sender, instance, **kwargs):
    quantities = []
    for dish in DishQuantity.objects.filter(order=instance):
        print(dish)
        quantities.append(f"{dish.dish.name} x {dish.dish.price} ---- {dish.dish.price * dish.quantity}Р\n")
    text = f"""Привет из models!\nНовый заказ #{instance.id}\n
Заказал: {instance.guest}
Состав: {''.join(quantities)}
Сумма: {instance.total}"""
    asyncio.ensure_future(notify_admin(text))
