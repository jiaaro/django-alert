# These targets are not files
.PHONY: test

test:
	DJANGO_SETTINGS_MODULE=test_project.settings python test_project/manage.py test alert_tests
