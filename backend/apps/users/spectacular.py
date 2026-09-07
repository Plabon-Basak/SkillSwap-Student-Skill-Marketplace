"""OpenAPI security scheme bindings for drf-spectacular.

Registers a Bearer/JWT scheme so Swagger UI can authenticate against the
custom JWT authenticator used across the API.
"""

from drf_spectacular.extensions import OpenApiAuthenticationExtension


class UserJWTBearerScheme(OpenApiAuthenticationExtension):
    target_class = 'apps.users.authentication.UserJWTAuthentication'
    name = 'JWT'

    def get_security_definition(self, auto_schema):
        return {
            'type': 'http',
            'scheme': 'bearer',
            'bearerFormat': 'JWT',
        }
