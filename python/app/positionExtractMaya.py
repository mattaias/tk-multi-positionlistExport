import maya.cmds as cmds
import json
import os


def superPrint(stringInput):
	stringTemp = "%s %s %s" %('#'*10,stringInput,'#'*10)
	print stringTemp
	
def setAssetDict(name, longName, asset, assetType, animated, position, rotation, scale, parentAssets = []):
	tempDict = {}
	tempDict["name"] = name
	tempDict["longName"] = longName
	tempDict["asset"] = asset
	tempDict["assetType"] = assetType
	tempDict["animated"] = animated
	tempDict["position"] = position
	tempDict["rotation"] = rotation
	tempDict["scale"] = scale
	tempDict["parentAssets"] = parentAssets
	return name, tempDict

def createPositionlist():
	childrenAndParentsDict, typeDict = getAllParentsAndTypeDict(cmds.listRelatives(cmds.ls(type = "locator") ,parent = True, type = "transform"))
	cmds.select(getMainSceneObjects())
	retrieveDataFromSelection(allParents = childrenAndParentsDict, allTypes = typeDict)
	
def getAllParentsAndTypeDict(objectList = None):
	childrenAndParentsDict = {}
	
	if objectList == None:
		objectList = cmds.listRelatives(cmds.ls(type = "locator") ,parent = True, type = "transform")
	typeDict = {}
	parentsDict = {}
	for obj in objectList:
		if obj not in typeDict:
			typeDict[str(obj)] = "Prop"
		tempParent = cmds.listRelatives(obj, parent = True)
		if tempParent != None:
			typeDict[str(tempParent[0])] = "Set"
			parentsDict[str(obj)] = str(tempParent[0])
		
	for obj in objectList:
		parentList = []
		newChild = obj
		while str(newChild) in parentsDict:
			parent = parentsDict[str(newChild)]
			parentList.append(parent)
			newChild = parent
		childrenAndParentsDict[str(obj)] = parentList
	return childrenAndParentsDict, typeDict
	
def getMainSceneObjects():
	sceneObjects = cmds.listRelatives(cmds.ls(type = "locator") ,allParents = True, type = "transform")
	
	mainObjectsList = []
	for obj in sceneObjects:
		if cmds.listRelatives(obj, allParents = True, type = "transform") == None:
			mainObjectsList.append(obj)
	# print mainObjectsList
	return mainObjectsList
	
def getDataFolder():
	targetPath = getFileName()
	print targetPath
	splitPath = targetPath.split("/")
	print splitPath
	name = getAssetName()
	target = "%s/%s/%s/%s/%s/data/" %(splitPath[0],splitPath[1],splitPath[2],splitPath[3],name)
	return target

def retrieveDataFromSelection(allTypes = None, allParents = None):
	transformDataDict = {}
	selected = cmds.ls(sl = True)
	print allParents
	print allTypes
	for obj in selected:
		print obj
		print str(obj)
		assetType = None
		parents = []
		if allTypes != None:
			if str(obj) in allTypes:
				assetType = allTypes[str(obj)]
		if allParents != None:
			if str(obj) in allParents:
				print "FOUND in ALLPARENTS"
				parents = allParents[str(obj)]
		tempName, tempOutput = getObjectData(obj, parents = parents, assetType = assetType)
		transformDataDict[tempName] = tempOutput
		
	targetPath = "%spositionlist.txt" %(getDataFolder())
	jsonData = saveJsonPositionList(transformDataDict, targetPath)
	return jsonData
		
def getFileName():
	return cmds.file(q=True,sceneName=True)
		
def getAssetName():
	quickName = getFileName()
	tempSplit = quickName.split("/")
	if len(tempSplit) > 4:
		return tempSplit[4]
	else:
		return None
		
def getSceneName():
	quickName = getFileName()
	tempSplit = quickName.split("/")
	if len(tempSplit) > 4:
		return tempSplit[4]
	else:
		return None
		
def getParentsOfObject(object):
	return cmds.listRelatives(object, parent = True)
		
def checkForChildren(object):
	tempChildren = cmds.listRelatives(object, allDescendents = True, type = "locator")
	if tempChildren != None:
		return False
	return tempChildren
		
def getObjectData(object, parents = [], assetType = None):
	longName = str(object)
	asset = ""
	asset = longName[longName.rfind("_")+1 : ].strip("0123456789")
	name = longName[ longName.rfind("_")+1 : ]
	if assetType == None:
		assetType = "prop"
	mainParent = getSceneName()
	parents.append(mainParent)
	animated = ""
	position = cmds.xform(object, ws=True, q=True, t=True)
	rotation = cmds.xform(object, ws=True, q=True, ro=True)
	scale = cmds.xform(object, r=True, q=True, s=True)
	return setAssetDict(name, longName, asset, assetType, animated, position, rotation, scale, parents)
		
def saveJsonPositionList(input, targetPath = None):
	toBeSaved = json.dumps(input , sort_keys=True ,ensure_ascii=True)
	toBeSaved = toBeSaved[+1 : -1]
	toBeSaved = toBeSaved.replace("}, ","},\n")
	print toBeSaved
	
	if targetPath != None:
		if not os.path.exists(os.path.dirname(targetPath)):
			os.makedirs(os.path.dirname(targetPath))
			
		with open(targetPath, 'w') as file:
			file.write(toBeSaved)
	print "__________________ SAVE TO" + targetPath
	return toBeSaved
	
def loadJsonPositionList(input):
	data = "{%s}" %input
	# data = data.replace("},\n","}, ")
	return json.loads(data)
	
def main():
	superPrint("Start") 
	returnValue = createPositionlist()
	superPrint("End") 
	
	
if __name__ == "__main__":
	main()