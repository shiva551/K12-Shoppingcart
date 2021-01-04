from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.shortcuts import reverse

CATEGORY_CHOICES = (
    ('D', 'Dresses'),
    ('W', 'Watches'),
    ('FW', 'Footwear'),
    ('M', 'Mobiles'),
    ('L', 'Laptops')
)

LABEL_CHOICES = (
    ('P', 'primary'),
    ('S', 'secondary'),
    ('D', 'danger')
)

ADDRESS_CHOICES = (
    ('B', 'Billing'),
    ('S', 'Shipping')
)

STATUS_CHOICES = (
    ('N', 'new'),
    ('P', 'paid')
)
MODE_OF_PAYMENT = (
    ('Cash', 'Cash on delivery'),
    ('Paytm', 'Paytm Bank'),
    ('Card', 'Credit/Debit'),
    ('UPI', 'Upi Payments')
)


class UserProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=50, blank=True, null=True)
    one_click_purchasing = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


class Product(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    imageLink = models.ImageField()
    price = models.FloatField()
    createdAt = models.DateField(auto_now_add=True)
    updatedAt = models.DateField(auto_now=True)
    slug = models.SlugField()
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=2)
    label = models.CharField(choices=LABEL_CHOICES, max_length=1)
    discount_price = models.FloatField(blank=True, null=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("core:product", kwargs={
            'slug': self.slug
        })

    def get_add_to_cart_url(self):
        return reverse("core:add-to-cart", kwargs={
            'slug': self.slug
        })

    def get_remove_from_cart_url(self):
        return reverse("core:remove-from-cart", kwargs={
            'slug': self.slug
        })


class Variation(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    class Meta:
        unique_together = (
            ('product', 'name')
        )

    def __str__(self):
        return self.name


class ProductVariation(models.Model):
    variation = models.ForeignKey(Variation, on_delete=models.CASCADE)
    value = models.CharField(max_length=50)
    attachment = models.ImageField(blank=True)

    class Meta:
        unique_together = (
            ('variation', 'value')
        )

    def __str__(self):
        return self.value


class OrderItem(models.Model):
    productId = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    product_variations = models.ManyToManyField(ProductVariation)
    price = models.FloatField()

    def __str__(self):
        return f"{self.quantity} of {self.productId.title}"

    def get_total_product_price(self):
        price = self.quantity * self.productId.price
        return price

    def get_total_discount_product_price(self):
        return self.quantity * self.productId.discount_price

    def get_amount_saved(self):
        return self.get_total_product_price() - self.get_total_discount_product_price()

    def get_final_price(self):
        if self.product.discount_price:
            return self.get_total_discount_product_price()
        return self.get_total_product_price()


class Order(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ref_code = models.CharField(max_length=20, blank=True, null=True)
    orderId = models.IntegerField(primary_key=True)
    createdAt = models.DateField(auto_now_add=True)
    updatedAt = models.DateField(auto_now=True)
    status = models.CharField(choices=STATUS_CHOICES, max_length=1)
    items = models.ManyToManyField(OrderItem)
    shipping_address = models.ForeignKey(
        'Address', related_name='shipping_address', on_delete=models.SET_NULL, blank=True, null=True)
    billing_address = models.ForeignKey(
        'Address', related_name='billing_address', on_delete=models.SET_NULL, blank=True, null=True)
    payment = models.ForeignKey(
        'Payment', on_delete=models.SET_NULL, blank=True, null=True)
    coupon = models.ForeignKey(
        'Coupon', on_delete=models.SET_NULL, blank=True, null=True)
    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        if self.coupon:
            total -= self.coupon.amount
        return total


class Address(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    # country = CountryField(multiple=False)
    zip = models.CharField(max_length=100)
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    default = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = 'Addresses'


class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(User,
                             on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class Coupon(models.Model):
    code = models.CharField(max_length=15)
    amount = models.FloatField()

    def __str__(self):
        return self.code


class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()

    def __str__(self):
        return f"{self.pk}"


def userprofile_receiver(sender, instance, created, *args, **kwargs):
    if created:
        userprofile = UserProfile.objects.create(user=instance)


post_save.connect(userprofile_receiver, sender=User)
