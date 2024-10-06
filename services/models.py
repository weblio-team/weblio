from django.db import models
from posts.models import Category
from members.models import Member

class Purchase(models.Model):
    """
    Representa una compra realizada por un usuario.

    Atributos:
    ----------
    user : ForeignKey
        Usuario que realizó la compra.
    category : ForeignKey
        Categoría que fue comprada.
    price : DecimalField
        Precio de la categoría comprada.
    date : DateTimeField
        Fecha y hora en que se realizó la compra.

    Métodos:
    --------
    __str__():
        Retorna una representación legible de la compra, incluyendo el usuario, la categoría, el precio y la fecha.
    """
    user = models.ForeignKey(Member, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Retorna una representación legible de la compra, incluyendo el usuario, la categoría, el precio y la fecha.

        Returns:
        --------
        str
            Representación legible de la compra.
        """
        return f"El usuario \"{self.user}\" compró la categoría \"{self.category}\" por ${self.price} en la fecha y hora {self.date}"