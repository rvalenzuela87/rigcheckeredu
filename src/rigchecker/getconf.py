import json
import os
import re

from collections import namedtuple

CONF = None
DEF_CONF = None

def get_conf():
	global CONF

	try:
		assert CONF is None
	except AssertionError:
		return CONF

	conf_dir_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

	try:
		CONF = json.load(open(os.path.join(conf_dir_path, "config", "config.json")))
	except(RuntimeError, Exception):
		# A custom configuration file may not exist. Therefore, load the default configuration
		CONF = json.load(open(os.path.join(os.path.dirname(__file__), "config", "default.json")))

	return CONF


def get_def_conf():
	global DEF_CONF

	try:
		assert DEF_CONF is None
	except AssertionError:
		return DEF_CONF

	try:
		DEF_CONF = json.load(open(os.path.join(os.path.dirname(__file__), "config", "default.json")))
	except(RuntimeError, Exception):
		# A default configuration doesn't exist. Raise the appropriate exception
		raise RuntimeError("Unable to find a default configuration file, default.json")

	return DEF_CONF


# ##############################
# Geometry
# ##############################


def get_geo_suffix():
	try:
		return get_conf()["geo"]["suffix"]
	except KeyError:
		return get_def_conf()["geo"]["suffix"]


def get_geo_expression():
	try:
		geo_exp = re.compile(get_conf()["geo"]["exp"])
	except KeyError:
		geo_exp = re.compile(get_def_conf()["geo"]["exp"])

	try:
		return re.compile(geo_exp)
	except(ValueError, RuntimeError, Exception):
		return None


def get_geo_types():
	try:
		return get_conf()["geo"]["types"]
	except KeyError:
		return get_def_conf()["geo"]["types"]


def get_geo_discovery_methods():
	try:
		return get_conf()["geo"]["discovery_methods"]
	except KeyError:
		return get_def_conf()["geo"]["discovery_methods"]


def get_selected_geo_discovery_methods():
	try:
		return get_conf()["geo"]["selected_discovery_methods"]
	except KeyError:
		return get_def_conf()["geo"]["selected_discovery_methods"]


def get_geo_discovery_data():
	sel_discovery_methods = get_selected_geo_discovery_methods()

	GeoDiscoveryData = namedtuple("GeoDiscoveryData", sel_discovery_methods)
	discovery_data = []

	for m in sel_discovery_methods:
		if m == "suffix":
			discovery_data.append(get_geo_suffix())
		elif m == "expression":
			discovery_data.append(get_geo_expression())
		elif m == "type":
			discovery_data.append(get_geo_types())
		else:
			discovery_data.append(None)

	return GeoDiscoveryData.__new__(GeoDiscoveryData, *discovery_data)


# ##############################
# Joints
# ##############################


def get_joints_suffix():
	try:
		return get_conf()["joints"]["suffix"]
	except KeyError:
		return get_def_conf()["joints"]["suffix"]


def get_joints_expression():
	try:
		joints_exp = re.compile(get_conf()["joints"]["exp"])
	except KeyError:
		joints_exp = re.compile(get_def_conf()["joints"]["exp"])

	try:
		return re.compile(joints_exp)
	except(ValueError, RuntimeError, Exception):
		return None


def get_joints_types():
	try:
		return get_conf()["joints"]["types"]
	except KeyError:
		return get_def_conf()["joints"]["types"]


def get_joints_discovery_methods():
	try:
		return get_conf()["joints"]["discovery_methods"]
	except KeyError:
		return get_def_conf()["joints"]["discovery_methods"]


def get_selected_joints_discovery_methods():
	try:
		return get_conf()["joints"]["selected_discovery_methods"]
	except KeyError:
		return get_def_conf()["joints"]["selected_discovery_methods"]


def get_joints_discovery_data():
	sel_discovery_methods = get_selected_joints_discovery_methods()

	JointsDiscoveryData = namedtuple("JointsDiscoveryData", sel_discovery_methods)
	discovery_data = []

	for m in sel_discovery_methods:
		if m == "suffix":
			discovery_data.append(get_joints_suffix())
		elif m == "expression":
			discovery_data.append(get_joints_expression())
		elif m == "types":
			discovery_data.append(get_joints_types())
		else:
			discovery_data.append(None)

	return JointsDiscoveryData.__new__(JointsDiscoveryData, *discovery_data)

# ##############################
# Controls
# ##############################


def get_controls_suffix():
	try:
		return get_conf()["controls"]["suffix"]
	except KeyError:
		return get_def_conf()["controls"]["suffix"]


def get_controls_expression():
	try:
		controls_exp = re.compile(get_conf()["controls"]["exp"])
	except KeyError:
		controls_exp = re.compile(get_def_conf()["controls"]["exp"])

	try:
		return re.compile(controls_exp)
	except(ValueError, RuntimeError, Exception):
		return None


def get_controls_types():
	try:
		return get_conf()["controls"]["types"]
	except KeyError:
		return get_def_conf()["controls"]["types"]


def get_controls_discovery_methods():
	try:
		return get_conf()["controls"]["discovery_methods"]
	except KeyError:
		return get_def_conf()["controls"]["discovery_methods"]


def get_selected_controls_discovery_methods():
	try:
		return get_conf()["controls"]["selected_discovery_methods"]
	except KeyError:
		return get_def_conf()["controls"]["selected_discovery_methods"]


def get_controls_discovery_data():
	sel_discovery_methods = get_selected_controls_discovery_methods()

	ControlDiscoveryData = namedtuple("ControlDiscoveryData", sel_discovery_methods)
	discovery_data = []

	for m in sel_discovery_methods:
		if m == "suffix":
			discovery_data.append(get_controls_suffix())
		elif m == "expression":
			discovery_data.append(get_controls_expression())
		elif m == "types":
			discovery_data.append(get_controls_types())
		else:
			discovery_data.append(None)

	return ControlDiscoveryData.__new__(ControlDiscoveryData, *discovery_data)


# ##############################
# Offset Groups
# ##############################


def get_offset_groups_suffix():
	try:
		return get_conf()["controls"]["off_grp_suffix"]
	except KeyError:
		return get_def_conf()["controls"]["off_grp_suffix"]


def get_geo_group_suffix():
	try:
		return get_conf()["geo_group_suffix"]
	except KeyError:
		return get_def_conf()["geo_group_suffix"]


def get_rig_group_suffix():
	try:
		return get_conf()["rig_group_suffix"]
	except KeyError:
		return get_def_conf()["rig_group_suffix"]


'''def get_controls_types():
	try:
		return get_conf()["controls_types"]
	except KeyError:
		return get_def_conf()["controls_types"]'''


def get_offset_groups_expression():
	try:
		return re.compile(get_conf()["offset_groups_exp"])
	except KeyError:
		return re.compile(get_def_conf()["offset_groups_exp"])


def get_geo_group_expression():
	try:
		return re.compile(get_conf()["geo_group_exp"])
	except KeyError:
		return re.compile(get_def_conf()["geo_group_exp"])


def get_offset_groups_discovery_methods():
	try:
		return get_conf()["offset_groups_discovery_methods"]
	except KeyError:
		return get_def_conf()["offset_groups_discovery_methods"]


def get_selected_offset_groups_discovery_methods():
	try:
		return get_conf()["selected_offset_groups_discovery_methods"]
	except KeyError:
		return get_def_conf()["selected_offset_groups_discovery_methods"]


def get_geo_group_discovery_methods():
	try:
		return get_conf()["geo_group_discovery_methods"]
	except KeyError:
		return get_def_conf()["geo_group_discovery_methods"]


def get_selected_geo_group_discovery_methods():
	try:
		return get_conf()["selected_geo_group_discovery_methods"]
	except KeyError:
		return get_def_conf()["selected_geo_group_discovery_methods"]


def get_offset_groups_discovery_data():
	discovery_data = dict.fromkeys(get_selected_offset_groups_discovery_methods())

	for k in discovery_data:
		if k == "suffix":
			discovery_data[k] = get_offset_groups_suffix()
		elif k == "expression":
			discovery_data[k] = get_offset_groups_expression()

	return discovery_data


def get_geo_group_discovery_data():
	discovery_data = dict.fromkeys(get_selected_geo_group_discovery_methods())

	for k in discovery_data:
		if k == "suffix":
			discovery_data[k] = get_geo_group_suffix()
		elif k == "expression":
			discovery_data[k] = get_geo_group_expression()

	return discovery_data