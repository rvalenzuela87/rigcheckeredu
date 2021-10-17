import json
import os
import re

from collections import namedtuple, OrderedDict

CONF = None
DEF_CONF = None

# ##############################
#
# Read Configuration
#
# ##############################

def get_conf_file_path():
	conf_dir_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

	return os.path.join(conf_dir_path, "config", "config.json")


def get_def_conf_file_path():
	return os.path.join(os.path.dirname(__file__), "config", "default.json")


def get_conf():
	global CONF

	try:
		assert CONF is None
	except AssertionError:
		return CONF

	try:
		conf_file = open(get_conf_file_path(), 'r')
	except(RuntimeError, Exception):
		# A user configuration file doesn't exists. Therefore, resort to the default configuration
		CONF = get_def_conf()
	else:
		try:
			CONF = json.load(conf_file, object_pairs_hook=OrderedDict)
		except(ValueError, RuntimeError, Exception):
			conf_file.close()
			raise
		else:
			conf_file.close()

	return CONF


def get_def_conf():
	global DEF_CONF

	try:
		assert DEF_CONF is None
	except AssertionError:
		return DEF_CONF

	try:
		def_conf_file = open(get_def_conf_file_path(), 'r')
	except(RuntimeError, Exception):
		if os.path.exists(get_conf_file_path()) is False:
			raise FileNotFoundError("Unable to find a default configuration file, default.json")
		else:
			raise

	try:
		DEF_CONF = json.load(def_conf_file, object_pairs_hook=OrderedDict)
	except(RuntimeError, Exception):
		# A default configuration doesn't exist. Raise the appropriate exception
		def_conf_file.close()
		raise RuntimeError("File default.json doesn't contain a valid JSON")

	def_conf_file.close()
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


# ##############################
#
# Modify Configuration
#
# ##############################


def reset_conf_to_default():
	# Assume a custom config file already exists or create a new one, otherwise
	try:
		config_file = open(get_conf_file_path(), 'w')
	except(RuntimeError, Exception):
		raise

	try:
		json.dump(get_def_conf(), config_file, indent=2, sort_keys=False)
	except(RuntimeError, Exception):
		config_file.close()
		raise

	# Force the configuration to reload
	global CONF

	CONF = None
	config_file.close()

	return True


def save_conf(config):
	mod_conf = get_conf()

	for k in config.keys():
		mod_conf[k] = config[k]

	try:
		conf_file = open(get_conf_file_path(), 'w')
	except(RuntimeError, Exception):
		raise

	try:
		json.dump(mod_conf, conf_file, sort_keys=False, indent=2)
	except(RuntimeError, Exception):
		conf_file.close()
		raise

	# Force the configuration to reload
	global CONF

	CONF = None
	conf_file.close()

	return True


def reload_conf():
	global CONF

	CONF = None

	return get_conf()


def reload_def_conf():
	global DEF_CONF

	DEF_CONF = None

	return get_def_conf()
