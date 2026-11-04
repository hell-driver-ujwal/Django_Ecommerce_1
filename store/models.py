from django.db import models
from category.models import Category
from django.urls import reverse
from accounts.models import Account
# Create your models here.


class Product(models.Model):
    product_name    = models.CharField(max_length= 255, unique= True)
    slug            = models.SlugField(max_length= 255, unique= True)
    description     = models.TextField(max_length= 500, blank= True)
    price           =models.FloatField()
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
    
    # my addition
    # def save(self, *args , **kwargs):
    #     if self.stock <= 0:
    #         self.is_available = False
    #     super().save(*args, **kwargs)

variation_category_choice = (
    ('color','color'),
    ('size', 'size')
)

class VariationsManager(models.Manager):
    def colors(self):
        return super(VariationsManager, self).filter( variations_category = 'color', is_active = True)

    def sizes(self):
        return super(VariationsManager, self).filter( variations_category = 'size', is_active = True) 

class Variations(models.Model):
    product = models.ForeignKey(Product, on_delete= models.CASCADE)
    variations_category = models.CharField(max_length= 100 , choices= variation_category_choice)
    variation_value = models.CharField(max_length= 100)
    is_active = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now= True) 
    objects = VariationsManager()
    
    def __str__(self):
        return f"{self.product.product_name}-{self.variation_value}"    

class ReviewRatings(models.Model):
    product = models.ForeignKey(Product, on_delete= models.CASCADE)
    user = models.ForeignKey(Account, on_delete= models.CASCADE)
    subject = models.CharField(max_length= 100, blank = True)
    review = models.TextField(max_length= 500)
    raiting = models.FloatField()
    ip = models.CharField(max_length=20, blank = True)
    status = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add= True)
    updated_at = models.DateTimeField(auto_now=True)
    is_edited = models.BooleanField(default= False)

    def __str__(self):
        return self.subject
