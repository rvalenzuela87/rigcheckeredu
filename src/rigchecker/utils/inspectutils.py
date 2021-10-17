import maya.api.OpenMaya as om
import maya.cmds as cmds

from .. import getconf

reload(getconf)

maya_useNewAPI = True

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
	Returns a generator for all the shape nodes in the scene.

	@return: (MObject,...)
	@rtype: generator
	"""

	geo_ref_sel_list = om.MSelectionList()
	map(geo_ref_sel_list.add, cmds.ls(type="mesh"))

	for shape_node in (geo_ref_sel_list.getDependNode(i) for i in xrange(geo_ref_sel_list.length())):
		yield shape_node


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


@get_node_reference_decorator
def geo_is_skinned(geo_node):
	geo_dag_fn = om.MFnDagNode(geo_node)

	try:
		if geo_node.hasFn(om.MFn.kTransform) is True:
			geo_node = geo_dag_fn.getPath().extendToShape(0).node()

		assert geo_node.hasFn(om.MFn.kShape) is True
	except AssertionError:
		raise ValueError("Unsupported type %s received as argument." % geo_node.apiTypeStr)
	else:
		geo_dag_fn.setObject(geo_node)

	try:
		input_geometry_plug = geo_dag_fn.findPlug("inMesh", False)
		assert input_geometry_plug is not None and input_geometry_plug.isNull is False
	except AssertionError:
		print("Shape type %s is not supported." % geo_node.apiTypeStr)

	shape_dep_graph_it = om.MItDependencyGraph(
		input_geometry_plug, om.MFn.kSkinClusterFilter,
		om.MItDependencyGraph.kUpstream, om.MItDependencyGraph.kDepthFirst
	)

	try:
		shape_dep_graph_it.currentNode()
	except(RuntimeError, Exception):
		return False
	else:
		return True


@get_node_reference_decorator
def geo_is_grouped(geo_node):
	geo_parent_dag_fn = om.MFnDagNode(geo_node)

	# Find the outermost parent for the mesh received as argument
	while geo_parent_dag_fn.parent(0).hasFn(om.MFn.kTransform):
		geo_parent_dag_fn.setObject(geo_parent_dag_fn.parent(0))

	# Retrieve the discovery information from the configuration file
	global GEO_GROUP_DISCOVERY_DATA

	if GEO_GROUP_DISCOVERY_DATA is None:
		GEO_GROUP_DISCOVERY_DATA = getconf.get_geo_group_discovery_data()

	try:
		GEO_GROUP_DISCOVERY_DATA["expression"].match(geo_parent_dag_fn.name()).group(0)
	except KeyError:
		# Expression is not a method of discovery. Therefore, ignore this error and continue on
		pass
	except AttributeError:
		return False

	try:
		assert geo_parent_dag_fn.name().endswith(GEO_GROUP_DISCOVERY_DATA["suffix"]) is True
	except KeyError:
		# Suffix is not a method of discovery. Therefore, ignore this error and continue on
		pass
	except AssertionError:
		return False

	return True


@get_node_reference_decorator
def geo_is_outside_control(geo_node):
	try:
		assert geo_node.hasFn(om.MFn.kMesh) is True
	except AssertionError:
		# Assume the node received as argument is a mesh's transform node
		geo_transform_node = geo_node
	else:
		# The node received as argument is a mesh. Therefore, retrieve its immediate parent node
		geo_transform_node = om.MFnDagNode(geo_node).parent(0)

	# Retrieve the mesh's transform's immediate parent
	geo_parent_dag_node = om.MFnDagNode(om.MFnDagNode(geo_transform_node).parent(0))

	# Make sure the mesh's transform's parent doesn't match the configuration file's specifications for an animation
	# control
	global CONTROLS_DISCOVERY_DATA

	if CONTROLS_DISCOVERY_DATA is None:
		CONTROLS_DISCOVERY_DATA = getconf.get_controls_discovery_data()

	try:
		assert CONTROLS_DISCOVERY_DATA["expression"].match(geo_parent_dag_node.name()) is None
	except AssertionError:
		return False
	except(KeyError, AttributeError):
		pass

	try:
		assert geo_parent_dag_node.name().endswith(CONTROLS_DISCOVERY_DATA["suffix"]) is False
	except AssertionError:
		return False
	except(KeyError, TypeError, RuntimeError):
		pass

	# Finally, make sure the mesh's transform's parent has no shape children. This will ensure the parent is a group
	# and not a shape's or group of shape's transform node
	for i in xrange(geo_parent_dag_node.childCount()):
		try:
			assert geo_parent_dag_node.child(i).hasFn(om.MFn.kTransform)
		except AssertionError:
			return False
	else:
		return True


@get_node_reference_decorator
def geo_is_not_constrained(geo_node):
	try:
		assert geo_node.hasFn(om.MFn.kMesh) is True
	except AssertionError:
		geo_transform_node = geo_node
	else:
		geo_transform_node = om.MFnDagNode(geo_node).parent(0)

	geo_transform_dag_fn = om.MFnDagNode(geo_transform_node)

	for i in xrange(geo_transform_dag_fn.childCount()):
		try:
			assert geo_transform_dag_fn.child(i).hasFn(om.MFn.kConstraint) is False
		except AssertionError:
			return False
	else:
		return True


@get_node_reference_decorator
def joint_is_hidden(joint_node):
	return not om.MFnDagNode(joint_node).getPath().isVisible()


@get_node_reference_decorator
def control_is_valid_type(control_node):
	control_dag_fn = om.MFnDagNode(control_node)

	global ACCEPTED_CONTROLS_TYPE

	if ACCEPTED_CONTROLS_TYPE is None:
		ACCEPTED_CONTROLS_TYPE = getconf.get_accepted_controls_type()

	try:
		assert control_node.hasFn(om.MFn.kShape) is True
	except AssertionError:
		# The node received as argument is not a shape node. Therefore, retrieve all of its shape nodes and check
		# if their type matches the accepted type for animation controls found in the configuration file

		for i in xrange(control_dag_fn.getPath().numberOfShapesDirectlyBelow()):
			try:
				assert cmds.nodeType(control_dag_fn.getPath().extendToShape(i).fullPathName()) == ACCEPTED_CONTROLS_TYPE
			except AssertionError:
				return False
		else:
			return True
	else:
		return cmds.nodeType(control_dag_fn.getPath().fullPathName()) == ACCEPTED_CONTROLS_TYPE


@get_node_reference_decorator
def control_has_offset_group(control_node):
	try:
		assert control_node.hasFn(om.MFn.kTransform) is True
	except AssertionError:
		# Assume the node received as argument is a shape node and retrieve its transform node
		control_node = om.MFnDagNode(control_node).parent(0)

	try:
		control_parent_dag_fn = om.MFnDagNode(om.MFnDagNode(control_node).parent(0))
	except(TypeError, RuntimeError, Exception):
		# The control node received as argument has no valid parent node
		return False

	# Retrieve the discovery data from the configuration file
	global OFFSET_GROUPS_DISCOVERY_DATA

	if OFFSET_GROUPS_DISCOVERY_DATA is None:
		OFFSET_GROUPS_DISCOVERY_DATA = getconf.get_offset_groups_discovery_data()

	try:
		assert OFFSET_GROUPS_DISCOVERY_DATA["expression"].match(control_parent_dag_fn.name()) is not None
	except AssertionError:
		# The name of the parent node of the node received as argument doesn't match the regular expression
		# found in the configuration file
		return False
	except(KeyError, RuntimeError):
		# Expression is not a method for discovering offset groups. Therefore, ignore it and continue on
		pass

	try:
		assert control_parent_dag_fn.name().endswith(OFFSET_GROUPS_DISCOVERY_DATA["suffix"]) is True
	except AssertionError:
		# The name of the parent node of the node received as argument doesn't end with the suffix found in the
		# configuration file
		return False
	except(KeyError, RuntimeError):
		# Suffix is not a method for discovering offset groups. Therefore, ignore it and continue on
		pass

	return True


@get_node_reference_decorator
def control_is_zeroed(control_node):
	try:
		assert control_node.hasFn(om.MFn.kTransform) is True
	except AssertionError:
		control_node = om.MFnDagNode(control_node).parent(0)

	control_dag_fn = om.MFnDagNode(control_node)
	control_path = control_dag_fn.fullPathName()

	for ta in ("%s%s" % (at, ax) for at in ("translate", "rotate", "scale") for ax in ("X", "Y", "Z")):
		try:
			assert cmds.getAttr("{}.{}".format(control_path, ta), lock=True) is False
		except AssertionError:
			continue

		if ta == "scale":
			default_value = 1.0
		else:
			default_value = 0.0

		try:
			assert cmds.getAttr("{}.{}".format(control_path, ta)) == default_value
		except AssertionError:
			return False
	else:
		return True


def all_geos_are_skinned():
	"""
	Asserts all geometry in the scene has a skin cluster node connected to it. An exception is raised if said condition
	is not met.

	@return: True if all the geos in the scene are skinned. False otherwise.
	@rtype: bool
	"""

	geo_ref_sel_list = om.MSelectionList()
	map(geo_ref_sel_list.add, cmds.ls(type="mesh"))

	non_skinned_geo_list = []
	shape_dag_fn = om.MFnDagNode()

	for shape_node in (geo_ref_sel_list.getDependNode(i) for i in xrange(geo_ref_sel_list.length())):
		try:
			if shape_node.hasFn(om.MFn.kTransform) is True:
				shape_node = om.MFnDagNode(shape_node).getPath().extendToShape(0)

			assert shape_node.hasFn(om.MFn.kShape) is True
		except AssertionError:
			raise ValueError("Unsupported type %s received as argument." % shape_node.apiTypeStr)

		try:
			input_geometry_plug = om.MFnDagNode(shape_node).findPlug("inMesh", False)
			assert input_geometry_plug is not None and input_geometry_plug.isNull is False
		except AssertionError:
			print("Shape type %s is not supported." % shape_node.apiTypeStr)
			continue

		shape_dep_graph_it = om.MItDependencyGraph(
			input_geometry_plug, om.MFn.kSkinClusterFilter,
			om.MItDependencyGraph.kUpstream, om.MItDependencyGraph.kDepthFirst
		)

		try:
			shape_dep_graph_it.currentNode()
		except(RuntimeError, Exception):
			shape_dag_fn.setObject(shape_node)
			non_skinned_geo_list.append(shape_dag_fn.name())

	print("\n".join(non_skinned_geo_list))


def all_geos_are_grouped():
	ungrouped_shape_nodes_list = []

	for geo in get_geos_in_scene_gen():
		try:
			assert geo_is_grouped(geo) is True
		except AssertionError:
			ungrouped_shape_nodes_list.append(geo)

	try:
		assert len(ungrouped_shape_nodes_list) == 0
	except AssertionError:
		return False
	else:
		return True


def all_geos_are_outside_controls():
	geos_in_controls = []

	for geo in get_geos_in_scene_gen():
		try:
			assert geo_is_outside_control(geo) is True
		except AssertionError:
			geos_in_controls.append(geo)

	try:
		assert len(geos_in_controls) == 0
	except AssertionError:
		return False
	else:
		return True


def all_geos_are_not_constrained():
	constrained_geos = []

	for geo in get_geos_in_scene_gen():
		try:
			assert geo_is_not_constrained(geo) is True
		except AssertionError:
			constrained_geos.append(geo)

	try:
		assert len(constrained_geos) == 0
	except AssertionError:
		return False
	else:
		return True


def all_joints_are_hidden():
	for joint in get_joints_in_scene_gen():
		try:
			assert joint_is_hidden(joint)
		except AssertionError:
			return False
	else:
		return True


def no_anim_curves_in_scene():
	return len(get_anim_curves_in_scene_list()) == 0


def all_controls_are_valid_type():
	non_curved_controls_list = []

	for control_node in get_controls_in_scene_gen():
		try:
			assert control_is_valid_type(control_node) is True
		except AssertionError:
			non_curved_controls_list.append(control_node)

	try:
		assert len(non_curved_controls_list) == 0
	except AssertionError:
		return False
	else:
		return True


def all_controls_are_zeroed():
	non_zeroed_list = []

	for control_node in get_controls_in_scene_gen():
		try:
			assert control_is_zeroed(control_node)
		except AssertionError:
			non_zeroed_list.append(control_node)

	try:
		assert len(non_zeroed_list) == 0
	except AssertionError:
		return False
	else:
		return True


def all_controls_have_offset_groups():
	no_offset_groups_list = []

	for control_node in get_controls_in_scene_gen():
		try:
			assert control_has_offset_group(control_node) is True
		except AssertionError:
			no_offset_groups_list.append(control_node)

	try:
		assert len(no_offset_groups_list) == 0
	except AssertionError:
		return False
	else:
		return True
