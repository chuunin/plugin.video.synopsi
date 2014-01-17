import local_settings

live_conn = {
	'base_url': 'https://api.synopsi.tv/',
	'key': '59c53964b1013defcff0155f6e4d54a4',
	'secret': '487615d20b22cdce510fd3476ed84d924e2b0c45ce7c49dc621764e05fae0904',
	'rel_api_url': '1.0/',
	'username': local_settings.username,
	'password': local_settings.password,
	'device_id': 'd2a8e78f-408a-11e2-9b7d-9927c8ae50bb',
}

local_conn = {
	'base_url': 'http://crux.local:8000/',
	'key': '59c53964b1013defcff0155f6e4d54a4',
	'secret': '487615d20b22cdce510fd3476ed84d924e2b0c45ce7c49dc621764e05fae0904',
	'rel_api_url': 'api/public/1.0/',
	'username': local_settings.username,
	'password': local_settings.password,
	'device_id': 'd2a8e78f-408a-11e2-9b7d-9927c8ae50bb',
}


test_papi_conn = {
	'base_url': 'https://test-papi.synopsi.tv/',
	'key': 'e20e8f465f42e96d8340e81bfc48c757',
	'secret': '72ab379c50650f7aec044b14db306430a55f09a2da1eb8e40b297a54b30e4b4f',
	'rel_api_url': '1.0/',
	'username': local_settings.username,
	'password': local_settings.password,
	'device_id': 'd2a8e78f-408a-11e2-9b7d-9927c8ae50bb',
}



connection = local_conn
