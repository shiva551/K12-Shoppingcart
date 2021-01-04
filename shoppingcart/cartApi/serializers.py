# from django_countries.serializer_fields import CountryField
from rest_framework import serializers
from cartApi.models import (
    Address, Product, Order, OrderItem, Coupon, Variation, ProductVariation,
    Payment
)


class StringSerializer(serializers.StringRelatedField):
    def to_internal_value(self, value):
        return value


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = (
            'id',
            'code',
            'amount'
        )


class ProductSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    label = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            'id',
            'title',
            'price',
            'discount_price',
            'category',
            'label',
            'slug',
            'description',
            'imageLink',
            'createdAt',
            'updatedAt'
        )

    def get_category(self, obj):
        return obj.get_category_display()

    def get_label(self, obj):
        return obj.get_label_display()


class VariationDetailSerializer(serializers.ModelSerializer):
    item = serializers.SerializerMethodField()

    class Meta:
        model = Variation
        fields = (
            'id',
            'name',
            'product'
        )

    def get_product(self, obj):
        return ProductSerializer(obj.item).data


class ProductVariationDetailSerializer(serializers.ModelSerializer):
    variation = serializers.SerializerMethodField()

    class Meta:
        model = ProductVariation
        fields = (
            'id',
            'value',
            'attachment',
            'variation'
        )

    def get_variation(self, obj):
        return VariationDetailSerializer(obj.variation).data


class OrderItemSerializer(serializers.ModelSerializer):
    product_variations = serializers.SerializerMethodField()
    product = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = (
            'id',
            'product',
            'product_variations',
            'quantity',
            'price'
        )

    def get_product(self, obj):
        return ProductSerializer(obj.item).data

    def get_product_variations(self, obj):
        return ProductVariationDetailSerializer(obj.item_variations.all(), many=True).data

    def get_price(self, obj):
        return obj.get_price()


class OrderSerializer(serializers.ModelSerializer):
    order_products = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()
    coupon = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = (
            'id',
            'order_products',
            'total',
            'coupon'
        )

    def get_order_products(self, obj):
        return OrderItemSerializer(obj.items.all(), many=True).data

    def get_total(self, obj):
        return obj.get_total()

    def get_coupon(self, obj):
        if obj.coupon is not None:
            return CouponSerializer(obj.coupon).data
        return None


class ProductVariationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariation
        fields = (
            'id',
            'value',
            'attachment'
        )


class VariationSerializer(serializers.ModelSerializer):
    product_variations = serializers.SerializerMethodField()

    class Meta:
        model = Variation
        fields = (
            'id',
            'name',
            'product_variations'
        )

    def get_product_variations(self, obj):
        return ProductVariationSerializer(obj.productvariation_set.all(), many=True).data


class ProductDetailSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    label = serializers.SerializerMethodField()
    variations = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            'id',
            'title',
            'price',
            'discount_price',
            'category',
            'label',
            'slug',
            'description',
            'imageLink',
            'createdAt',
            'updatedAt',
            'variations'
        )

    def get_category(self, obj):
        return obj.get_category_display()

    def get_label(self, obj):
        return obj.get_label_display()

    def get_variations(self, obj):
        return VariationSerializer(obj.variation_set.all(), many=True).data


class AddressSerializer(serializers.ModelSerializer):
    # country = CountryField()

    class Meta:
        model = Address
        fields = (
            'id',
            'user',
            'street_address',
            'apartment_address',
            # 'country',
            'zip',
            'address_type',
            'default'
        )


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = (
            'id',
            'amount',
            'timestamp'
        )
