#
# This file is part of TEN Framework, an open source project.
# Licensed under the Apache License, Version 2.0.
# See the LICENSE file for more information.
#
from rte import (
    Addon,
    register_addon_as_extension,
    RteEnv,
)
from .extension import DifyExtension, EXTENSION_NAME
from .log import logger

@register_addon_as_extension(EXTENSION_NAME)
class DifyExtensionAddon(Addon):
    def on_create_instance(self, rte: RteEnv, name: str, context) -> None:
        logger.info("DifyExtensionAddon on_create_instance")
        rte.on_create_instance_done(DifyExtension(name), context)
