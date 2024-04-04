# Kaze Docker - UAV Wind Simulation Testing Utility
## Build
In order to run Kaze, simply clone the repo, and run build the docker container...
```sh
git clone git@github.com:SUNY-BU-Software-Systems-Research-Group/Kaze-Docker.git
cd Kaze-Docker
sudo docker build .
```
## Run
Run the docker container. Here you can specify how many cpus you would like to give the container.
```sh
sudo docker run --cpus 8 -it <container_id>
```

Once inside the docker container, simply run the Kaze.py script with your generation filfe. An example generation file (with a population of 1) can be found at Kaze-Docker/Kaze/inputs/kaze/seed/seed_1.xml. Templates of generation files can be found at Kaze/templates/generation_1.template, Kaze/templates/generation_10.template (population of 1 and 10, respectively).
```sh
cd Kaze
python Kaze.py path/to/generation/file.xml
```

## Collecting Fitness Results
The results of a given run (a batch of one or more simulations), the results will be found in /var/batch_name/fitness.xml. This will be contain fitness results, with one entry for every entry in the input generation file. Each entry will contain two values; Position and Collision. Position refers to the Positional PCC calculated by comparing the simulation with its "windless" equivalent. Collision refers to if the drone went out of bounds, and collided with a building.
