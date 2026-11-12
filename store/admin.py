from django.contrib import admin
from .models import Product , Variations , ReviewRatings , ProductGallery
import admin_thumbnails

# Register your models here.
@admin_thumbnails.thumbnail('image')
class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 1 

class ProductAdmin(admin.ModelAdmin):
    list_display = ['product_name','price', 'stock', 'category' , 'modified_date' ,'is_available']
    prepopulated_fields = {'slug':('product_name',)}
    inlines = [ProductGalleryInline]

class VariationsAdmin(admin.ModelAdmin):
    list_display = ['product','variations_category', 'variation_value', 'is_active' , 'created_date']
    list_editable = ['is_active']
    list_filter = ['product','variations_category','variation_value' ]


admin.site.register(Product, ProductAdmin)
admin.site.register(Variations, VariationsAdmin) 
admin.site.register(ReviewRatings)
admin.site.register(ProductGallery)