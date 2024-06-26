# Copyright (c) 2013 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

import sgtk
from sgtk import Hook, TankError

import mari


class MariSceneOperations(Hook):
    """
    Breakdown operations for Mari.

    This implementation handles detection of mari geometry versions
    """

    def scan_scene(self):
        """
        The scan scene method is executed once at startup and its purpose is
        to analyze the current scene and return a list of references that are
        to be potentially operated on.

        The return data structure is a list of dictionaries. Each scene reference
        that is returned should be represented by a dictionary with three keys:

        - "node": The name of the 'node' that is to be operated on. Most DCCs have
          a concept of a node, path or some other way to address a particular
          object in the scene.
        - "type": The object type that this is. This is later passed to the
          update method so that it knows how to handle the object.
        - "path": Path on disk to the referenced object.

        Toolkit will scan the list of items, see if any of the objects matches
        any templates and try to determine if there is a more recent version
        available. Any such versions are then displayed in the UI as out of date.
        """
        if not mari.projects.current():
            # can't do anything if we don't have an open project!
            return []

        # find all geo in the current project using the engine utility method:
        mari_engine = self.parent.engine
        all_geo = mari_engine.list_geometry()

        # now, for all geo, find all versions:
        found_versions = []
        for geo in [g.get("geo") for g in all_geo]:

            # get all versions for this geo:
            all_geo_versions = mari_engine.list_geometry_versions(geo)

            # now find the publish path for the current version:
            current_version = geo.currentVersion()
            for geo_version, path in [
                (v["geo_version"], v.get("path")) for v in all_geo_versions
            ]:
                if geo_version == current_version:
                    # found the current version :)
                    found_versions.append(
                        {"node": geo.name(), "type": "geo", "path": path}
                    )
                    break

        return found_versions

    def update(self, items):
        """
        Perform replacements given a number of scene items passed from the app.

        Once a selection has been performed in the main UI and the user clicks
        the update button, this method is called.

        The items parameter is a list of dictionaries on the same form as was
        generated by the scan_scene hook above. The path key now holds
        the that each node should be updated *to* rather than the current path.
        """
        if not items:
            # nothing to do!
            return

        # update all geometry items:
        geo_items = [item for item in items if item.get("type") == "geo"]
        if geo_items:
            self._update_geometry_items(geo_items)

    def _update_geometry_items(self, items):
        """
        Update specified geo items in the current project

        :param items:    List of geometry items to update
        """
        mari_engine = self.parent.engine

        # set the geometry load options - default (None) uses the same options as the current
        # version of the geometry:
        options = None

        # first pass, find the publish details for all the paths of all the items
        # we need to update:
        all_paths = set([item["path"] for item in items])
        try:
            fields = ["id", "path", "version_number"]
            found_publishes = sgtk.util.find_publish(
                self.parent.sgtk, all_paths, fields=fields
            )
        except TankError as e:
            raise TankError(
                "Failed to query publishes from Flow Production Tracking: %s" % e
            )

        # now we have all the info we need to update geometry:
        for item in items:
            publish_path = item["path"]
            geo_name = item["node"]

            # find the publish details:
            sg_publish_data = found_publishes.get(publish_path)
            if not sg_publish_data:
                raise TankError(
                    "Failed to find PTR publish record for '%s'" % publish_path
                )

            # find geo in project:
            geo = mari.geo.find(geo_name)
            if not geo:
                raise TankError(
                    "Failed to find geometry '%s' in the current project" % geo_name
                )

            # check to see if this version is already loaded:
            already_loaded = False
            all_geo_versions = mari_engine.list_geometry_versions(geo)
            for geo_version, path in [
                (v["geo_version"], v.get("path")) for v in all_geo_versions
            ]:
                if path == publish_path:
                    # we already have this version laoded so just set it as current:
                    geo.setCurrentVersion(geo_version.name())
                    already_loaded = True
                    break

            if not already_loaded:
                # add the new version:
                new_version = mari_engine.add_geometry_version(
                    geo, sg_publish_data, options
                )
                if new_version:
                    geo.setCurrentVersion(new_version.name())

    def find_node(self, node_name):
        pass
