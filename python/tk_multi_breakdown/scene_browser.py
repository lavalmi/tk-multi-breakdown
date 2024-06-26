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
from sgtk.platform.qt import QtCore
from . import breakdown


browser_widget = sgtk.platform.import_framework("tk-framework-widget", "browser_widget")
shotgun_globals = sgtk.platform.import_framework(
    "tk-framework-shotgunutils", "shotgun_globals"
)

from .breakdown_list_item import BreakdownListItem


class SceneBrowserWidget(browser_widget.BrowserWidget):

    _item_work_completed = QtCore.Signal(str, object)
    _item_work_failed = QtCore.Signal(str, str)
    find_node = QtCore.Signal(str)

    def __init__(self, parent=None):
        browser_widget.BrowserWidget.__init__(self, parent)

    def _find_node_item_signal(self, node_name):
        self.find_node.emit(node_name)

    def get_data(self, data):
        items = breakdown.get_breakdown_items()
        return {
            "items": items,
            "show_red": data["show_red"],
            "show_green": data["show_green"],
        }

    def _make_row(self, first, second):
        return "<tr><td><b>%s</b>&nbsp;&nbsp;&nbsp;</td><td>%s</td></tr>" % (
            first,
            second,
        )

    def set_app(self, app):
        browser_widget.BrowserWidget.set_app(self, app)
        # For some reason connecting the worker signal directly to the child items' slots causes a
        # segmentation fault when there are many items. But re-emitting a local signal works fine
        self._worker.notifier.work_completed.connect(
            lambda uid, data: self._item_work_completed.emit(uid, data)
        )
        self._worker.notifier.work_failure.connect(
            lambda uid, msg: self._item_work_failed.emit(uid, msg)
        )

    def process_result(self, result):

        if len(result.get("items")) == 0:
            self.set_message("No versioned data in your scene!")
            return

        ################################################################################
        # PASS 1 - grouping
        # group these items into various buckets first based on type, and asset type
        groups = {}

        for d in result["items"]:

            if d.get("sg_data"):

                # publish in shotgun!
                sg_data = d["sg_data"]

                entity = sg_data.get("entity")
                if entity is None:
                    entity_type = "Unknown Type"
                else:
                    entity_type = shotgun_globals.get_type_display_name(entity["type"])

                asset_type = sg_data["entity.Asset.sg_asset_type"]

                if asset_type:
                    group = "%ss" % asset_type  # eg. Characters
                else:
                    group = "%ss" % entity_type  # eg. Shots

                # it is an asset, so group by asset type
                if group not in groups:
                    groups[group] = []
                groups[group].append(d)

            else:
                # everything not in shotgun goes into the other bucket
                OTHER_ITEMS = "Unpublished Items"
                if OTHER_ITEMS not in groups:
                    groups[OTHER_ITEMS] = []
                groups[OTHER_ITEMS].append(d)

        ################################################################################
        # PASS 2 - display the content of all groups

        if sgtk.util.get_published_file_entity_type(self._app.sgtk) == "PublishedFile":
            published_file_type_field = "published_file_type"
        else:  # == "TankPublishedFile"
            published_file_type_field = "tank_type"

        # now iterate through the groups
        for group in sorted(groups.keys()):

            i = self.add_item(browser_widget.ListHeader)
            i.set_title(group)
            for d in groups[group]:

                # item has a publish in sg
                i = self.add_item(BreakdownListItem)
                i.find_node_clicked.connect(self._find_node_item_signal)

                # provide a limited amount of data for receivers via the
                # data dictionary on
                # the item object
                i.data = {
                    "node_name": d["node_name"],
                    "node_type": d["node_type"],
                    "template": d["template"],
                    "fields": d["fields"],
                }

                # populate the description
                details = []

                if d.get("sg_data"):

                    sg_data = d["sg_data"]

                    details.append(
                        self._make_row(
                            "Item",
                            "%s, Version %d"
                            % (sg_data["name"], sg_data["version_number"]),
                        )
                    )

                    # see if this publish is associated with an entity
                    linked_entity = sg_data.get("entity")
                    if linked_entity:
                        display_name = shotgun_globals.get_type_display_name(
                            linked_entity["type"]
                        )

                        details.append(
                            self._make_row(display_name, linked_entity["name"])
                        )

                    # does it have a tank type ?
                    if sg_data.get(published_file_type_field):
                        details.append(
                            self._make_row(
                                "Type",
                                sg_data.get(published_file_type_field).get("name"),
                            )
                        )

                    details.append(self._make_row("Node", d["node_name"]))

                else:

                    details.append(self._make_row("Version", d["fields"]["version"]))

                    # display some key fields in the widget
                    # todo: make this more generic?
                    relevant_fields = ["Shot", "Asset", "Step", "Sequence", "name"]

                    for (k, v) in d["fields"].items():
                        # only show relevant fields - a bit of a hack
                        if k in relevant_fields:
                            details.append(self._make_row(k, v))

                    details.append(self._make_row("Node", d["node_name"]))

                inner = "".join(details)

                i.set_details("<table>%s</table>" % inner)

                # finally, ask the node to calculate its red-green status
                # this will happen asynchronously.
                i.calculate_status(
                    d["template"],
                    d["fields"],
                    result["show_red"],
                    result["show_green"],
                    d.get("sg_data"),
                )
