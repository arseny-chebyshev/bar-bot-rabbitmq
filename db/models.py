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
    name = models.CharField(max_length=255)
    
    def __str__(self) -> str:
        return self.name

class Order(models.Model):
    dish = models.ManyToManyField(to='Dish', related_name='orders_with_dish')
    guest = models.ForeignKey(to=Guest, related_name='orders_from_guest', on_delete=models.DO_NOTHING)
    is_ready = models.BooleanField(default=False)
    total = models.FloatField(null=True, blank=True)
    
    def __str__(self) -> str:
        return f"{self.guest.name}, {self.total}, {'ГОТОВ' if self.is_ready else 'НЕ ГОТОВ'}"
        
    def get_summary(self):
        total = self.dish.all().aggregate(total=models.Sum('price'))
        return total['total']
    
    def save(self, *args, **kwagrs):
        self.summary = self.get_summary()
        return super(Order, self).save()
