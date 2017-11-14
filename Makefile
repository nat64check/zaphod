.PHONY: help graph reset-db

help:
	@echo "Available make targets:"
	@echo "- graph"
	@echo "- reset-db"

graph: zaphod.png

zaphod.png: */models.py
	./manage.py graph_models --output zaphod.png --disable-sort-fields --group-models instances measurements world

reset-db:
	./manage.py reset_db
	./manage.py migrate
	./manage.py loaddata initial
