
deps:
	sudo apt-get -y install ssmtp mailutils
	sudo pip3 install pika


SYSTEMD_SERVICE_DIR = /etc/systemd/system

install-doorbell-sensor: deps
	sudo cp ./etc/doorbell-sensor.service ${SYSTEMD_SERVICE_DIR}
	sudo systemctl enable doorbell-sensor.service
	sudo systemctl stop doorbell-sensor.service || true
	sudo systemctl start doorbell-sensor.service

install-doorbell-ringer: deps
	sudo cp ./etc/doorbell-ringer.service ${SYSTEMD_SERVICE_DIR}
	sudo systemctl enable doorbell-ringer.service
	sudo systemctl stop doorbell-ringer.service || true
	sudo systemctl start doorbell-ringer.service
