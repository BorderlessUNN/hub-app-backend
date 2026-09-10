import csv

from django.http import HttpResponse
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView

from accounts.imports import (
    CSV_COLUMNS,
    MemberImportPreviewSerializer,
    MemberImportConfirmSerializer,
    parse_and_classify_csv,
)
from accounts.permissions import IsSuperAdminUser
from helpers.responses import CustomResponse


class MemberImportTemplateView(APIView):
    """ Download a blank CSV template with the expected columns (Super Admin only). """
    permission_classes = [IsSuperAdminUser]

    def get(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="member_import_template.csv"'
        writer = csv.writer(response)
        writer.writerow(CSV_COLUMNS)
        return response


class MemberImportPreviewView(APIView):
    """
    Upload a CSV and get back a classification of every row (valid /
    duplicate / invalid) without writing anything (Super Admin only). The
    frontend renders this so the admin can resolve duplicates per row before
    confirming.
    """
    permission_classes = [IsSuperAdminUser]
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = MemberImportPreviewSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = parse_and_classify_csv(serializer.validated_data['file'])
        return CustomResponse(
            valid=True,
            msg="CSV parsed successfully",
            data=result,
        )


class MemberImportConfirmView(APIView):
    """
    Commit a resolved import: the frontend sends back the rows with a
    per-row action (create / update / skip) (Super Admin only).
    """
    permission_classes = [IsSuperAdminUser]
    serializer_class = MemberImportConfirmSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return CustomResponse(
            valid=True,
            msg="Member import completed",
            status=201,
            data=result,
        )
