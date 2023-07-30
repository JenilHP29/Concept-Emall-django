from django.db import models
from ckeditor.fields import RichTextField
from django.utils.text import slugify
from django.db.models.signals import pre_save

# Create your models here.
class slider(models.Model):

    DISCOUNT_DEALS = (
        ("HOT DEALS","HOT DEALS"),
        ("New Arrivals","New Arrivals"),
    )

    Image = models.ImageField(upload_to='media/slider_imgs')
    Discount_Deal = models.CharField(choices=DISCOUNT_DEALS,max_length=100)
    SALE = models.IntegerField()
    Brand_Name = models.CharField(max_length=200)
    Discount = models.IntegerField()
    Link = models.CharField(max_length=200)

    def __str__(self):
        return self.Brand_Name
    
        
class banner_area(models.Model):
    Image = models.ImageField(upload_to='media/banner_img')
    Tags = models.CharField(max_length=100)
    Quote = models.CharField(max_length=100)
    Discount_Deal = models.CharField(max_length=200)
    Link = models.CharField(max_length=200,null=True)

    def __str__(self):
        return self.Quote

class Main_Category(models.Model):
    Name = models.CharField(max_length=100)

    def __str__(self):
        return self.Name
    
class Category(models.Model):
    main_category = models.ForeignKey(Main_Category,on_delete=models.CASCADE)
    Name = models.CharField(max_length=100)

    def __str__(self):
        return self.main_category.Name +" -- "+self.Name
    
class Sub_Category(models.Model):
    category = models.ForeignKey(Category,on_delete=models.CASCADE)
    Name = models.CharField(max_length=100)

    def __str__(self):
        return self.category.main_category.Name + " -- " +self.category.Name+" -- "+ self.Name
    
class Section(models.Model):
    Name = models.CharField(max_length=100)

    def __str__(self):
        return self.Name

class Color(models.Model):
    code = models.CharField(max_length=100)

    def __str__(self):
        return self.code
    
class Brand(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Product(models.Model):
    total_quantity = models.IntegerField()
    availability = models.IntegerField()
    featured_Image = models.CharField(max_length=500)
    product_Name = models.CharField(max_length=100)
    brand = models.ForeignKey(Brand,on_delete=models.CASCADE,null=True)
    price = models.IntegerField()
    discount = models.IntegerField()
    tax = models.IntegerField(null=True)
    packing_cost = models.IntegerField(null=True)
    product_Information = RichTextField()
    model_Name = models.CharField(max_length=100)    
    categories = models.ForeignKey(Category,on_delete=models.CASCADE)
    color = models.ForeignKey(Color,on_delete=models.CASCADE,null=True)
    tags = models.CharField(max_length=100)
    description = RichTextField()
    section = models.ForeignKey(Section,on_delete=models.DO_NOTHING)
    slug = models.SlugField(default='', max_length=500, null=True, blank=True)

    def __str__(self):
        return self.product_Name
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse("product_detail", kwargs={'slug': self.slug})

    class Meta:
        db_table = "app_Product"

def create_slug(instance, new_slug=None):
    slug = slugify(instance.product_Name)
    if new_slug is not None:
        slug = new_slug
    qs = Product.objects.filter(slug=slug).order_by('-id')
    exists = qs.exists()
    if exists:
        new_slug = "%s-%s" % (slug, qs.first().id)
        return create_slug(instance, new_slug=new_slug)
    return slug

def pre_save_post_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_slug(instance)

pre_save.connect(pre_save_post_receiver, Product)

class Coupon_Code(models.Model):
    code = models.CharField(max_length=100)
    discount = models.IntegerField()

    def __str__(self):
        return self.code
    
class Product_Image(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    image_url = models.CharField(max_length=500)

class Additional_Information(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    specification =models.CharField(max_length=100)
    detail = models.CharField(max_length=100)
