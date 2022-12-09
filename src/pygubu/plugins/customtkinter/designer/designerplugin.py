from pygubu.api.v1 import IPluginBase, IDesignerPlugin
from .preview import (
    CTkToplevelPreviewBO,
    CTkPreviewBO,
    CTkFramePreviewBO,
    CTkTabviewForPreviewBO,
)
from ..ctkbase import _plugin_uid


class CTkDesignerPlugin(IDesignerPlugin):
    def get_preview_builder(self, builder_uid: str):
        if builder_uid == f"{_plugin_uid}.CTkToplevel":
            return CTkToplevelPreviewBO
        if builder_uid == f"{_plugin_uid}.CTk":
            return CTkPreviewBO
        if builder_uid == f"{_plugin_uid}.CTkFrame":
            return CTkFramePreviewBO
        if builder_uid == f"{_plugin_uid}.CTkTabview":
            return CTkTabviewForPreviewBO
        return None

    def get_toplevel_preview_for(
        self, builder_uid: str, widget_id: str, builder, top_master
    ):
        top = None
        toplevel_uids = ("customtkinter.CTkToplevel", "customtkinter.CTk")
        if builder_uid in toplevel_uids:
            top = builder.get_object(widget_id)
        return top

    def configure_for_preview(self, builder_uid: str, widget):
        """Make widget just display with minimal functionality."""

        if not builder_uid.startswith(f"{_plugin_uid}."):
            return

        def _no_op(event=None):
            pass

        widget_canvas = widget._canvas
        if builder_uid.endswith(".CTKEntry"):
            seqlist = ("<FocusOut>", "<FocusIn>")
            for seq in seqlist:
                widget_canvas.bind(seq, _no_op)
        elif builder_uid.endswith(".CTkSlider"):
            seqlist = ("<Enter>", "<Leave>", "<Button-1>", "<B1-Motion>")
            for seq in seqlist:
                widget_canvas.bind(seq, _no_op)
        elif builder_uid.endswith(".CTkOptionMenu"):
            seqlist = ("<Enter>", "<Leave>", "<Button-1>")
            for seq in seqlist:
                widget_canvas.bind(seq, _no_op)
                widget._text_label.bind(seq, _no_op)
        elif builder_uid.endswith(".CTkComboBox"):
            widget_canvas.tag_bind("right_parts", "<Enter>", _no_op)
            widget_canvas.tag_bind("dropdown_arrow", "<Enter>", _no_op)
            widget_canvas.tag_bind("right_parts", "<Leave>", _no_op)
            widget_canvas.tag_bind("dropdown_arrow", "<Leave>", _no_op)
            widget_canvas.tag_bind("right_parts", "<Button-1>", _no_op)
            widget_canvas.tag_bind("dropdown_arrow", "<Button-1>", _no_op)
