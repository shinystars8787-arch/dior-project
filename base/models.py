from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify


class Category(models.Model):
    CATEGORY_CHOICES = [
        ('shoes', 'Shoes'),
        ('perfumes', 'Perfumes'),
        ('makeup', 'Makeup'),
        ('skincare', 'Skincare'),
    ]

    name = models.CharField(max_length=100, choices=CATEGORY_CHOICES, unique=True, verbose_name='Category Name')
    slug = models.SlugField(max_length=100, unique=True, blank=True, verbose_name='Slug')
    image = models.ImageField(upload_to='categories/', null=True, blank=True, verbose_name='Category Image')

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.get_name_display()


class SubCategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories', verbose_name='Main Category')
    name = models.CharField(max_length=100, verbose_name='Subcategory Name')
    slug = models.SlugField(max_length=100, unique=True, blank=True, verbose_name='Slug')

    class Meta:
        verbose_name = 'Subcategory'
        verbose_name_plural = 'Subcategories'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.category.get_name_display()} - {self.name}"


class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name='Product Name')
    slug = models.SlugField(max_length=255, unique=True, blank=True, verbose_name='Slug')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name='Category')
    subcategory = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='products', verbose_name='Subcategory')
    
    description = models.TextField(blank=True, null=True, verbose_name='Description')
    
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Price ($)')
    old_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Old Price ($)')
    
    main_image = models.ImageField(upload_to='products/', null=True, blank=True, verbose_name='Main Image')
    
    in_stock = models.BooleanField(default=True, verbose_name='In Stock')
    is_featured = models.BooleanField(default=False, verbose_name='Featured Product')
    is_new = models.BooleanField(default=False, verbose_name='New Arrival')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name='Product')
    image = models.ImageField(upload_to='products/gallery/', verbose_name='Image')
    alt_text = models.CharField(max_length=100, blank=True, null=True, verbose_name='Alt Text')

    class Meta:
        verbose_name = 'Product Image'
        verbose_name_plural = 'Product Images'

    def __str__(self):
        return f"Image for {self.product.name}"


class HomepageSection(models.Model):
    SECTION_CHOICES = [
        ('shoes', 'Footwear Section'),
        ('perfumes', 'Fragrance Section'),
        ('skincare', 'Skincare Section'),
        ('makeup', 'Makeup Section'),
    ]
    
    section_name = models.CharField(max_length=50, choices=SECTION_CHOICES, unique=True, verbose_name='Section')
    
    big_title = models.CharField(max_length=100, blank=True, null=True, verbose_name='Big Title')
    subtitle = models.CharField(max_length=100, blank=True, null=True, verbose_name='Subtitle')
    description = models.TextField(blank=True, null=True, verbose_name='Description')
    section_image = models.ImageField(upload_to='sections/', null=True, blank=True, verbose_name='Section Background Image')

    product_1 = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name='section_product_1', verbose_name='Product 1')
    product_2 = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name='section_product_2', verbose_name='Product 2')

    class Meta:
        verbose_name = 'Homepage Section'
        verbose_name_plural = 'Homepage Sections'

    def __str__(self):
        return self.get_section_name_display()


class HomepageContent(models.Model):
    hero_background = models.ImageField(upload_to='homepage/', null=True, blank=True, verbose_name='Hero Background Image')
    hero_title = models.CharField(max_length=100, null=True, blank=True, verbose_name='Hero Title')
    hero_subtitle = models.CharField(max_length=200, null=True, blank=True, verbose_name='Hero Subtitle')

    class Meta:
        verbose_name = 'Homepage Hero Content'
        verbose_name_plural = 'Homepage Hero Content'

    def __str__(self):
        return "Homepage Hero Settings"


class User(AbstractUser):
    email = models.EmailField(unique=True, verbose_name='Email Address')
    phone = models.CharField(max_length=15, blank=True, null=True, verbose_name='Phone Number')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name='User')
    session_key = models.CharField(max_length=40, null=True, blank=True, verbose_name='Session Key')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')

    class Meta:
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'

    def __str__(self):
        if self.user:
            return f"Cart for {self.user.username}"
        return f"Cart (Session: {self.session_key})"

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items', verbose_name='Cart')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Product')
    quantity = models.PositiveIntegerField(default=1, verbose_name='Quantity')

    class Meta:
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def total_price(self):
        return self.product.price * self.quantity