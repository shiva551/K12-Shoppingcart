from django.contrib import messages
# from django_countries import countries
from django.db.models import Q
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import (
    ListAPIView, RetrieveAPIView, CreateAPIView,
    UpdateAPIView, DestroyAPIView
)
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from cartApi.models import Product, OrderItem, Order
from cartApi.serializers import (
    ProductSerializer, OrderSerializer, ProductDetailSerializer, AddressSerializer,
    PaymentSerializer
)
from cartApi.models import (Product, OrderItem, Order, Address, Payment, Coupon, Refund, UserProfile, Variation,
                            ProductVariation)

import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY


class UserIDView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({'userID': request.user.id}, status=HTTP_200_OK)


class ProductPagination(PageNumberPagination):
    page_size = 5


class ProductListView(ListAPIView):
    pagination_class = ProductPagination
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('id', 'title', 'price', 'slug', 'category')
    permission_classes = (AllowAny,)
    serializer_class = ProductSerializer
    queryset = Product.objects.all()


class ProductDetailView(RetrieveAPIView):
    permission_classes = (AllowAny,)
    serializer_class = ProductDetailSerializer
    queryset = Product.objects.all()


class OrderQuantityUpdateView(APIView):
    def post(self, request, *args, **kwargs):
        slug = request.data.get('slug', None)
        if slug is None:
            return Response({"message": "Invalid data"}, status=HTTP_400_BAD_REQUEST)
        product = get_object_or_404(Product, slug=slug)
        order_qs = Order.objects.filter(
            user=request.user,
            ordered=False
        )
        if order_qs.exists():
            order = order_qs[0]
            # check if the order product is in the order
            if order.products.filter(product__slug=product.slug).exists():
                order_item = OrderItem.objects.filter(
                    item=product,
                    user=request.user,
                    ordered=False
                )[0]
                if order_item.quantity > 1:
                    order_item.quantity -= 1
                    order_item.save()
                else:
                    order.items.remove(order_item)
                return Response(status=HTTP_200_OK)
            else:
                return Response({"message": "This product was not in your cart"}, status=HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "You do not have an active order"}, status=HTTP_400_BAD_REQUEST)


class OrderItemDeleteView(DestroyAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = OrderItem.objects.all()


class AddToCartView(APIView):
    def post(self, request, *args, **kwargs):
        slug = request.data.get('slug', None)
        variations = request.data.get('variations', [])
        if slug is None:
            return Response({"message": "Invalid request"}, status=HTTP_400_BAD_REQUEST)

        product = get_object_or_404(Product, slug=slug)

        minimum_variation_count = Variation.objects.filter(item=product).count()
        if len(variations) < minimum_variation_count:
            return Response({"message": "Please specify the required variation types"}, status=HTTP_400_BAD_REQUEST)

        order_item_qs = OrderItem.objects.filter(
            item=product,
            user=request.user,
            ordered=False
        )
        for v in variations:
            order_item_qs = order_item_qs.filter(
                Q(item_variations__exact=v)
            )

        if order_item_qs.exists():
            order_item = order_item_qs.first()
            order_item.quantity += 1
            order_item.save()
        else:
            order_item = OrderItem.objects.create(
                item=product,
                user=request.user,
                ordered=False
            )
            order_item.item_variations.add(*variations)
            order_item.save()

        order_qs = Order.objects.filter(user=request.user, ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            if not order.items.filter(item__id=order_item.id).exists():
                order.items.add(order_item)
                return Response(status=HTTP_200_OK)

        else:
            ordered_date = timezone.now()
            order = Order.objects.create(
                user=request.user, ordered_date=ordered_date)
            order.items.add(order_item)
            return Response(status=HTTP_200_OK)


class OrderDetailView(RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            return order
        except ObjectDoesNotExist:
            raise Http404("You do not have an active order")
            # return Response({"message": "You do not have an active order"}, status=HTTP_400_BAD_REQUEST)


class PaymentView(APIView):

    def post(self, request, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        userprofile = UserProfile.objects.get(user=self.request.user)
        token = request.data.get('stripeToken')
        billing_address_id = request.data.get('selectedBillingAddress')
        shipping_address_id = request.data.get('selectedShippingAddress')

        billing_address = Address.objects.get(id=billing_address_id)
        shipping_address = Address.objects.get(id=shipping_address_id)

        if userprofile.stripe_customer_id != '' and userprofile.stripe_customer_id is not None:
            customer = stripe.Customer.retrieve(
                userprofile.stripe_customer_id)
            customer.sources.create(source=token)

        else:
            customer = stripe.Customer.create(
                email=self.request.user.email,
            )
            customer.sources.create(source=token)
            userprofile.stripe_customer_id = customer['id']
            userprofile.one_click_purchasing = True
            userprofile.save()

        amount = int(order.get_total() * 100)

        try:

            # charge the customer because we cannot charge the token more than once
            charge = stripe.Charge.create(
                amount=amount,  # cents
                currency="usd",
                customer=userprofile.stripe_customer_id
            )
            # charge once off on the token
            # charge = stripe.Charge.create(
            #     amount=amount,  # cents
            #     currency="usd",
            #     source=token
            # )

            # create the payment
            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = order.get_total()
            payment.save()

            # assign the payment to the order

            order_items = order.items.all()
            order_items.update(ordered=True)
            for item in order_items:
                item.save()

            order.ordered = True
            order.payment = payment
            order.billing_address = billing_address
            order.shipping_address = shipping_address
            # order.ref_code = create_ref_code()
            order.save()

            return Response(status=HTTP_200_OK)

        except stripe.error.CardError as e:
            body = e.json_body
            err = body.get('error', {})
            return Response({"message": f"{err.get('message')}"}, status=HTTP_400_BAD_REQUEST)

        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            messages.warning(self.request, "Rate limit error")
            return Response({"message": "Rate limit error"}, status=HTTP_400_BAD_REQUEST)

        except stripe.error.InvalidRequestError as e:
            print(e)
            # Invalid parameters were supplied to Stripe's API
            return Response({"message": "Invalid parameters"}, status=HTTP_400_BAD_REQUEST)

        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            return Response({"message": "Not authenticated"}, status=HTTP_400_BAD_REQUEST)

        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            return Response({"message": "Network error"}, status=HTTP_400_BAD_REQUEST)

        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            return Response({"message": "Something went wrong. You were not charged. Please try again."},
                            status=HTTP_400_BAD_REQUEST)

        except Exception as e:

            return Response({"message": "A serious error occurred. We have been notifed."}, status=HTTP_400_BAD_REQUEST)

        return Response({"message": "Invalid data received"}, status=HTTP_400_BAD_REQUEST)


class AddCouponView(APIView):
    def post(self, request, *args, **kwargs):
        code = request.data.get('code', None)
        if code is None:
            return Response({"message": "Invalid data received"}, status=HTTP_400_BAD_REQUEST)
        order = Order.objects.get(
            user=self.request.user, ordered=False)
        coupon = get_object_or_404(Coupon, code=code)
        order.coupon = coupon
        order.save()
        return Response(status=HTTP_200_OK)


# class CountryListView(APIView):
#     def get(self, request, *args, **kwargs):
#         return Response(countries, status=HTTP_200_OK)


class AddressListView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = AddressSerializer

    def get_queryset(self):
        address_type = self.request.query_params.get('address_type', None)
        qs = Address.objects.all()
        if address_type is None:
            return qs
        return qs.filter(user=self.request.user, address_type=address_type)


class AddressCreateView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = AddressSerializer
    queryset = Address.objects.all()


class AddressUpdateView(UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = AddressSerializer
    queryset = Address.objects.all()


class AddressDeleteView(DestroyAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Address.objects.all()


class PaymentListView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = PaymentSerializer

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)
