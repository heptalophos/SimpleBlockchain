
Set the environment and start 3 instances
``powershell
$env:FLASK_APP=".\blockchain.py"
$env:FLASK_DEBUG=1
$env:WERKZEUG_DEBUG_PIN="off"

flask run -h localhost -p 5000
flask run -h localhost -p 5001
flask run -h localhost -p 5002
```

Register the nodes
```cmd
curl --request POST --url http://localhost:5000/nodes/register
curl --request POST --url http://localhost:5001/nodes/register
curl --request POST --url http://localhost:5002/nodes/register
```

Mine a few and create some transactions
```
curl --request GET --url http://127.0.0.1:5000/mine \
  --header 'content-type: application/json' \
  --data '{
	"sender": "efde26eee15148ee92c6cd394edd974e", 
	"receiver": "some-another-address", 
	"amount": 2
}'
curl --request GET --url http://127.0.0.1:5001/mine \
  --header 'content-type: application/json' \
  --data '{
	"sender": "efde26eee15148ee92c6cd394edd974e", 
	"receiver": "yet-another-address", 
	"amount": 2
}'
curl --request POST --url http://127.0.0.1:5000/transactions/new \
  --header 'content-type: application/json' \
  --data '{
	"sender": "efde26eee15148ee92c6cd394edd974e", 
	"receiver": "yet-another-address", 
	"amount": 2
}'
```

```

