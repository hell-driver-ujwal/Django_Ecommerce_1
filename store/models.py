from django.db import models
from category.models import Category
from django.urls import reverse
# Create your models here.


class Product(models.Model):
    product_name    = models.CharField(max_length= 255, unique= True)
    slug            = models.SlugField(max_length= 255, unique= True)
    description     = models.TextField(max_length= 500, blank= True)
    price           =models.IntegerField()
    images          =models.ImageField(upload_to='photos/products')
    stock           =models.IntegerField()
    is_available    =models.BooleanField(default= True)
    category        =models.ForeignKey(Category, on_delete= models.CASCADE)
    created_date    =models.DateTimeField(auto_now_add= True)
    modified_date   =models.DateTimeField(auto_now= True)


    def get_url(self):
        return reverse('product_detail', args=[self.category.slug, self.slug])
    
    def __str__(self):
        return self.product_name

class ProductVariations(models.Model):
    product = models.ForeignKey(Product, 
            on_delete=models.CASCADE,
            related_name= 'variants')
    
    color = models.CharField(max_length= 50)
    size = models.CharField(max_length= 50)

    stock = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                field =['product', 'color', 'size'],
                name = 'unique_product_color_size'
            )
        ]


