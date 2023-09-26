from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json
from .models import Robot


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

            # Check if a robot with the same model already exists
            if Robot.objects.filter(model=model).exists():
                robot = Robot(model=model, version=version, created=created, serial=serial)
                robot.save()
                return JsonResponse({'message': 'Existing model, robot have been created'}, status=201)

            # If robot is new model
            else:
                robot = Robot(model=model, version=version, created=created, serial=serial)
                robot.save()
                return JsonResponse({'message': 'New robot created successfully'}, status=201)

        except KeyError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
