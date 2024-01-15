# Parser
Dota 2 replay parser expanding on [odota/parser](https://github.com/odota/parser) to create simplified textual representations of Dota 2 matches.

Quickstart
----
* Build the docker image  
``` docker build . --tag 'odota-parser'```
* Run the docker image  
``` docker run -d -p 5600:5600 --name odota-parser-container odota-parser```
* Run the parser  
``` cd demos/```  
```python parse_tournament.py --league-id 15728 --min-start-time 2023-01-01T07:00:00.000Z``` [Grab league-id from [OpenDota Explorer](https://www.opendota.com/explorer)]
