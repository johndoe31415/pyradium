#	pyradium - HTML presentation/slide show generator
#	Copyright (C) 2015-2023 Johannes Bauer
#
#	This file is part of pyradium.
#
#	pyradium is free software; you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation; this program is ONLY licensed under
#	version 3 of the License, later versions are explicitly excluded.
#
#	pyradium is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with pyradium; if not, write to the Free Software
#	Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#	Johannes Bauer <JohannesBauer@gmx.de>

import logging
import subprocess
import datetime
from .Exceptions import DeploymentException
from .CmdlineEscape import CmdlineEscape

_log = logging.getLogger(__spec__.name)

class Deployment():
	def __init__(self, deployment_configuration: dict, presentation_directory: str):
		self._deployment_configuration = deployment_configuration
		self._presentation_directory = presentation_directory

	def deploy(self, configuration_name: str):
		_log.debug("Executing deployment configuration: %s", configuration_name)
		if configuration_name not in self._deployment_configuration:
			raise DeploymentException(f"No such deployment configuration: {configuration_name}")

		target_config = self._deployment_configuration[configuration_name]
		if "available" in target_config:
			try:
				ts = datetime.datetime.strptime(target_config["available"], "%Y-%m-%d %H:%M:%S")
			except ValueError as e:
				raise DeploymentException(f"Deployment configuration {configuration_name} has invalid format for 'available' datetime: {target_config['available']}. Expecting format \"YYYY-mm-dd HH:MM:SS\".") from e
			if "not_available_redirect" in target_config:
				redirect = target_config["not_available_redirect"]
			else:
				redirect = "/not_available_yet.html"
			with open(self._presentation_directory + "/.htaccess", "w") as f:
				if "access_key" in target_config:
					print("# If access key is set in query string, set the access_key cookie", file = f)
					print(f"RewriteCond %{{QUERY_STRING}} ^{target_config['access_key']}$", file = f)
					print(f"RewriteRule ^ - [CO=access_key:{target_config['access_key']}:%{{HTTP_HOST}}] [L]", file = f)
					print(file = f)

				if "access_key" not in target_config:
					print("# If too soon, redirect to 'not available' page", file = f)
				else:
					print("# If too soon, access_key query string is not set and access_key cookie is not set, redirect to 'not available' page", file = f)
				print(f"RewriteCond %{{TIME}} <{ts.strftime('%Y%m%d%H%M%S')}", file = f)
				if "access_key" in target_config:
					print(f"RewriteCond %{{QUERY_STRING}} !^{target_config['access_key']}$", file = f)
					print(f"RewriteCond %{{HTTP_COOKIE}} !access_key={target_config['access_key']}", file = f)
				print(f"RewriteRule ^ {redirect} [R=307]", file = f)

		cmd = [ "rsync", "-a", "--mkpath", "--delete", "--chmod=D755,F644", self._presentation_directory + "/", target_config["remote_target"] ]
		_log.debug("Synchronizing via rsync: %s", CmdlineEscape().cmdline(cmd))
		try:
			subprocess.check_call(cmd)
		except subprocess.CalledProcessError as e:
			raise DeploymentException("Deployment {configuration_name} failed to successfully execute rsync: {CmdlineEscape().cmdline(cmd)}") from e
		_log.info("Successully deployed deployment configuration \"%s\".", configuration_name)

	def deploy_all(self):
		for configuration_name in self._deployment_configuration:
			self.deploy(configuration_name)
