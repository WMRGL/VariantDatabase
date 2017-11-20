from rolepermissions.roles import AbstractUserRole


class Viewer(AbstractUserRole):

	available_permissions = {
		"change_view_filter" : True #Can user change the filter settings on the summary page
	}


class Analyst(AbstractUserRole):

	available_permissions ={
		"change_view_filter" : True,
		"create_report" : True,
		"complete_check": True,
		"approve_qc": True,
		"add_comment": True,


	}


class SeniorAnalyst(AbstractUserRole):

	available_permissions ={
		"change_view_filter" : True,
		"create_report" : True,
		"complete_check": True,
		"approve_qc": True,
		"add_comment": True,
		"resolve_differences": True,
		"create_panel": True,
		"edit_panel": True,
		"change_sample_panel": True

	}