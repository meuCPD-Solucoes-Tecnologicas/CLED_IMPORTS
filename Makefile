SHELL := /bin/bash
build:
	cd dist;\
	source venv/bin/activate;\
	pip install --force-reinstall merm_orquestrador-0.1.*.whl;\
	cp -r 

get_merm_types:
	cd  merm_orquestrador;\
	ln -s -f merm-schema/merm-types.ts . 

generate_lambdazip:
	./new_version.sh


	
	