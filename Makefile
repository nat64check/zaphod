.PHONY: help graph reset-db

help:
	@echo "Available make targets:"
	@echo "- graph"
	@echo "- reset-db"

graph: zaphod.png

zaphod.png:
	./manage.py graph_models --output zaphod.png --disable-sort-fields --group-models zaphod

reset-db:
	./manage.py reset_db
	./manage.py migrate
	./manage.py loaddata initial
