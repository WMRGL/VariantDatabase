from django.shortcuts import render, get_object_or_404
from VariantDatabase.models import *
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def home_page(request):

	return render(request, 'VariantDatabase/home_page.html', {})

@login_required
def list_projects(request):

	all_projects = Project.objects.all()

	return render(request, 'VariantDatabase/list_projects.html', {'all_projects': all_projects} )

@login_required
def list_batches(request, pk):

	project = get_object_or_404(Project, pk=pk)

	batches_for_project = Batch.objects.filter(project=project)

	return render(request,'VariantDatabase/list_batches.html', {'batches_for_project': batches_for_project, 'project': project})


@login_required
def list_batch_samples(request, pk):

	batch = get_object_or_404(Batch, pk=pk)

	#project = get_object_or_404(Project, pk_project)

	samples_in_batch = Sample.objects.filter(batch = batch)

	return render(request, 'VariantDatabase/list_batch_samples.html', {'batch': batch, 'samples_in_batch' : samples_in_batch})


