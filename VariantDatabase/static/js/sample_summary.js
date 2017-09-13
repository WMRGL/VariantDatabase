/*
Sample Summary Javascript - For the page sample_summary.html

- Contains the following:

1) An ajax function for collecting extar data when a user clicks on a row
2) Code for a button which toggles coverage data
3) Code for a select all button - This selects all options in the FilterForm
4) Code to activate the popover for exac data
5) Code for HTML DataTables plugin - https://datatables.net/


*/







$(document).ready(function(){


	//DataTable Initialisation 
	var variant_table = $('#variant_table').DataTable({
		"searching": false, "lengthChange": false, "scrollY":"600px", "paging": false, "info": false, "colReorder": true,"order": [],
		 "columnDefs": [

						{

						targets: [0,1,2,3,4,5],
						className: 'noVis'

						},

						{

						targets:[13,14,15,16],
						visible:false



					}]
	});

	// column filter button for datatable - This moves the button group to a custom area
	var buttons = new $.fn.dataTable.Buttons(variant_table, {
	buttons: [{

		extend:'colvis', columns: ':not(.noVis)'}]}).container().appendTo($('#button_group'));





	//Row click function
	$(".variant").click(function(){


		//add colour to selected row	
		var variant_hash  = $(this).children().eq(0).text(); //get hash from row 0
		var sample_pk = $("#sample_pk").text(); //get sample_pk from div



		var selected = $(this).hasClass("success");
		$(this).siblings().removeClass("success");


		if(!selected){
			$(this).addClass("success");
		
			//Now we do the ajax
			$.ajax({
				url: '/ajax/ajax_detail',
				type: 'get',
				data: {"variant_hash" : variant_hash, 'sample_pk': sample_pk},
				success: function(data) {

					$("#detail").html(data);

					},
				failure: function(data) { 

					alert('Got an error dude');

					}

					});


		};



      });

 function format(value) {
      return '<div>Hidden Value: ' + value + '</div>';
  }



      // Add event listener for opening and closing details
      $('#variant_table').on('click', 'td.details-control', function () {
          var tr = $(this).closest('tr');
          var row = variant_table.row(tr);

          if (row.child.isShown()) {
              // This row is already open - close it
              row.child.hide();
              tr.removeClass('shown');
          } else {
              // Open this row
              row.child(format('hi')).show();
              tr.addClass('shown');
          }
      });























	$("#togglecovdata").click(function(){ //toggle coverage columns with only raw data i.e. not percentages

		$(".hidecol").toggle();

	});

	$("#selectall").click(function(){ //This function selects everything in the filter_form form


		$("#id_upstream_gene_variant").prop("checked", true);
		$("#id_transcript_amplification").prop("checked", true);
		$("#id_transcript_ablation").prop("checked", true);
		$("#id_synonymous_variant").prop("checked", true);
		$("#id_stop_retained_variant").prop("checked", true);
		$("#id_stop_lost").prop("checked", true);
		$("#id_stop_gained").prop("checked", true);
		$("#id_start_lost").prop("checked", true);
		$("#id_splice_region_variant").prop("checked", true);
		$("#id_splice_donor_variant").prop("checked", true);
		$("#id_splice_acceptor_variant").prop("checked", true);
		$("#id_regulatory_region_variant").prop("checked", true);
		$("#id_regulatory_region_amplification").prop("checked", true);
		$("#id_regulatory_region_ablation").prop("checked", true);
		$("#id_protein_altering_variant").prop("checked", true);
		$("#id_non_coding_transcript_variant").prop("checked", true);
		$("#id_non_coding_transcript_exon_variant").prop("checked", true);
		$("#id_missense_variant").prop("checked", true);
		$("#id_mature_miRNA_variant").prop("checked", true);
		$("#id_intron_variant").prop("checked", true);
		$("#id_intergenic_variant").prop("checked", true);
		$("#id_inframe_insertion").prop("checked", true);
		$("#id_inframe_deletion").prop("checked", true);
		$("#id_incomplete_terminal_codon_variant").prop("checked", true);
		$("#id_frameshift_variant").prop("checked", true);
		$("#id_feature_truncation").prop("checked", true);
		$("#id_feature_elongation").prop("checked", true);
		$("#id_downstream_gene_variant").prop("checked", true);
		$("#id_coding_sequence_variant").prop("checked", true);
		$("#id_TF_binding_site_variant").prop("checked", true);
		$("#id_TFBS_amplification").prop("checked", true);
		$("#id_TFBS_ablation").prop("checked", true);
		$("#id_NMD_transcript_variant").prop("checked", true);
		$("#id_five_prime_UTR_variant").prop("checked", true);
		$("#id_three_prime_UTR_variant").prop("checked", true);

		$("#id_freq_max_af").val(1);


	});


	//popover for ExaC frequencies
	$('.exac').popover({title: "", content: "", html: true, placement: "top",trigger: "hover"});  










});