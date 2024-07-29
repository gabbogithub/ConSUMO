# Overview
**ConSUMO** is a simple tool to evaluate mobile traffic impact on cell towers' load. It consists of three Python scripts written to be used with a SUMO simulation and a CSV file that contains the positions of some BTSs (base transceiver stations).

# Table of contents

- [Requirements](#requirements)
- [How to](#how-to)
- [Extraction script](#extraction-script)
- [Association script](#association-script)
- [Analysis script](#analysis-script)
- [Case study](#case-study)

# Requirements
To execute the scripts, aside from [SUMO](https://eclipse.dev/sumo/) and [Python](https://www.python.org/), you have to install some Python libraries. A requirements file is provided to quickly install all the libraries needed.
All you have to do is navigate to the cloned repository and type this command inside a shell:

```shell
pip install -r requirements.txt
```

What follows is a list of the requirements:
- **Pandas** version **2.2.2**.
- **Libsumo** version **1.20.0**.
- **Pyproj** version **3.6.1**.

> [!IMPORTANT]
> ConSUMO developers recomment to use SUMO version **1.20.0** and Python version **3.12**.

# How to
All the scripts have a variety of options that can be listes with the command **--help**. Some are required while others are optional.\
To execute a script, simply open a terminal and launch the Python interpreter followed by the path to the script with the required options and input files.

## Extraction script
This script extracts the cell sites located inside a certain city and writes them into a new file.

In order to use it, you have to specify the path to the input file with the **-i** or **--input** option and the name of the city to filter the cell sites
with the option **-c** or **--city**. This script was written to be used with [LTE ITALY](https://lteitaly.it) CSV files but could theoretically work with every CSV file that
has at least four columns with the following names: *node_id* (to uniquely identify sites), *cell_lat* (latitude of the site), *cell_long* (longitude of the site)
and *site_name* (column that has to contain the name of the city).

## Association script
This script maps a cell site to every vehicle in the simulation and regularly checks that the distance doesn't exceed a value given by the user. If it happens, a new association is computed.

In order to use it you have to specify the path to the SUMO configuration file with the option **-su** or **--sumo_cfg**. You will then need to provide the path to CSV file with the sites using the option **-i** or **--input** and the path to the net file with the option **-n** or **--sumo_net** (because it is used to convert from latitude and longitude to x and y values of the simulation). This script should work with every CSV file that follows this structure: first column *site id*, second column *site latitude* and third column *site longitude*. If you don't have a CSV file with the sites, you can still use the script using the option **-c** or **--cell_sites** to generate random cell sites and in this case the net file is not needed.

## Analysis script
This script analyses the results of the second script and extracts some metrics of interest.

Currently the tool can produce five different analysis:
- **-us/--users** : the number of users associated with a cell site at every timestamp. It requires an input file with the associations between vehicles and cell sites that uses commas as separators like the file produced by the second script and a file with the IDs of the sites such as the output of the first script.
- **-rt/--route-time** : the length of the route followed by every vehicle (in meters) and the time the vehicle remained in the simulation (in seconds). It requires an input file with the route length, the depart and arrival times and semicolon as separator. The suggested file to use is the output file produced by SUMO using the **--vehroute-output** option. Remember to convert it into a CSV file using the tool **xml2CSV.py**.
- **-si/--unique_sites** : the number of unique sites associated with the vehicles throughout the simulation. It requires an input file with the associations between vehicles and cell sites that uses commas as separators like the file produced by the second script.
- **-nc/--number_changes** : the number of times a vehicle changed site. The changes include when a vehicle that had an association with a site, drives too far from that site and no other sites is near enough to establish a connection. In other words it counts the number of times the state of the association of a vehicle changed. It requires an input file with the associations between vehicles and cell sites that uses commas as separators like the file produced by the second script.
- **-ns/--new_sites** : the most suitable roads to build new cell sites. The output will contains a row for each time a vehicle couldn't find a site near enough. Every row contains the edge id of the edge the vehicle was on, the position of the vehicle in longitude and latitude and a counter for the edge that represents the number of times a vehicle that couldn't find a cell site, was on that edge. The resulting file does not contain duplicated row (so if it happens multiple times that some vehicles in the same positions couldn't find a site, only one row will be saved). It requires two input files, the first one should have the associations between vehicles and sites, while the second one should contain the positions of every vehicle at every step. The former has to use commas as separators while the latter has to use semicolon. The suggested files to use are the output file from the second script and the output file produced by SUMO using the **--fcd-output** option. Remember to convert the second file into a CSV file using the tool **xml2CSV.py**.

# Case study
To test this tool we analyzed the mobile traffic inpact on the BTSs of Turin. To replicate the case study you have to follow four steps that will allow you to go from the raw data about Italian cell sites and a plain SUMO simulation of Turin to the results of the analysis.

> [!WARNING]
> The simulation's repository uses [Git LFS](https://git-lfs.com/), so be sure to set it up before before proceeding any further.

## Setup
The first step concerns the preparation of the data for the execution.\
The simulation can be download from a GitHub [repository](https://github.com/marcorapelli/TuSTScenario) with the command:

```shell
git clone https://github.com/marcorapelli/TuSTScenario.git
```

We will then need to download the data about the cell sites, which can be found on [LTE ITALY](https://lteitaly.it/) after signing up and going into the profile settings. In particular we are going to use the files from the NetMonitor database. 

## Extraction
Now we can extract the sites of interest.

```shell
python src/sites_extraction.py -i sites_file_path -c Torino -o extracted_sites.csv
```

After running this command, always check the output for weird sites that might have been left. For instance, the script included three incorrect sites in the end of the output when extracting the BTSs from the Vodafone file: the sites' names are Torino di Sangro instead of Torino and the coordinates are implausible.

## Execution
We are finally ready to run the main script with all the necessary data:

```shell
python src/sites_association.py -i extracted_sites.csv -t 86400 -s 180 -d 2000 -su TuSTScenario/Scenario/TuST.sumocfg -n TuSTScenario/Scenario/TuST.net.xml -o sites_associations.csv
```

The parameters have been tuned for this particular simulation.

## Analysis
There only remains to analyze the associations to gather some information about the usage of cell sites and about the simulation. Here is an example that illustrates how to obatin the number of users associated with a cell site at every timestamp:

```shell 
python src/sites_analysis.py -us -i sites_associations.csv extracted_sites.csv -o number_associations.csv
```

Remember to check the section [Analysis script](#analysis-script) to learn what analysis are available and what input they need.

# Contacts
You can contact the developers at the following email: 284745@studenti.unimore.it
