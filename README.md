# ParkNam-Back
# Usage

First you have to build the container :
```
docker build -t parknam:latest .
```
Then, you can launch it on the port 8000. 
```
docker run --name parknam -d -p 8000:8000 parknam:latest
```
After that, you can check the documentation on http://localhost:8000/docs
