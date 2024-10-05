from django.db import models
from posts.models import Category
from members.models import Member

class Purchase(models.Model):
    user = models.ForeignKey(Member, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"El usuario \"{self.user}\" compró la categoría \"{self.category}\" por ${self.price} en la fecha y hora {self.date}"