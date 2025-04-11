#
#
# Agora Real Time Engagement
# Created by XinHui Li in 2024.
# Copyright (c) 2024 Agora IO. All rights reserved.
#
#
from rte import (
    Addon,
    register_addon_as_extension,
    RteEnv,
)
from .extension import EXTENSION_NAME
from .log import logger
from .bedrock_mcp_extension import BedrockMcpExtension


@register_addon_as_extension(EXTENSION_NAME)
class BedrockMcpExtensionAddon(Addon):
    def on_create_instance(self, rte: RteEnv, addon_name: str, context) -> None:
        logger.info("on_create_instance")

        rte.on_create_instance_done(BedrockMcpExtension(addon_name), context)
