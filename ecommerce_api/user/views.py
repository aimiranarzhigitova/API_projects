from django.middleware.csrf import get_token
from django.shortcuts import render
from rest_framework.response import Response
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from .serializers import DetailsSerializer, AddressSerializer
from .utils import generate_access_token, generate_refresh_token
from .decorators import check_blacklist_token
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny
import jwt, json
from django.conf import settings
from ecommerce_api.settings import blackListedTokens
from django.db.utils import IntegrityError
from API.serializers import *


@api_view(['GET'])
@check_blacklist_token
def profile(request):
    user = request.user
    try:
        serialized_user = DetailsSerializer(user).data
    except AttributeError:
        return Response({'response': 'authorization credentials missing!', 'status': False})
    address = Address.objects.filter(userId=user).first()
    if address:
        serialized_address = AddressSerializer(address).data
        del serialized_address['id']
        del serialized_address['userId']
        serialized_user['address'] = serialized_address
    else:
        serialized_user['address'] = '(unavailable)'
    return Response({'user': serialized_user, 'status': True})


@api_view(['POST'])
@check_blacklist_token
def user_address(request):
    jsn = request.data['address']
    area = None if 'area' not in jsn else jsn['area']
    city = None if 'city' not in jsn else jsn['city']
    state = None if 'state' not in jsn else jsn['state']
    country = None if 'country' not in jsn else jsn['country']
    pincode = None if 'pincode' not in jsn else jsn['pincode']
    landmark = None if 'landmark' not in jsn else jsn['landmark']
    adr_type = None if 'adr_type' not in jsn else jsn['adr_type']
    if area or city or country or pincode or landmark or adr_type:
        authorization_header = request.headers.get('Authorization')
        if authorization_header is None:
            return Response({'response': 'Authorization credential missing!', 'status': False})
        try:
            access_token = authorization_header.split(' ')[1]
            payload = jwt.decode(
                access_token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return Response({'response': 'access token expired!', 'status': False})
        User = get_user_model()
        user = User.objects.filter(id=payload['user_id']).first()
        if user is None:
            return Response({'response': 'User with given credentials not found!', 'status': False})
        address = Address.objects.filter(userId=user).first()
        if address:
            address = Address(id=address.id, area=area, city=city, country=country, state=state, pinCode=pincode, landmark=landmark, type=adr_type, userId=user)
            address.save()
            address = Address.objects.filter(userId=user).first()
            address = AddressSerializer(address).data
            return Response({'response': 'address successfully modified!', 'status': True, 'address': address})
        address = Address(area=area, city=city, country=country, pinCode=pincode, landmark=landmark, type=adr_type, userId=user)
        address.save()
        address = Address.objects.filter(userId=user).first()
        address = AddressSerializer(address).data
        return Response({'response': 'address successfully saved!', 'status': True, 'address': address})
    else:
        return Response({'response': 'nothing happened!', 'status': False})


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    context = {}
    jsn: dict
    try:
        jsn = json.loads(request.body)
    except json.decoder.JSONDecodeError:
        jsn = {}
    if jsn:
        for k, v in jsn.items():
            if 'password' != k:
                context[k] = jsn[k]
    if not ('email' in jsn and 'username' in jsn and 'password' in jsn):
        return Response({'response': 'Registration Unsuccessful! (required data: email, username, password)', 'status': False})
    try:
        User = get_user_model()
        user = User(email=jsn['email'], username=jsn['username'])
        user.set_password(jsn['password'])
        user.save()
    except IntegrityError as err:
        dup = str(err).split('user_details_')[1].split('_key')[0]
        return Response({'response': f'{dup} already taken by another user, please user another {dup} and try again!', 'duplicate': dup})
    except IndexError as err:
        return Response({'response': 'duplication found!', 'status': False})
    if jsn:
        user = User.objects.filter(email=jsn['email']).first()
        cart = Cart(userId=user)
        cart.save()
        return Response({'response': 'user created!', 'status': True, 'context': context})
    return Response({'response': 'user not created!', 'status': False})


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    User = get_user_model()
    email = request.data.get('email')
    password = request.data.get('password')
    response = Response()
    if email is None and password is None:
        return Response({'response': 'email and password are missing and are required for authentication', 'status': False})
    user = User.objects.filter(email=email).first()
    if user is None:
        return Response({'response': 'User not found!', 'status': False})
    if not user.check_password(password):
        return Response({'response': 'Wrong Password', 'status': False})

    serialized_user = DetailsSerializer(user).data

    access_token = generate_access_token(user)
    refresh_token = generate_refresh_token(user)
    csrf_token = get_token(request)
    response.set_cookie(key='refreshtoken', value=refresh_token, httponly=True)
    response.data = {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'csrf_token': csrf_token,
        'user': serialized_user,
        'status': True
    }
    return response


@api_view(['POST'])
def logout(request):
    User = get_user_model()
    authorization_header = request.headers.get('Authorization')
    if not authorization_header:
        return Response({'response': 'authorization credential missing!', 'status': False})
    access_token = False
    refresh_token = False
    try:
        access_token = authorization_header.split(' ')[1]
        refresh_token = request.COOKIES.get('refreshtoken')
        payload = jwt.decode(
            access_token, settings.SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        if not refresh_token:
            return Response({'response': 'Credential not found in request cookies! (you might have already been logged out!)', 'status': False})
        try:
            payload = jwt.decode(
                refresh_token, settings.REFRESH_TOKEN_SECRET, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return Response({'response': 'your jwt session time has already been out, you have been logged out already!', 'status': True})
        user = User.objects.filter(id=payload['user.id'])
        if user is None:
            return Response({'response': 'user associated with received credential was not found!', 'status': False})
    finally:
        if access_token in blackListedTokens and refresh_token in blackListedTokens:
            return Response({'response': 'already logged out!', 'status': False})
        elif access_token in blackListedTokens:
            blackListedTokens.add(refresh_token)
            return Response({'response': 'already logged out!', 'status': False})
        elif refresh_token in blackListedTokens:
            blackListedTokens.add(access_token)
            return Response({'response': 'already logged out!', 'status': False})
        if access_token:
            blackListedTokens.add(access_token)
        if refresh_token:
            blackListedTokens.add(refresh_token)
        return Response({'response': 'successfully logged out!', 'status': True})


@api_view(['POST'])
@check_blacklist_token
def refresh_token(request):
    User = get_user_model()
    refresh_token = request.COOKIES.get('refreshtoken')
    if not refresh_token:
        return Response({'response': 'authentication credential missing!', 'status': False})
    try:
        payload = jwt.decode(
            refresh_token, settings.REFRESH_TOKEN_SECRET, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return Response({'response': 'refresh token expired!', 'status': False})
    except jwt.InvalidSignatureError:
        return Response({'response': 'invalid refresh token!', 'status': False})
    user = User.objects.filter(id=payload['user.id']).first()
    if user is None:
        return Response({'response': 'user not found!', 'status': False})
    access_token = generate_access_token(user)
    return Response({'access_token': access_token, 'status': True})


@api_view(['POST'])
@check_blacklist_token
def delete_user(request):
    User = get_user_model()
    authorization_header = request.headers.get('Authorization')
    if not authorization_header:
        return Response({'response': 'Authorization credential missing/expired!', 'status': False})
    try:
        access_token = authorization_header.split(' ')[1]
        payload = jwt.decode(
            access_token, settings.SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return Response({'response': 'access token expired!', 'status': False})
    user = User.objects.filter(id=payload['user_id']).first()
    if user is None:
        return Response({'response': 'User not found!', 'status': False})
    user.delete()
    return Response({'response': 'User successfully deleted!', 'status': True})


@api_view(['GET'])
@check_blacklist_token
def cart_view(request):
    authorization_header = request.headers.get('Authorization')
    if not authorization_header:
        return Response({'response': 'authorization credential missing!', 'status': False})
    try:
        access_token = authorization_header.split(' ')[1]
        payload = jwt.decode(
            access_token, settings.SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return Response({'response': 'access token expired!', 'status': False})
    User = get_user_model()
    user = User.objects.filter(id=payload['user_id']).first()
    if not user:
        return Response({'response': 'User not found!', 'status': False})
    cart = Cart.objects.filter(userId=user).first()
    if cart is None:
        cart = Cart(userId=user)
        cart.save()
    cartProducts = []
    cost = 0
    for cartProds in cart.products.all():
        prod = QuantityProductSerializer(cartProds).data
        product = Product.objects.filter(productId=prod['productId']).first()
        serialized_product = ProductSerializer(product).data
        cost += serialized_product['price'] * prod['prod_quantity']
        cartProducts.append(prod)
    cart = Cart(id=cart.id, paymentMethod=cart.paymentMethod, finalAmount="Rs." + str(cost), userId=user)
    cart.save()
    serializedCart = CartSerializer(cart).data
    del serializedCart['products']
    serializedCart['products'] = cartProducts
    return Response({'response': {'cart': serializedCart}, 'status': True})


@api_view(['POST'])
@check_blacklist_token
def add_to_cart(request):
    authorization_header = request.headers.get('Authorization')
    if not authorization_header:
        return Response({'response': 'authorization credential missing!', 'status': False})
    try:
        access_token = authorization_header.split(' ')[1]
        payload = jwt.decode(
            access_token, settings.SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return Response({'response': 'access token expired!', 'status': False})
    User = get_user_model()
    user = User.objects.filter(id=payload.get('user_id')).first()
    if user is None:
        return Response({'response': 'User not found!', 'status': False})
    cart = Cart.objects.filter(userId=user).first()
    if not cart:
        cart = Cart(userId=user)
        cart.save()
        cart = Cart.objects.filter(userId=user).first()
    jsn = request.data
    if 'product' not in jsn:
        return Response({'response': 'missing product data in request!', 'status': False})
    productId = jsn['product']
    serialized_cart = CartSerializer(cart).data
    cart_products = serialized_cart['products']
    for cart_product in cart_products:
        quantity_product = QuantityProduct.objects.filter(id=cart_product).first()
        serialized_quantity_product = QuantityProductSerializer(quantity_product).data
        if productId == serialized_quantity_product['productId']:
            quantity_product = QuantityProduct(id=quantity_product.id, prod_quantity=1+quantity_product.prod_quantity, productId=quantity_product.productId)
            quantity_product.save()
            return Response({'response': f"item ({quantity_product.productId.name}) successfully added to {user.username}'s cart!", 'status': True})
    product = Product.objects.filter(productId=productId).first()
    if not product:
        return Response({'response': 'product not found!', 'status': False})
    productQuantity = QuantityProduct(productId=product, prod_quantity=1)
    productQuantity.save()
    cart.products.add(productQuantity)
    return Response({'response': f'''successfully added product '{productQuantity.prod_quantity}' '{productQuantity.productId.name}(s)' in {user.username}'s cart''', 'status': True})


@api_view(['POST'])
@check_blacklist_token
def remove_from_cart(request):
    authorization_header = request.headers.get('Authorization')
    if not authorization_header:
        return Response({'response': 'authorization credential missing!', 'status': False})
    try:
        access_token = authorization_header.split(' ')[1]
        payload = jwt.decode(
            access_token, settings.SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return Response({'response': 'access token expired!', 'status': False})
    User = get_user_model()
    user = User.objects.filter(id=payload['user_id']).first()
    if user is None:
        return Response({'response': 'User not found!', 'status': False})
    cart = Cart.objects.filter(userId=user).first()
    if cart is None:
        cart = Cart(userId=user)
        cart.save()
        return Response({'response': 'cart is already empty', 'status': False})
    jsn = request.data
    if 'product' not in jsn:
        return Response({'response': 'missing product data in request!', 'status': False})
    productId = jsn['product']
    serialized_cart = CartSerializer(cart).data
    cart_products = serialized_cart['products']
    for cart_product in cart_products:
        quantity_product = QuantityProduct.objects.filter(id=cart_product).first()
        if productId == quantity_product.productId.productId:
            quantity_product = QuantityProduct.objects.filter(id=quantity_product.id).first()
            productName = quantity_product.productId.name
            quantity_product.delete()
            return Response({'response': f'''successfully removed {productName} from {user.username}'s cart''', 'status': True})
    return Response({'response': 'product not found in cart!', 'status': False})


@api_view(['POST'])
@check_blacklist_token
def change_cart_product_quantity(request):
    authorization_header = request.headers.get('Authorization')
    if not authorization_header:
        return Response({'response': 'authorization credential missing!', 'status': False})
    try:
        access_token = authorization_header.split(' ')[1]
        payload = jwt.decode(
            access_token, settings.SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return Response({'response': 'access token expired!', 'status': False})
    User = get_user_model()
    user = User.objects.filter(id=payload.get('user_id')).first()
    if user is None:
        return Response({'response': 'User not found!', 'status': False})
    cart = Cart.objects.filter(userId=user).first()
    if not cart:
        cart = Cart(userId=user)
        cart.save()
        return Response({'response': 'cart is empty!', 'status': False})
    jsn = request.data
    if 'product' not in jsn:
        return Response({'response': 'missing product data in request!', 'status': False})
    productId = jsn['product']['pro_id']
    pro_quantity = jsn['product']['quantity']
    serialized_cart = CartSerializer(cart).data
    cart_products = serialized_cart['products']
    for cart_product in cart_products:
        quantity_product = QuantityProduct.objects.filter(id=cart_product).first()
        if productId == quantity_product.productId.productId:
            if pro_quantity == 0:
                productName = quantity_product.productId.name
                quantity_product.delete()
                return Response({'response': f"successfully removed product ({productName}) from {user.username}'s cart!", 'status': True})
            quantity_product = QuantityProduct(id=quantity_product.id, productId=quantity_product.productId, prod_quantity=pro_quantity)
            quantity_product.save()
            return Response({'response': f"successfully changed product quantity of product {quantity_product.productId.name} to {pro_quantity} quantity in cart!", 'status': True})
    return Response({'response': 'product not found in cart!', 'status': False})


@api_view(['POST'])
@check_blacklist_token
def cart_paymentMethod(request):
    authorization_header = request.headers.get('Authorization')
    if not authorization_header:
        return Response({"response": "authorization credential missing!", "status": False})
    try:
        access_token = authorization_header.split(' ')[1]
        payload = jwt.decode(
            access_token, settings.SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return Response({'response': 'access token expired!', 'status': False})
    except jwt.InvalidSignatureError:
        return Response({'response': 'invalid token!', 'status': False})
    User = get_user_model()
    user = User.objects.filter(id=payload['user_id']).first()
    if not user:
        return Response({'response': 'User not found!', 'status': False})
    cart = Cart.objects.filter(userId=user).first()
    if not cart:
        cart = Cart(userId=user)
        cart.save()
        return Response({'response': 'cart is empty!', 'status': False})
    jsn = request.data
    if 'paymentMethod' not in jsn:
        return Response({'response': 'missing payment method in request!', 'status': False})
    paymentMethod = jsn['paymentMethod']
    if type(paymentMethod) != str:
        return Response({'response': f'''paymentMethod field should be only string but received of type '{str(type(paymentMethod)).split("'")[1]}' ''', 'status': False})
    cart = Cart(id=cart.id, paymentMethod=paymentMethod, finalAmount=cart.finalAmount, userId=cart.userId)
    cart.save()
    return Response({'response': f'{cart.paymentMethod}', 'status': True})


@api_view(['GET'])
@check_blacklist_token
def orders_view(request):
    authorization_header = request.headers.get('Authorization')
    if not authorization_header:
        return Response({'response': 'authorization credentials missing!', 'status': False})
    try:
        access_token = authorization_header.split(' ')[1]
        payload = jwt.decode(
            access_token, settings.SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return Response({'response': 'access token expired!', 'status': False})
    except jwt.InvalidSignatureError:
        return Response({'response': 'invalid token!', 'status': False})
    User = get_user_model()
    user = User.objects.filter(id=payload['user_id']).first()
    if not user:
        return Response({'response': 'User not found!', 'status': False})
    orders = user.order_set.all()
    userOrders = []
    for order in orders:
        serialized_order = OrderSerializer(order).data
        orderProducts = []
        for cartProds in order.products.all():
            prod = QuantityProductSerializer(cartProds).data
            orderProducts.append(prod)
        userAddress = AddressSerializer(order.userId.address_set.all()[0]).data
        del userAddress['userId']
        del userAddress['id']
        del serialized_order['id']
        del serialized_order['address']
        serialized_order['address'] = userAddress
        del serialized_order['products']
        serialized_order['products'] = orderProducts
        userOrders.append(serialized_order)
    return Response({'response': {'orders': userOrders}, 'status': True})


@api_view(['POST'])
@check_blacklist_token
def place_order(request):
    authorization_header = request.headers.get('Authorization')
    if not authorization_header:
        return Response({'response': 'authorization credential missing!', 'status': False})
    try:
        access_token = authorization_header.split(' ')[1]
        payload = jwt.decode(
            access_token, settings.SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return Response({'response': 'access token expired!', 'status': False})
    except jwt.InvalidSignatureError:
        return Response({'response': 'invalid token!', 'status': False})
    User = get_user_model()
    user = User.objects.filter(id=payload['user_id']).first()
    if not user:
        return Response({'response': 'User not found!', 'status': False})
    cart = CartSerializer(user.cart).data
    cart_products = cart['products']
    if len(cart_products) == 0:
        return Response({'response': "User cart is empty, can't place order", 'status': False})
    order = Order(userId=user, finalAmount=cart['finalAmount'], paymentMethod=cart['paymentMethod'], orderState="pending", address=user.address_set.all()[0])
    order.save()
    for cart_product in cart_products:
        quantity_product = QuantityProduct.objects.filter(id=cart_product).first()
        quantity_product = QuantityProduct(productId=quantity_product.productId, prod_quantity=quantity_product.prod_quantity)
        quantity_product.save()
        order.products.add(quantity_product)
    serialized_order = OrderSerializer(order).data
    orderProducts = []
    for cartProds in order.products.all():
        prod = QuantityProductSerializer(cartProds).data
        orderProducts.append(prod)
    del serialized_order['products']
    serialized_order['products'] = orderProducts
    user.cart.delete()
    cart = Cart(userId=user)
    cart.save()
    return Response({'response': 'order successfully placed!', 'order_details': serialized_order, 'status': True})
