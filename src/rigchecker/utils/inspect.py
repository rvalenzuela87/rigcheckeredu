import maya.api.OpenMaya as om
import maya.cmds as cmds

from .. import getconf

reload(getconf)

maya_useNewAPI = True

GEO_DISCOVERY_DATA = None
CONTROLS_DISCOVERY_DATA = None
ACCEPTED_CONTROLS_TYPE = None
OFFSET_GROUPS_DISCOVERY_DATA = None
GEO_GROUP_DISCOVERY_DATA = None


def get_node_reference_decorator(function):
	def decorated(node):
		try:
			assert type(node) is om.MObject
		except AssertionError:
			node_sel_list = om.MSelectionList()

			try:
				node_sel_list.add(node)
			except(RuntimeError, Exception):
				raise
			else:
				node = node_sel_list.getDependNode(0)

		return function(node)

	return decorated


def get_geos_in_scene_gen():
	"""
	Returns a generator for all the shape nodes in the scene which match the filters specified via the configuration
	file.

	@return: (MObject,...)
	@rtype: generator
	"""

	global GEO_DISCOVERY_DATA

	if GEO_DISCOVERY_DATA is None:
		GEO_DISCOVERY_DATA = getconf.get_geo_discovery_data()

	# Assume there is a types specification for finding geos in the scene
	try:
		geos_in_scene = cmds.ls(type=GEO_DISCOVERY_DATA.type, noIntermediate=True)
	except AttributeError:
		geos_in_scene = cmds.ls(noIntermediate=True)

	geo_ref_sel_list = om.MSelectionList()

	for geo_name in geos_in_scene:
		try:
			assert geo_name.endswith(GEO_DISCOVERY_DATA.suffix) is True
		except AttributeError:
			# There isn't a suffix specification for finding geos in the scene. Therefore, ignore this error and
			# continue on
			pass
		except AssertionError:
			continue

		try:
			assert GEO_DISCOVERY_DATA.exp.match(geo_name) is not None
		except AttributeError:
			# There isn't a suffix specification for finding geos in the scene. Therefore, ignore this error and
			# continue on
			pass
		except AssertionError:
			continue

		geo_ref_sel_list.clear()
		geo_ref_sel_list.add(geo_name)

		yield geo_ref_sel_list.getDependNode(0)


def get_geos_in_scene_list():
	"""
	Returns a list with references to all the shape nodes in the scene.

	@return: [MObject,...]
	@rtype: list
	"""

	return [geo for geo in get_geos_in_scene_gen()]


def get_anim_curves_in_scene_list():
	return cmds.ls(type=["animCurveTL", "animCurveTA", "animCurveTU"])


def get_controls_in_scene_gen():
	nodes_sel_list = om.MSelectionList()

	global CONTROLS_DISCOVERY_DATA

	if CONTROLS_DISCOVERY_DATA is None:
		CONTROLS_DISCOVERY_DATA = getconf.get_controls_discovery_data()

	for node_name in cmds.ls():
		# Assume controls_names_exp is not None
		try:
			assert CONTROLS_DISCOVERY_DATA["expression"].match(node_name) is not None
		except(KeyError, AttributeError):
			# Expressions is not a method of discovery. Therefore, ignore this error and continue on
			pass
		except AssertionError:
			# The current node name didn't satisfy the regular expressions. Therefore, ignore it and continue with
			# the next name
			continue

		# Assume controls_type is not None
		try:
			assert cmds.nodeType(node_name) == CONTROLS_DISCOVERY_DATA["type"]
		except AssertionError:
			# The node's type is not supported. Therefore, ignore it and continue with the next node name
			continue
		except(KeyError, ValueError):
			# Type is not a method of discovery. Therefore, ignore this error and continue on
			pass

		# Assume controls_suffix is not None
		try:
			assert node_name.endswith(CONTROLS_DISCOVERY_DATA["suffix"])
		except(KeyError, ValueError, RuntimeError):
			# Suffixes is not a method of discovery. Therefore, ignore this error and continue on
			pass
		except AssertionError:
			# The node name doesn't end with the suffix found in the configuration file. Therefore,
			# ignore it and continue with the next name
			continue

		nodes_sel_list.clear()
		nodes_sel_list.add(node_name)

		yield nodes_sel_list.getDependNode(0)


def get_controls_in_scene_list():
	return [n for n in get_controls_in_scene_gen()]


def get_joints_in_scene_gen():
	joints_sel_list = om.MSelectionList()

	for joint_name in cmds.ls(type="joint"):
		joints_sel_list.clear()
		joints_sel_list.add(joint_name)

		yield joints_sel_list.getDependNode(0)


def get_joints_in_scene_list():
	return [j for j in get_controls_in_scene_gen()]