# Copyright (c) 2013 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.


from sgtk.platform import Application
import maya.cmds as cmds
import json
import os

class StgkPositionlistExport(Application):
	"""
	The app entry point. This class is responsible for intializing and tearing down
	the application, handle menu registration etc.
	"""
	
	def init_app(self):
		"""
		Called as the application is being initialized
		"""
		if self.context.entity is None:
			raise tank.TankError("Cannot load the Set Frame Range application! "
								 "Your current context does not have an entity (e.g. "
								 "a current Shot, current Asset etc). This app requires "
								 "an entity as part of the context in order to work.")

		self.engine.register_command("Export positionlist", self.run_app)
		
	'''
	def init_app(self):
		"""
		Called as the application is being initialized
		"""
		
		# first, we use the special import_module command to access the app module
		# that resides inside the python folder in the app. This is where the actual UI
		# and business logic of the app is kept. By using the import_module command,
		# toolkit's code reload mechanism will work properly.
		app_payload = self.import_module("app")
		
		# now register a *command*, which is normally a menu entry of some kind on a Shotgun
		# menu (but it depends on the engine). The engine will manage this command and 
		# whenever the user requests the command, it will call out to the callback.

		# first, set up our callback, calling out to a method inside the app module contained
		# in the python folder of the app
		menu_callback = lambda : app_payload.positionExtractMaya.createPositionlist()

		# now register the command with the engine
		self.engine.register_command("Export positionlist", menu_callback)
	'''
		
	def destroy_app(self):
		self.log_debug("Destroying StgkPositionlistExport")

	def run_app(self):
		"""
		Callback from when the menu is clicked.
		"""		
		print "start"
		message = "Exported positionlist to \n"
		
		returnValue, path = createPositionlist()
		message += path

		print "end"
		
		# if new_in is None or new_out is None:
			# message =  "Shotgun has not yet been populated with \n"
			# message += "in and out frame data for this Shot."

		# present a pyside dialog
		# lazy import so that this script still loads in batch mode
		from tank.platform.qt import QtCore, QtGui
		QtGui.QMessageBox.information(None, "Position List Exported", message)

		
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
	tempData, tempPath = retrieveDataFromSelection(allParents = childrenAndParentsDict, allTypes = typeDict)
	return tempData, tempPath
	
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
	return jsonData, targetPath
		
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
