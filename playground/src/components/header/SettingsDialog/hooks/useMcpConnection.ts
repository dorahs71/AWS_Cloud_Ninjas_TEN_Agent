import { useState } from "react"
import { message, Modal } from "antd"
import { apiMcpInfo } from "@/common"
import { SettingsState, SettingsAction } from "./useSettingsState"

export const useMcpConnection = (
    settings: SettingsState,
    dispatch: React.Dispatch<SettingsAction>
) => {
    const [isLoading, setIsLoading] = useState(false)

    // Helper function to normalize API base URL
    const normalizeApiBase = (apiBase: string) => {
        if (!apiBase) return ""

        // Remove trailing slash
        if (apiBase.endsWith('/')) {
            return apiBase.slice(0, -1)
        }
        return apiBase
    }

    // Helper function to handle API errors
    const handleApiError = (error: any, errorMessage: string) => {
        console.error(errorMessage, error)
        message.error(`${errorMessage}: ${error instanceof Error ? error.message : String(error)}`)
    }

    const connectToMcp = async () => {
        // Send GET request to http://mcpServer/v1/list/models
        if (!settings.mcpApiBase) {
            message.error("Please enter a valid MCP server URL")
            return
        }

        const normalizedApiBase = normalizeApiBase(settings.mcpApiBase)
        dispatch({ type: 'SET_GENERAL', payload: { mcpApiBase: normalizedApiBase } })

        setIsLoading(true)
        dispatch({ type: 'SET_GENERAL', payload: { mcpConnected: false } })

        try {
            const res = await apiMcpInfo(normalizedApiBase, settings.mcpApiKey, 'list/models')

            if (res?.code != 0) {
                Modal.error({
                    title: "Error",
                    content: `code:${res?.code},msg:${res?.msg}`
                })

                throw new Error(res?.msg)
            }

            if (res?.data?.models) {
                dispatch({ type: 'SET_MCP_MODELS', payload: res.data.models })
                dispatch({ type: 'SET_GENERAL', payload: { mcpConnected: true } })

                // Set the first model as selected if there's no previously selected model
                if (res.data.models.length > 0 && !settings.mcpSelectedModel) {
                    dispatch({
                        type: 'SET_GENERAL',
                        payload: { mcpSelectedModel: res.data.models[0].model_id }
                    })
                }

                message.success("Successfully connected to MCP server")
            } else {
                message.warning("Connected to MCP server but no models found")
                dispatch({ type: 'SET_MCP_MODELS', payload: [] })
                dispatch({ type: 'SET_GENERAL', payload: { mcpConnected: true } })
            }
        } catch (error) {
            handleApiError(error, "Failed to connect to MCP server")
            dispatch({ type: 'SET_MCP_MODELS', payload: [] })
            dispatch({ type: 'SET_GENERAL', payload: { mcpConnected: false } })
        } finally {
            setIsLoading(false)
        }
    }

    const listMcpServers = async () => {
        // Send GET request to http://{mcpServer}/v1/list/mcp_server
        if (!settings.mcpApiBase) {
            message.error("Please enter a valid MCP server URL")
            return
        }

        const normalizedApiBase = normalizeApiBase(settings.mcpApiBase)
        dispatch({ type: 'SET_GENERAL', payload: { mcpApiBase: normalizedApiBase } })

        try {
            const res = await apiMcpInfo(normalizedApiBase, settings.mcpApiKey, 'list/mcp_server')

            if (res?.code != 0) {
                Modal.error({
                    title: "Error",
                    content: `code:${res?.code},msg:${res?.msg}`
                })

                throw new Error(res?.msg)
            }

            if (res?.data?.servers) {
                dispatch({ type: 'SET_MCP_SERVERS', payload: res.data.servers })
            } else {
                message.warning("Connected to MCP server but no servers found")
            }
        } catch (error) {
            handleApiError(error, "Failed to connect to MCP server")
            dispatch({ type: 'SET_MCP_SERVERS', payload: [] })
        }
    }

    return {
        isLoading,
        connectToMcp,
        listMcpServers
    }
}
