.PHONY: install run

install:
	# clone selfspy
	-git clone https://github.com/JamesGuthrie/selfspy.git
	# install selfspy
	cd selfspy && python setup.py install
	# install tccutil (used for altering the accessibility db)
	brew install tccutil
	# Add python, selfspy and iterm2 to the accessibility db
	@echo "\ntccutil will ask you for your root password in order to modify the accessibility database\n"
	sudo tccutil -i /usr/bin/python2.7
	sudo tccutil -i /usr/local/bin/selfspy
	sudo tccutil -i com.googlecode.iterm2

run:
	@echo "Sarting selfspy as a background process. To bring to foreground, run \`fg\`"
	@nohup selfspy -n &
