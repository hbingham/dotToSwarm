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

def totalWorkers(services):
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

def createServices(services, managerName):
	replicas = 0
	localServices = []

	for service in services:
		if isOfficialService(service):
			replicas = services[service]
			cmd_end = service + ' ' + service
			cmd_str = sudo+'docker-machine ssh '+managerName+' '+sudo+'docker service create --replicas ' + str(replicas) + ' --name ' + cmd_end
			cmdReply = subprocess.check_output(cmd_str, shell=True).strip()
			print 'Created service: ' + service + ' from docker hub.'
		else:
			localServices.append(service)
	print 'Local services: ' + str(localServices)

def checkService(service, managerName):
	cmd_str = sudo + 'docker-machine ssh ' + managerName + ' ' + sudo + 'docker service ps ' + service
	retStr = subprocess.check_output(cmd_str, shell=True).rstrip()
	return retStr


def isOfficialService(service):
	cmd_str = sudo+"docker search --filter 'is-official=true' " + service
	retStr = subprocess.check_output(cmd_str, shell=True).strip()
	if service in retStr:
		return True
	else:
		return False


if __name__ == "__main__":
	endSwarm = False
	managerCounter = 1
	workerCounter = 1
	managerList = []
	workerList = []
	sudo = 'sudo '

	content = fileToList('e2eWithCache.dot')
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
	createServices(serviceDict, manager1)


	if endSwarm:
		cmd_str = sudo + 'docker-machine ssh ' + manager1 + ' ' + sudo + 'docker swarm leave --force'
		cmdRep = subprocess.check_output(cmd_str, shell=True).strip()
		for node in workerList:
			cmd_str = sudo + 'docker-machine ssh ' + node +' '+sudo+'docker swarm leave'
			cmdRep = subprocess.check_output(cmd_str, shell=True).strip()





