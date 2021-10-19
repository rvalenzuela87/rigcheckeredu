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
# Find
# ##############################


def get_suffix(title):
	try:
		return get_conf()["find"][title]["suffix"]
	except KeyError:
		try:
			return get_def_conf()["find"][title]["suffix"]
		except KeyError:
			return ""


def get_expression(title):
	try:
		geo_exp = get_conf()["find"][title]["exp"]
	except KeyError:
		try:
			geo_exp = get_def_conf()["find"][title]["exp"]
		except KeyError:
			return None

	try:
		return re.compile(geo_exp)
	except(ValueError, RuntimeError, Exception):
		return None


def get_types(title):
	try:
		return get_conf()["find"][title]["types"]
	except KeyError:
		try:
			return get_def_conf()["find"][title]["types"]
		except KeyError:
			return []


def get_discovery_methods(title):
	try:
		return get_conf()["find"][title]["discovery_methods"]
	except KeyError:
		try:
			return get_def_conf()["find"][title]["discovery_methods"]
		except KeyError:
			return []


def get_selected_discovery_methods(title):
	try:
		return get_conf()["find"][title]["selected_discovery_methods"]
	except KeyError:
		try:
			return get_def_conf()["find"][title]["selected_discovery_methods"]
		except KeyError:
			return []


def get_discovery_data(title):
	sel_discovery_methods = get_selected_discovery_methods(title)

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


# ##############################
#
# Modify Configuration
#
# ##############################


def get_icons_dir_path():
	return os.path.join(__file__, os.path.sep.join(["resource", "icons"]))
