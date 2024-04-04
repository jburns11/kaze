export PAPARAZZI_SRC=/home/rti/kaze/paparazzi
export PAPARAZZI_HOME=/home/rti/kaze/paparazzi
export EXEC_PATH=$(pwd)/
cp ./paparazzi_diff/conf/conf.xml  $PAPARAZZI_HOME/conf/conf.xml
cp ./paparazzi_diff/conf/flight_plans/udales_sim.xml  $PAPARAZZI_HOME/conf/flight_plans/udales_sim.xml
bash clean_proc.sh 2>/dev/null
python Kaze/Kaze-NSGA.py ardrone2
