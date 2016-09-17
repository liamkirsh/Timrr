.PHONY: install

install:
	# install Tkinter bindings for selfspy to work
	sudo apt-get install python-tk

	# create virtualenv & install dependencies
	virtualenv --no-site-packages env
	env/bin/pip install -r requirements.txt
