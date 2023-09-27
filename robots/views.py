from django.http import JsonResponse
from django.http import HttpResponse

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required

from django.views import View
from .models import Robot

import json
from openpyxl import Workbook
from datetime import datetime, timedelta


@method_decorator(csrf_exempt, name='dispatch')
class RobotCreateView(View):
    def post(self, request):
        try:
            data = json.loads(request.body.decode('utf-8'))
            model = data['model']
            version = data['version']
            created = data['created']
            serial = f"{model}-{version}"

            # Check if creation data already exists
            if Robot.objects.filter(created=created, serial=serial).exists():
                return JsonResponse({'message': 'Robot already registered'}, status=400)

            # Check if robot with the same model already exists
            if Robot.objects.filter(model=model).exists():
                robot = Robot(model=model, version=version, created=created, serial=serial)
                robot.save()
                return JsonResponse({'message': 'Existing model, a robot has been created'}, status=201)

            # If robot is a new model
            else:
                robot = Robot(model=model, version=version, created=created, serial=serial)
                robot.save()
                return JsonResponse({'message': 'A new robot created successfully'}, status=201)

        except KeyError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


@staff_member_required
def generate_excel(request):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)

    # Create a new Excel workbook
    wb = Workbook()

    # Filter datetime
    robots = Robot.objects.filter(created__range=[start_date, end_date])

    # Query the database to retrieve unique robot models for the last week
    models = robots.values_list('model', flat=True).distinct()

    for model in models:
        # Create a new sheet for each model
        model_sheet = wb.create_sheet(title=model)
        model_sheet.append(["Модель", "Версия", "Количество за неделю"])

        # Filter models
        model_robots = Robot.objects.filter(created__range=[start_date, end_date], model=model)

        # Fill sheet with corresponding data
        for version in model_robots.values_list('version', flat=True).distinct():
            model_version_robots = model_robots.filter(version=version)
            robot_count = model_version_robots.count()
            model_sheet.append([model, version, robot_count])

    default_sheet = wb['Sheet']
    wb.remove(default_sheet)

    # Create an HTTP response with the Excel file
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=robot_production_summary.xlsx'
    wb.save(response)

    return response
