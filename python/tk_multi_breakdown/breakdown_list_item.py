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
from sgtk.platform.qt import QtGui, QtCore

browser_widget = sgtk.platform.import_framework("tk-framework-widget", "browser_widget")

from .ui.item import Ui_Item


class BreakdownListItem(browser_widget.ListItem):
    """
    Custom list widget for displaying the breakdown status in the list view
    """
    find_node_clicked = QtCore.Signal(str)
    def __init__(self, app, worker, parent=None):
        """
        Construction
        """
        browser_widget.ListItem.__init__(self, app, worker, parent)

        self._green_pixmap = QtGui.QPixmap(":/res/green_bullet.png")
        self._red_pixmap = QtGui.QPixmap(":/res/red_bullet.png")
        self._latest_version = None
        self._is_latest = None
        self._browser = parent

    def _setup_ui(self):
        """
        Setup the Qt UI.  Typically, this just instantiates the UI class
        and calls its .setupUi(self) method.

        :returns:    The constructed UI
        """
        ui = Ui_Item()
        ui.setupUi(self)
        ui.btn_find_node.clicked.connect(self._on_find)
        return ui

    def _on_find(self):
        self.find_node_clicked.emit(self.data.get('node_name'))

    def get_latest_version_number(self):
        # returns none if not yet determined
        return self._latest_version

    def is_latest_version(self):
        # returns none if not yet determined
        return self._is_latest

    def is_out_of_date(self):
        # returns none if not yet determined
        if self._is_latest is None:
            return None
        else:
            return self._is_latest == False

    def calculate_status(
        self, template, fields, show_red, show_green, entity_dict=None
    ):
        """
        Figure out if this is a red or a green one. Also get thumb if possible
        """

        # we can only process stuff with a version
        if "version" not in fields:
            raise Exception("Fields must have a version!")

        # start spinner
        self._timer.start(100)

        # store data
        self._template = template
        self._fields = fields
        self._show_red = show_red
        self._show_green = show_green
        self._sg_data = entity_dict

        # kick off the worker!
        self._browser._item_work_completed.connect(self._on_worker_task_complete)
        self._browser._item_work_failed.connect(self._on_worker_failure)
        self._worker_uid = self._worker.queue_work(self._calculate_status, {})

    def _calculate_status(self, data):
        """
        The computational payload that downloads thumbnails and figures out the
        status for this item. This is run in a worker thread.
        """
        # set up the payload
        output = {}

        # First, calculate the thumbnail
        # see if we can download a thumbnail
        # thumbnail can be in any of the fields
        # entity.Asset.image
        # entity.Shot.image
        # entity.Scene.image
        # entity.Sequence.image
        if self._sg_data:

            thumb_url = self._sg_data.get("image")

            if thumb_url is not None:
                # input is a dict with a url key
                # returns a dict with a  thumb_path key
                ret = self._download_thumbnail({"url": thumb_url})
                if ret:
                    output["thumbnail"] = ret.get("thumb_path")
                else:
                    output["thumbnail"] = ":/res/no_thumb.png"
            else:
                output["thumbnail"] = ":/res/no_thumb.png"

        # first, get the latest available version for this item
        app = sgtk.platform.current_bundle()
        latest_version = app.execute_hook(
            "hook_get_version_number", template=self._template, curr_fields=self._fields
        )

        current_version = self._fields["version"]
        output["up_to_date"] = latest_version == current_version

        self._latest_version = latest_version
        self._is_latest = output["up_to_date"]

        return output

    def _on_worker_failure(self, uid, msg):

        if self._worker_uid != uid:
            # not our job. ignore
            return

        # finally, turn off progress indication and turn on display
        self._timer.stop()

        # show error message
        self._app.log_warning("Worker error: %s" % msg)

    def _on_worker_task_complete(self, uid, data):
        """
        Called when the computation is complete and we should update widget
        with the result
        """
        if uid != self._worker_uid:
            return

        # stop spin
        self._timer.stop()

        # set thumbnail
        if data.get("thumbnail"):
            self.ui.thumbnail.setPixmap(QtGui.QPixmap(data.get("thumbnail")))

        # set light - red or green
        if data["up_to_date"]:
            icon = self._green_pixmap
        else:
            icon = self._red_pixmap
        self.ui.light.setPixmap(icon)

        # figure out if this item should be hidden
        if data["up_to_date"] == True and self._show_green == False:
            self.setVisible(False)
        if data["up_to_date"] == False and self._show_red == False:
            self.setVisible(False)
