
deps:
	sudo apt-get -y install ssmtp mailutils
	sudo pip3 install pika


SYSTEMD_SERVICE_DIR = /etc/systemd/system

install-doorbell-sensor: deps
	cp ./etc/doorbell-sensor.service ${SYSTEMD_SERVICE_DIR}
	systemctl enable doorbell-sensor.service
	systemctl stop doorbell-sensor.service || true
	systemctl start doorbell-sensor.service

install-doorbell-ringer: deps
	cp ./etc/doorbell-ringer.service ${SYSTEMD_SERVICE_DIR}
	systemctl enable doorbell-ringer.service
	systemctl stop doorbell-ringer.service || true
	systemctl start doorbell-ringer.service
