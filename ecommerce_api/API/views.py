from django.utils.text import slugify
from rest_framework.response import Response
from django.http import JsonResponse, QueryDict
from rest_framework.permissions import AllowAny
import jwt
import json
import shortuuid
from user.decorators import *
from user.models import *
from .serializers import *
from user.serializers import *
from rest_framework.decorators import api_view, permission_classes
from user.decorators import check_blacklist_token
from django.conf import settings
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import ensure_csrf_cookie


@api_view(['GET'])
@permission_classes([AllowAny])
def products_view(request):
    print("query parameters : ", end="")
    query_params = dict(request.query_params)
    print(query_params)
    query_params_n = len(query_params)
    done_query_param_n = 0
    print("no of params : " + str(query_params_n))
    products = Product.objects.all()
    categories_values = fetch_categories_from_product_instance(products)
    print(categories_values)
    query_errors = []
    if query_params_n > 0:
        while True:
            if 'price>' in query_params:
                price_filter = str(query_params['price>'][0])
                del query_params['price>']
                done_query_param_n += 1
                if price_filter.isdigit():
                    products = products.filter(price__gte = int(price_filter))
                    resultProducts = serialize_products_from_instance(products)
                    if len(query_errors) > 0:
                        return Response({'response': resultProducts, 'status': True, 'errors': query_errors, 'error': True})
                    if done_query_param_n == query_params_n:
                        return Response({'response': resultProducts, 'status': True})
                else:
                    query_errors.append("invalid value for query parameter 'price>'")
                    if done_query_param_n == query_params_n:
                        return Response({'response': query_errors, 'status': False, 'error': True})
            elif 'price<' in query_params:
                price_filter = str(query_params['price<'][0])
                del query_params['price<']
                done_query_param_n += 1
                if price_filter.isdigit():
                    products = products.filter(price__lte = int(price_filter))
                    resultProducts = serialize_products_from_instance(products)
                    if len(query_errors) > 0:
                        return Response({'response': resultProducts, 'status': True, 'errors': query_errors, 'error': True})
                    if done_query_param_n == query_params_n:
                        return Response({'response': resultProducts, 'status': True})
                else:
                    query_errors.append("invalid value for query parameter 'price<'")
                    if done_query_param_n == query_params_n:
                        return Response({'response': query_errors, 'status': False, 'error': True})
            elif 'cate' in query_params:
                category_query = query_params['cate'][0]
                del query_params['cate']
                done_query_param_n += 1
                category_query = category_query.split('-')
                if len(category_query) > 0:
                    temp_products = products.filter(productId=-1)
                    for category in category_query:
                        temp_products = temp_products | products.filter(productdetails__categories__contains=[category])
                    products = temp_products
                    resultProducts = serialize_products_from_instance(products)
                    if len(query_errors) > 0:
                        return Response(
                            {'response': resultProducts, 'status': True, 'errors': query_errors, 'error': True})
                    if done_query_param_n == query_params_n:
                        return Response({'response': resultProducts, 'status': True})
                else:
                    query_errors.append("invalid value for query parameter 'cate'")
                    if done_query_param_n == query_params_n:
                        return Response({'response': query_errors, 'status': False})
            elif 'pay' in query_params:
                pay_opt = query_params['pay'][0]
                del query_params['pay']
                done_query_param_n += 1
                if pay_opt == 'c' or pay_opt == 'o':
                    if pay_opt == 'c':
                        print("cash on delivery filter")
                        products = products.filter(paymentOption='Cash On Delivery')
                    else:
                        print("online filter")
                        products = products.filter(paymentOption='Online')
                    resultProducts = serialize_products_from_instance(products)
                    if len(query_errors) > 0:
                        return Response(
                            {'response': resultProducts, 'status': True, 'errors': query_errors, 'error': True})
                    if done_query_param_n == query_params_n:
                        return Response({'response': resultProducts, 'status': True})
                else:
                    query_errors.append({'response': "invalid value for query parameter 'pay'"})
                    if done_query_param_n == query_params_n:
                        return Response({'response': query_errors, 'status': False})
            elif 'stock' in query_params:
                stock = query_params['stock'][0]
                del query_params['stock']
                done_query_param_n += 1
                if stock == 't' or stock == 'f':
                    if stock == 't':
                        products = products.filter(isInStock=True)
                    else:
                        products = products.filter(isInStock=False)
                    resultProducts = serialize_products_from_instance(products)
                    if len(query_errors) > 0:
                        return Response({'response': resultProducts, 'status': True, 'errors': query_errors, 'error': True})
                    if done_query_param_n == query_params_n:
                        return Response({'response': resultProducts, 'status': True})
                else:
                    query_errors.append({'response': "invalid value for query parameter 'stock'"})
                    if done_query_param_n == query_params_n:
                        return Response({'response': query_errors, 'status': False})
            elif 'rating_l' in query_params:
                rate_l = query_params['rating_l'][0]
                del query_params['rating_l']
                done_query_param_n += 1
                if len(rate_l) > 0 and rate_l.isdigit:
                    products = products.filter(productdetails__rating__lte=float(rate_l))
                    resultProducts = serialize_products_from_instance(products)
                    if len(query_errors) > 0:
                        return Response(
                            {'response': resultProducts, 'status': True, 'errors': query_errors, 'error': True})
                    if done_query_param_n == query_params_n:
                        return Response({'response': resultProducts, 'status': True})
                else:
                    query_errors.append({'response': "invalid value for query parameter 'rating_l'"})
                    if done_query_param_n == query_params_n:
                        return Response({'response': query_errors, 'status': False})
            elif 'rating_g' in query_params:
                rate_g = query_params['rating_g'][0]
                del query_params['rating_g']
                done_query_param_n += 1
                if len(rate_g) > 0 and rate_g.isdigit:
                    products = products.filter(productdetails__rating__gte=float(rate_g))
                    resultProducts = serialize_products_from_instance(products)
                    if len(query_errors) > 0:
                        return Response(
                            {'response': resultProducts, 'status': True, 'errors': query_errors, 'error': True})
                    if done_query_param_n == query_params_n:
                        return Response({'response': resultProducts, 'status': True})
                else:
                    query_errors.append({'response': "invalid value for query parameter 'rating_l'"})
                    if done_query_param_n == query_params_n:
                        return Response({'response': query_errors, 'status': False})
            elif 'orderby' in query_params:
                orderby = query_params['orderby'][0]
                del query_params['orderby']
                done_query_param_n += 1
                if orderby == '-price' or orderby == '-name' or orderby == '-stock' or orderby == '-manufacturer' or orderby == 'price' or orderby == 'name' or orderby == 'stock' or orderby == 'manufacturer' or orderby == 'rating' or orderby == '-rating':
                    if orderby == 'rating':
                        print("rating order")
                        products = products.order_by("productdetails__rating")
                    elif orderby == '-rating':
                        print("-rating order")
                        products = products.order_by("-productdetails__rating")
                    else:
                        products = products.order_by(orderby)
                    if done_query_param_n == query_params_n:
                        resultProducts = serialize_products_from_instance(products)
                        if len(query_errors) > 0:
                            return Response({'response': resultProducts, 'status': True, 'errors': query_errors, 'error': True})
                        return Response({'response': resultProducts, 'status': True})
                else:
                    query_errors.append('invalid orderby value received in url query')
                    if done_query_param_n == query_params_n:
                        return Response({'response': query_errors, 'status': False, 'error': True})

    if query_params_n == 0:
        resultProducts = serialize_products_from_instance(products.order_by('productId'))
        resultProducts['categories'] = categories_values
        return Response({'response': resultProducts, 'status': True})
    else:
        return Response({'response': 'invalid url request', 'status': False})


def serialize_products_from_instance(products):
    serialized_products = ProductSerializer(products, many=True).data
    products_result = {'total_products': 0, 'categories': fetch_categories_from_product_instance(products), 'products': []}
    totalProducts = len(serialized_products)
    for product in serialized_products:
        product = dict(product)
        products_result['products'].append(product)
    products_result['total_products'] = totalProducts
    return products_result


def fetch_categories_from_product_instance(products):
    categories_values = list(products.values('productdetails__categories'))
    cate_s = set()
    for cat_d in categories_values:
        if 'productdetails__categories' in cat_d:
            for category in cat_d['productdetails__categories']:
                cate_s.add(category)
    categories_values = list(cate_s)
    return categories_values


@api_view(['GET'])
@permission_classes([AllowAny])
def product_detailed_view(request):
    query_params = request.query_params
    if 'prdct' in query_params or ('id' in query_params and query_params['id'].isdigit):
        if 'prdct' in query_params:
            query_slug = query_params['prdct']
            product = Product.objects.filter(productSlug__exact=query_slug).first()
        else:
            pr_id = int(query_params['id'])
            product = Product.objects.filter(productId=pr_id).first()
        if not product:
            return Response({'response': 'product does not exists', 'status': False})
        product = ProductSerializer(product).data
        product_details = ProductDetails.objects.filter(product_id=product['productId']).first()
        product_details = ProductDetailSerializer(product_details).data
        del product_details['product_id']
        for (k, v) in product_details.items():
            product[k] = v
        return Response({'response': product, 'status': True})
    else:
        return Response({'response': 'missing product identity query parameter in requested url', 'status': False})


@api_view(['POST'])
@check_blacklist_token
def create_product(request):
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
        return Response({'response': '(unauthorized access) User associated with received access token not found!',
                         'status': False})
    jsonData = request.data
    if jsonData:
        if type(jsonData) == QueryDict:
            jsonData = dict(jsonData)
        print(jsonData)
        required_fields = [
            "name",
            "price",
            "thumbnail",
            "stock",
        ]
        optional_fields = [
            "manufacturer",
            "brand",
            "paymentOption",
            "description",
            "countryOfOrigin",
            "photos",
            "categories",
            "rating",
            "discount",
            "coupons"
        ]
        for fields in required_fields:
            if fields not in jsonData:
                return Response({'response': 'missing one of the required fields for product creation in request', 'fields': {'required_fields': required_fields, 'optional_fields': optional_fields}, 'status': False})
        product_name = jsonData['name']
        product_slug = slugify(product_name) + "-" + str(shortuuid.ShortUUID().random(length=12))
        product_price = jsonData['price']
        product_thumbnail = jsonData['thumbnail']
        product_stock = jsonData['stock'] if type(jsonData['stock']) == int else 0
        product_inStock = product_stock > 0
        product_manufacturer = jsonData['manufacturer'] if 'manufacturer' in jsonData else 'Anonymous'
        product_brand = jsonData['brand'] if 'brand' in jsonData else None
        product_paymentOption = jsonData['paymentOption'] if 'paymentOption' in jsonData else 'Cash On Delivery'
        product_description = jsonData['description'] if 'description' in jsonData else 'description not provided by seller'
        product_countryOfOrigin = jsonData['countryOfOrigin'] if 'countryOfOrigin' in jsonData else 'Anonymous'
        product_photos = jsonData['products'] if 'products' in jsonData and type(jsonData['products']) == list else []
        product_categories = jsonData['categories'] if 'categories' in jsonData and type(jsonData['categories']) == list else []
        product_rating = jsonData['rating'] if 'rating' in jsonData else '0.0'
        product_discount = jsonData['discount'] if 'discount' in jsonData else None
        product_coupons = jsonData['coupons'] if 'coupons' in jsonData and type(jsonData['coupons']) == list else []
        product = Product(
            name=product_name,
            productSlug=product_slug,
            price=product_price,
            thumbnail=product_thumbnail,
            stock=product_stock,
            isInStock=product_inStock,
            manufacturer=product_manufacturer,
            paymentOption=product_paymentOption,
        )
        product.save()
        product_details = ProductDetails(
            product_id=product,
            description=product_description,
            brand=product_brand,
            countryOfOrigin=product_countryOfOrigin,
            photos=product_photos,
            categories=product_categories,
            rating=product_rating,
            discount=product_discount,
            coupons=product_coupons
        )
        product_details.save()
        product = ProductSerializer(product).data
        product_details = ProductDetailSerializer(product_details).data
        del product_details['product_id']
        for k, v in product_details.items():
            product[k] = v
        return Response({'response': 'product successfully created!', "product": product, 'status': True})
    else:
        return Response({'response': 'product data not found in request', 'status': False})


@api_view(['POST'])
@check_blacklist_token
def update_product(request):
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
        return Response({'response': '(unauthorized access) User associated with received access token not found!',
                         'status': False})
    query_params = request.query_params
    jsonData = request.data
    if len(query_params) > 0 and 'id' in query_params and query_params['id'].isdigit:
        if jsonData and type(jsonData) == QueryDict:
            jsonData = dict(jsonData)
        product_id = int(query_params['id'])
        product = Product.objects.filter(productId=product_id).first()
        if not product:
            return Response({'response': 'product of given id does not exists', 'status': False})
        product_details = ProductDetails.objects.filter(product_id=product_id).first()
        product_dict = ProductSerializer(product).data
        product_details_dict = ProductDetailSerializer(product_details).data
        updated_product_data = dict()
        product_fields = [
            "name",
            "price",
            "manufacturer",
            "thumbnail",
            "stock",
            "paymentOption",
        ]
        product_details_fields =[
            "description",
            "brand",
            "countryOfOrigin",
            "photos",
            "categories",
            "rating",
            "discount",
            "coupons"
        ]
        if jsonData:
            for field in product_fields:
                if field in jsonData:
                    updated_product_data[field] = jsonData[field]
                else:
                    updated_product_data[field] = product_dict[field]
            for field in product_details_fields:
                if field in jsonData:
                    updated_product_data[field] = jsonData[field]
                else:
                    updated_product_data[field] = product_details_dict[field]
            updated_product = Product(
                productId=product_id,
                name=updated_product_data['name'],
                productSlug=product.productSlug,
                price=updated_product_data['price'],
                manufacturer=updated_product_data['manufacturer'],
                thumbnail=updated_product_data['thumbnail'],
                stock=updated_product_data['stock'],
                isInStock=True if updated_product_data['stock'] > 0 else False,
                paymentOption=updated_product_data['paymentOption']
            )
            updated_product.save()
            updated_product_details = ProductDetails(
                product_id_id=product_details.product_id,
                description=updated_product_data['description'],
                brand=updated_product_data['brand'],
                countryOfOrigin=updated_product_data['countryOfOrigin'],
                photos=updated_product_data['photos'],
                categories=updated_product_data['categories'],
                rating=updated_product_data['rating'],
                discount=updated_product_data['discount'],
                coupons=updated_product_data['coupons']
            )
            updated_product_details.save()
            return Response({'response': f'product(id:{product_id}) data has been successfully updated', 'status': True})
        else:
            return Response({'response': 'product did not updated as no product data received from request', 'status': False})
    else:
        return Response({'response': 'missing query parameter for product identification', 'status': False})


@api_view(['POST'])
@check_blacklist_token
def delete_product(request):
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
        return Response({'response': '(unauthorized access) User associated with received access token not found!', 'status': False})
    query_params = request.query_params
    if len(query_params) > 0 and 'id' in query_params and query_params['id'].isdigit:
        product_id = int(query_params['id'])
        product = Product.objects.filter(productId=product_id).first()
        if not product:
            return Response({'response': 'given product does not exists', 'status': False})
        print(f"[+] deleting product(id:{product.productId} , name:{product.name}) ")
        product.delete()
        return Response({'response': 'product successfully deleted', 'status': True})
    else:
        return Response({'response': 'missing query parameter of product identity in request', 'status': False})
