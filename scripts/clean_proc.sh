kill -9 $(ps aux | grep -e /home/rti/Kaze-Docker/ws/paparazzi/var/aircrafts/ardrone2/nps/simsitl | awk '{ print $2 }')
kill -9 $(ps aux | grep -e paparazzi | awk '{ print $2 }')
kill -9 $(ps aux | grep -e simsitl | awk '{ print $2 }')
kill -9 $(ps aux | grep -e nps | awk '{ print $2 }')
