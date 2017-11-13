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


	var user_settings = $('#user_settings').text().trim();

	var temp = new Array();

	temp = user_settings.split(",");

	console.log(temp);

	


	var variant_table = $('#variant_table').DataTable({
		"searching": false, "lengthChange": false, "scrollY":"600px","scrollX": true, "autoWidth": false, "paging": false, "info": false, "colReorder": true,"order": [],
		 "columnDefs": [

						{

						targets: ['variant_hash','expand_box','variant_desc','reference','alt'],
						className: 'noVis'

						},

						{

						targets: temp  ,
						visible: false



					}]
	});




	// column filter button for datatable - This moves the button group to a custom area
	var buttons = new $.fn.dataTable.Buttons(variant_table, {
	buttons: [{

		extend:'colvis', columns: ':not(.noVis)'}]}).container().appendTo($('#button_group'));





	//Row click function
	$(".get_detail").click(function(){


		//add colour to selected row	
		var variant_hash  = $(this).siblings('td.variant_hash.noVis').eq(0).text(); //get hash from row 0
		var sample_pk = $("#sample_pk").text(); //get sample_pk from div
		console.log(variant_hash)


		var selected = $(this).parent().hasClass("success");
		$(this).parent().siblings().removeClass("success");


		if(!selected){
			$(this).parent().addClass("success");
		
			//Now we do the ajax
			$.ajax({
				url: '/ajax/ajax_detail',
				type: 'get',
				data: {"variant_hash" : variant_hash, 'sample_pk': sample_pk},
				success: function(data) {

					$("#detail").html(data);

					},
				failure: function(data) { 

					alert('Got an error');

					}

					});


		};



      });

 function format(value) {
      return '<div>Hidden Value: ' + value + '</div>';
  }



      // Add event listener for opening and closing details
      $('#variant_table').on('click', 'td.details-control', function () {


      	var variant_hash  = $(this).siblings('td.variant_hash.noVis').eq(0).text(); //get hash from row 0
		
		
		var tr = $(this).closest('tr');
		var row = variant_table.row(tr);

		if (row.child.isShown()) {
		// This row is already open - close it
			row.child.hide();
			tr.removeClass('shown');
			} else {
			// Open this row


			console.log(variant_hash)
			
			$.ajax({
			url: '/ajax/ajax_table_expand',
			type: 'get',
			data: {"variant_hash" : variant_hash},
			success: function(data) {

			row.child(data).show();
            tr.addClass('shown');

			},
			failure: function(data) { 

			alert('Got an error');

			}

			});



          }
      });




	$("#togglecovdata").click(function(){ //toggle coverage columns with only raw data i.e. not percentages

		$(".hidecol").toggle();

	});

	$("#selectall").click(function(){ //This function selects everything in the filter_form form


		var check_box = $("#id_consequences.selectmultiple.form-control").children();

		for (i=0; i <check_box.length; i++){


			check_box[i].selected =true;


		}

		var frequency_box = $("#id_max_af");

		frequency_box.val(1.0);



	});


	//popover for ExaC frequencies
	$('.exac').popover({title: "", content: "", html: true, placement: "top",trigger: "hover"});  









});