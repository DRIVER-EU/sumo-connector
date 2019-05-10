## Running the demo

For a video of the running demo check: [screencapture.zip](https://github.com/DRIVER-EU/sumo-connector/files/3166656/2019-05-10-14-34-01.zip)

First download the docker local i4cm test-bed repository to a folder on your machine: [https://github.com/DRIVER-EU/test-bed/tree/master/docker/local-i4cm](https://github.com/DRIVER-EU/test-bed/tree/master/docker/local-i4cm).

Start this test-bed variant by running 
``` bash
docker-compose up -d
```

It will start most services needed for the simulation-trial, including:
- Kafka-broker + UI ([http://localhost:3600](http://localhost:3600))
- Schema-registry + UI ([http://localhost:3601](http://localhost:3601))
- Time-service ([http://localhost:8100](http://localhost:8100))
- Trial management tool ([http://localhost:3000](http://localhost:3000))
- Copper dashboard ([http://localhost:8080](http://localhost:8080))
- Copper server ([http://localhost:3007](http://localhost:3007))
- LCMS-connector ([http://localhost:8500](http://localhost:8500))
- After Action Review tool ([http://localhost:8095](http://localhost:8095))

Connect additional simulators to the broker on http://localhost:3501 and the schema-registry at http://localhost:3501.

### Setting up the demo

-------------------------------------
Open a browser window with the Copper dashboard at http://localhost:8080 and enable the Simulation group layers.
![coppert1](https://user-images.githubusercontent.com/11523459/57529161-7f22ee00-7334-11e9-833b-22089790f49b.jpg)

-------------------------------------

Open another browser window with the Trial Management Tool (TMT) dashboard at http://localhost:3000. First, import the [exported sqlite file](https://github.com/DRIVER-EU/test-bed/blob/master/docker/local-i4cm/tmt-data/trial_2f670b5c-6ec0-4b70-9e87-92252d305d6e.sqlite3?raw=true) by clicking the green '+'-button and then 'upload existing trial'.
![coppert2](https://user-images.githubusercontent.com/11523459/57529348-fc4e6300-7334-11e9-9afd-c939532a2548.jpg)
![coppert3](https://user-images.githubusercontent.com/11523459/57529350-fd7f9000-7334-11e9-82de-c413833e1b0e.jpg)

-------------------------------------

Then open this trial by clicking the title.
![coppert4](https://user-images.githubusercontent.com/11523459/57529352-ff495380-7334-11e9-8a27-d1b5f968df1f.jpg)


-------------------------------------

### Starting the demo

-------------------------------------
Go to the 'Run' tab on the right to go into run mode.
![coppert5](https://user-images.githubusercontent.com/11523459/57530144-e80b6580-7336-11e9-8a38-24f3f8575c8e.jpg)

-------------------------------------
Connect to the test-bed by clicking the 'connect' switch.
![coppert6](https://user-images.githubusercontent.com/11523459/57530147-e93c9280-7336-11e9-87f1-d4b828c9eafa.jpg)

-------------------------------------
Initialize the scenario time
![coppert7](https://user-images.githubusercontent.com/11523459/57530150-ea6dbf80-7336-11e9-9054-5236adc69cc6.jpg)

-------------------------------------
Check the status tab to see which action have been taken. Actions with a check-mark have been finished, action with a pause-sign are on hold.
![coppert8](https://user-images.githubusercontent.com/11523459/57530152-eb9eec80-7336-11e9-8591-5a510cae93d3.jpg)

-------------------------------------
Open an action item that is on hold, and press 'Click here when ready' to continue with the selected action, in this case initializing SUMO.
![coppert9](https://user-images.githubusercontent.com/11523459/57530155-ec378300-7336-11e9-9742-cc0bf35e708c.jpg)

-------------------------------------
This will trigger an additional set of actions, e.g. to request a route from SUMO.
![coppert10](https://user-images.githubusercontent.com/11523459/57530158-ee014680-7336-11e9-8019-2bfc7cc8e716.jpg)

-------------------------------------
All actions, events and unit updates will be visible in the Copper dashboard.
![coppert11](https://user-images.githubusercontent.com/11523459/57530493-a4fdc200-7337-11e9-894b-4f10b1c5785a.jpg)
