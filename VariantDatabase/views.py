from django.shortcuts import render, get_object_or_404
from VariantDatabase.models import *

# Create your views here.

def home_page(request):

	return render(request, 'VariantDatabase/home_page.html', {})


def list_projects(request):

	all_projects = Project.objects.all()

	return render(request, 'VariantDatabase/list_projects.html', {'all_projects': all_projects} )


def list_batches(request, pk):


	project = get_object_or_404(Project, pk=pk)

	batches_for_project = Batch.objects.filter(project=project)

	return render(request,'VariantDatabase/list_batches.html', {'batches_for_project': batches_for_project, 'project': project})

