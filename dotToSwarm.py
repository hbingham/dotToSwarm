import subprocess, os, time, sys


def fileToList(filename):
	fileOpen = open(filename)
	lines = fileOpen.readlines()
	return lines

def getServices(fileContent):
	retDict = dict()
	serviceList = list()
	for line in fileContent:
		if '->' in line:
			theServices = line.split('->')
			for service in theServices:
				if service not in serviceList:
					serviceList.append(service.strip())
	for service in serviceList:
		if '_' in service:
			theService = service.split('_')
			if theService[0] not in retDict:
				retDict[theService[0]] = 1
			else:
				replica = retDict[theService[0]]
				if int(theService[1]) > replica:
					retDict[theService[0]] = int(theService[1])
		elif service not in retDict:
			retDict[service] = 1
	return retDict

def totalNodes(services):
	total = -1
	for service in services:
		total = total + services[service]
	return total
				
def newManagerName(counter):
	retStr = 'manager' + str(counter)
	return retStr, counter + 1

def newWorkerName(counter):
	retStr = 'worker' + str(counter)
	return retStr, counter + 1


def createMachine(machineName):
	cmd_str = sudo + 'docker-machine create ' + machineName
	os.system(cmd_str)
	print("Successful, machine: " + machineName + " created.")

def getMachineIP(machineName):
	cmd_str = sudo + 'docker-machine ip ' + machineName
	theIP = subprocess.check_output(cmd_str, shell=True).strip()
	return theIP


def initSwarm(managerName):
	cmd_str = sudo + 'docker-machine ssh ' + managerName + ' ' + sudo + 'docker swarm init --advertise-addr ' + getMachineIP(managerName)
	retStr = subprocess.check_output(cmd_str, shell=True)
	print retStr


def joinWorkerToken(managerName):
	cmd_str =  sudo + 'docker-machine ssh ' + managerName + ' ' + sudo + 'docker swarm join-token worker -q'
	retStr = subprocess.check_output(cmd_str, shell=True).strip()
	return retStr

def swarmJoinWorker(managerName, workerName):
	token = joinWorkerToken(managerName)
	ip = getMachineIP(managerName)
	cmd_str = sudo + 'docker-machine ssh ' + workerName + ' ' + sudo + 'docker swarm join --token ' + token + ' ' + ip
	retStr = subprocess.check_output(cmd_str, shell=True).strip()
	return retStr

def runCassandra(services, managerName):
	replicas = 0
	for service in services:
		if service == 'cassandra':
			replicas = services[service]
			break
	cmd_str = sudo + 'docker-machine ssh ' + managerName+' '+sudo+'docker service create --replicas ' + str(replicas) + ' --name cassandra cassandra'
	retStr = subprocess.check_output(cmd_str, shell=True).rstrip()

def checkCassandra(managerName):
	cmd_str = sudo + 'docker-machine ssh ' + managerName + ' ' + sudo + 'docker service ps cassandra'
	retStr = subprocess.check_output(cmd_str, shell=True).rstrip()
	return retStr

if __name__ == "__main__":
	managerCounter = 1
	workerCounter = 1
	managerList = []
	workerList = []
	sudo = 'sudo '

	content = fileToList('e2e.dot')
	serviceDict = getServices(content)
	manager1, managerCounter = newManagerName(managerCounter)
	createMachine(manager1)
	initSwarm(manager1)
	for x in range(0, 2):
		thisWorker, workerCounter = newWorkerName(workerCounter)
		workerList.append(thisWorker)
		createMachine(thisWorker)

	for worker in workerList:
		swarmJoinWorker(manager1, worker)
	runCassandra(serviceDict, manager1)
	print checkCassandra(manager1)
	
	








