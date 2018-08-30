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

	var user_settings_array = new Array();

	user_settings_array = user_settings.split(",");

	console.log(user_settings_array);

	


	var variant_table = $('#variant_table').DataTable({
		"searching": false, "lengthChange": false, "scrollY":"600px","scrollX": true, "autoWidth": false, "paging": false, "info": false, "colReorder": true,"order": [],
		 "columnDefs": [

						{

						targets: ['variant_hash','expand_box','variant_desc','reference','alt', 'check1'],
						className: 'noVis'

						},

						{

						targets: user_settings_array,
						visible: false

						}]

					




					
	});




	//Row click function
	$(".get_detail").click(function(){


		//add colour to selected row	
		var variant_hash  = $(this).siblings('td.variant_hash.noVis').eq(0).text(); //get hash from row 0
		var sample_pk = $("#sample_pk").text(); //get sample_pk from div


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



	//popover for ExaC frequencies
	$('.exac').popover({title: "", content: "", html: true, placement: "top",trigger: "hover"});  




	$("#submit_check").click(function(){ //submit check data e.g. classifications and hgvs


		var variant_classification_dict = {}

		var rows = $("#variant_table").children('tbody').children();


		for (var i =0; i<rows.length; i++){


			var variant_hash  = $(rows[i]).children('td.variant_hash.noVis').text();
			var variant_class = $(rows[i]).children('td.check').children().val();
			var user_hgvs = $(rows[i]).children('td.hgvs_check').children().val();


			variant_classification_dict[variant_hash] = [variant_class, user_hgvs];





		}


		console.log(variant_classification_dict)

		var sample_pk = $("#sample_pk").text();
		var report_pk = $("#report_pk").text();
		var check_number = $("#check_number").text();

		var formData = new FormData();

		formData.append('csrfmiddlewaretoken',document.getElementsByName('csrfmiddlewaretoken')[0].value );
		formData.append('classifications', JSON.stringify(variant_classification_dict));
		formData.append('sample_pk', sample_pk);
		formData.append('report_pk', report_pk);
		formData.append('check_number', check_number);




		$.ajax({
			url: '/ajax/ajax_receive_classification_data/',
			type: 'POST',
			data: formData,


			contentType: false, // NEEDED, DON'T OMIT THIS (requires jQuery 1.6+)
    		processData: false, // NEEDED, DON'T OMIT THIS

			success: function(data) {

			alert(data)

			window.location.replace('/sample/'+$.trim(sample_pk)+'/summary/');

			},
			failure: function(data) { 

			alert('Got an error');

			}

			});





	});




});