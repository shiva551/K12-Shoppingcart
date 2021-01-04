from django.contrib import admin

from .models import (
    Product, OrderItem, Order, Payment, Coupon, Refund,
    Address, UserProfile, Variation, ProductVariation
)


def make_refund_accepted(modeladmin, request, queryset):
    queryset.update(refund_requested=False, refund_granted=True)


make_refund_accepted.short_description = 'Update orders to refund granted'


class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'orderId',
        'createdAt',
        'updatedAt',
        'status',
        'shipping_address',
        'billing_address',
        'payment',
        'coupon',
        'being_delivered',
        'received',
        'refund_requested',
        'refund_granted'
    ]
    list_display_links = [
        'user',
        'shipping_address',
        'billing_address',
        'payment',
        'coupon'
    ]
    list_filter = [
        'being_delivered',
        'received',
        'refund_requested',
        'refund_granted'
    ]
    search_fields = [
        'user__username',
        'ref_code'
    ]
    actions = [make_refund_accepted]


class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'street_address',
        'apartment_address',
        'zip',
        'address_type',
        'default'
    ]
    list_filter = ['default', 'address_type']
    search_fields = ['user', 'street_address', 'apartment_address', 'zip']


class ProductVariationAdmin(admin.ModelAdmin):
    list_display = ['variation',
                    'value',
                    'attachment']
    list_filter = ['variation', 'variation__product']
    search_fields = ['value']


class ProductVariationInLineAdmin(admin.TabularInline):
    model = ProductVariation
    extra = 1


class VariationAdmin(admin.ModelAdmin):
    list_display = ['product',
                    'name']
    list_filter = ['product']
    search_fields = ['name']
    inlines = [ProductVariationInLineAdmin]


admin.site.register(ProductVariation, ProductVariationAdmin)
admin.site.register(Variation, VariationAdmin)
admin.site.register(Product)
admin.site.register(OrderItem)
admin.site.register(Order, OrderAdmin)
admin.site.register(Payment)
admin.site.register(Coupon)
admin.site.register(Refund)
admin.site.register(Address, AddressAdmin)
admin.site.register(UserProfile)
