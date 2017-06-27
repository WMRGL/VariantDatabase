from django.core.management.base import BaseCommand, CommandError
from VariantDatabase.models import *
from interop import py_interop_run_metrics, py_interop_run, py_interop_summary
from django.db import transaction

def get_read_lane_data(read, lane, summary):
    
    qc_data ={}
    
    yield_g = summary.at(read).at(lane).yield_g()
    density = summary.at(read).at(lane).density().mean()
    cluster_count_pf = summary.at(read).at(lane).cluster_count_pf().mean()
    cluster_count = summary.at(read).at(lane).cluster_count().mean()
    phasing = summary.at(read).at(lane).phasing().median()
    prephasing = summary.at(read).at(lane).prephasing().median()
    read_count = summary.at(read).at(lane).reads()
    reads_pf = summary.at(read).at(lane).reads_pf()
    percent_gt_q30 = summary.at(read).at(lane).percent_gt_q30()
    percent_aligned = summary.at(read).at(lane).percent_aligned().mean()
    error_rate = summary.at(read).at(lane).error_rate().mean()
    error_rate_35 = summary.at(read).at(lane).error_rate_35().mean()
    error_rate_50 = summary.at(read).at(lane).error_rate_50().mean()
    error_rate_75 = summary.at(read).at(lane).error_rate_75().mean()
    error_rate_100 = summary.at(read).at(lane).error_rate_100().mean()
    
    qc_data['read'] = read
    qc_data['lane'] = lane
    qc_data['yield_g'] = yield_g
    qc_data['density'] = density
    qc_data['cluster_count_pf'] = cluster_count_pf
    qc_data['cluster_count'] = cluster_count
    qc_data['phasing'] = phasing
    qc_data['prephasing'] = prephasing
    qc_data['read_count'] = read_count
    qc_data['reads_pf'] = reads_pf
    qc_data['percent_gt_q30'] = percent_gt_q30
    qc_data['percent_aligned'] = percent_aligned
    qc_data['error_rate'] = error_rate
    qc_data['error_rate_35'] = error_rate_35
    qc_data['error_rate_50'] = error_rate_50  
    qc_data['error_rate_75'] = error_rate_75
    qc_data['error_rate_100'] = error_rate_100
    
    
    return qc_data
    

def get_all_qc_data(summary):
    
    data =[]
    
    lane_count = summary.lane_count()
    read_count = summary.size()
    
    for read in range(read_count):
        
        for lane in range(lane_count):
        
            read_lane_data = get_read_lane_data(read, lane, summary)
            
            data.append(read_lane_data)
            
    return data


def get_summary(ngs_folder_path):

	run_folder = ngs_folder_path

	run_metrics = py_interop_run_metrics.run_metrics()
	valid_to_load = py_interop_run.uchar_vector(py_interop_run.MetricCount, 0)
	py_interop_run_metrics.list_summary_metrics_to_load(valid_to_load)

	run_folder = run_metrics.read(run_folder, valid_to_load)

	summary = py_interop_summary.run_summary()
	py_interop_summary.summarize_run_metrics(run_metrics, summary)

	return summary


class Command(BaseCommand):

	help = "import qc data from the InterOp folder of an illumina NGS run"

	def add_arguments(self, parser):

		parser.add_argument('ngs_folder_path', nargs =1, type = str)
		parser.add_argument('worksheet_pk', nargs =1, type = str)


	def handle(self, *args, **options):


		with transaction.atomic():


			ngs_folder_path = options['ngs_folder_path'][0]
			worksheet_pk =  options['worksheet_pk'][0]

			try:

				worksheet = Worksheet.objects.get(pk=worksheet_pk)

			except:

				raise CommandError('Could not find that Worksheet: Enter a number e.g.1-5')


			summary = get_summary(ngs_folder_path)

			qc_data = get_all_qc_data(summary)

			for read_lane in qc_data:

				read = read_lane['read']
				lane = read_lane['lane']
				yield_g = read_lane['yield_g']
				density = read_lane['density']
				cluster_count_pf = read_lane['cluster_count_pf']
				cluster_count = read_lane['cluster_count']
				phasing = read_lane['phasing']
				prephasing = read_lane['prephasing']
				read_count = read_lane['read_count']
				reads_pf = read_lane['reads_pf']
				percent_gt_q30 = read_lane['percent_gt_q30']
				percent_aligned = read_lane['percent_aligned']
				error_rate = read_lane['error_rate']
				error_rate_35 = read_lane['error_rate_35']
				error_rate_50 = read_lane['error_rate_50']
				error_rate_75 = read_lane['error_rate_75']
				error_rate_100 = read_lane['error_rate_100']

				new_qc_model = ReadLaneQuality(worksheet=worksheet,read=read, lane=lane, yield_g=yield_g,density=density,cluster_count_pf=cluster_count_pf, cluster_count=cluster_count,
												phasing=phasing, prephasing=prephasing, read_count=read_count, reads_pf=reads_pf,percent_gt_q30=percent_gt_q30,
												percent_aligned=percent_aligned,error_rate=error_rate,error_rate_35=error_rate_35,error_rate_75=error_rate_75,error_rate_100=error_rate_100)

				new_qc_model.save()


		self.stdout.write(self.style.SUCCESS('Complete'))