# datalogger
Generic data logging server head.


## Running the server
Defaults to port 3004

usage: datalogserver.py [-h] [-keyfile KEYFILE] [-certfile CERTFILE]
                        [--nocert] [-port PORT]

HTTP:
`python datalogserver.py --nocert`

HTTPS:
`python datalogserver.py -keyfile path/to/mykey.key -certfile path/to/mycert.crt`


## Logging data from the client
GET: `http[s]://myhost.com/log?mydata1=x&mydata2=y`

Stored in `datalog.txt` where the server is running, to change the outfile, edit the hard-coded variable at the top of `datahandler.py`.
