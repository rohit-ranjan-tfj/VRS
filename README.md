# Welcome to Video Rental System!

The VRS was implemented as a course project under Prof. Abir Das and Prof. Sourangshu Bhattacharya for ``CS29202 SOFTWARE ENGINEERING LABORATORY`` in Spring '22. Check out our [presentation](Project_Presentation.pdf)!

## Run Instructions
```
$ sudo systemctl start elasticsearch.service
$ flask db migrate
$ flask db upgrade
$ flask run
```
## Install and Setup Instructions
[ElasticSearch Setup Instructions](https://stackoverflow.com/questions/39447617/failed-to-establish-a-new-connection-errno-111-connection-refusedelasticsear)
```
$ pip install -r requirements.txt
```
## Known issues with Elastic Search API
The API defaults to read-only mode for its index when disk space is low. Use the below commands to change the default behaviour. [Refer here for details](https://stackoverflow.com/questions/50609417/elasticsearch-error-cluster-block-exception-forbidden-12-index-read-only-all)

```
curl -XPUT -H "Content-Type: application/json" http://localhost:9200/_cluster/settings -d '{ "transient": { "cluster.routing.allocation.disk.threshold_enabled": false } }'
curl -XPUT -H "Content-Type: application/json" http://localhost:9200/_all/_settings -d '{"index.blocks.read_only_allow_delete": null}'
```
