from quiz import settings

def staticfiles(request):
	return {
		'STATIC_URL': settings.STATIC_URL,
	}
