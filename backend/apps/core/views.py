"""Health and infrastructure endpoints for the SkillSwap API."""

from django.db import connection
from django.db.utils import OperationalError
from django.http import JsonResponse
from drf_spectacular.utils import extend_schema
from rest_framework import serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from config.settings import DEBUG


class HealthSerializer(serializers.Serializer):
    status = serializers.CharField()
    database = serializers.CharField()
    debug = serializers.BooleanField()


@extend_schema(
    responses={200: HealthSerializer},
)
@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """Report service and database health. Used by load balancers and CI."""
    database_ok = True
    try:
        connection.ensure_connection()
    except OperationalError:
        database_ok = False

    status_code = 200 if database_ok else 503
    payload = {
        'status': 'ok' if database_ok else 'degraded',
        'database': 'ok' if database_ok else 'unavailable',
        'debug': DEBUG,
    }
    return JsonResponse(payload, status=status_code)
