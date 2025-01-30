# from django.utils.deprecation import MiddlewareMixin
# import json
# import logging


# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#                     datefmt='%Y-%m-%d %H:%M:%S', filename='load_data.log')

# logger = logging.getLogger('basket')



# class CartMiddleware(MiddlewareMixin):
#     def process_request(self, request):
#         cart_data = request.COOKIES.get('cart')
#         if cart_data:
#             request.cart = json.loads(cart_data)
#             logger.info(f'Корзина загружена: {request.cart}')
#         else:
#             request.cart = {}
#             logger.info('Корзина пуста.')

#     def process_response(self, request, response):
#         if hasattr(request, 'cart'):
#             response.set_cookie('cart', json.dumps(request.cart), max_age=3600)  
#             logger.info(f'Корзина сохранена в cookies: {request.cart}')
#         return response
    