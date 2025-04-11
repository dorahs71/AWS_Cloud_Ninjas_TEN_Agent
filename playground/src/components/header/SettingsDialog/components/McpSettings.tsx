import { Input, Button, Select, Checkbox } from "antd"
import { InfoCircleOutlined, WarningFilled } from "@ant-design/icons"
import { SettingsState, SettingsAction } from "../hooks/useSettingsState"
import styles from "../index.module.scss"

interface McpSettingsProps {
    settings: SettingsState;
    dispatch: React.Dispatch<SettingsAction>;
    agentConnected: boolean;
    mcpLoading: boolean;
    onConnectMcp: () => void;
}

const McpSettings = ({
    settings,
    dispatch,
    agentConnected,
    mcpLoading,
    onConnectMcp
}: McpSettingsProps) => {
    return (
        <div className={styles.settingGroup}>
            <div className={styles.settingItem}>
                <div className={styles.desc}>
                    <span>MCP: Model Context Protocol. </span>
                    <span> Configure MCP following <a target="_blank" href="https://github.com/aws-samples/demo_mcp_on_amazon_bedrock">instructions here.</a></span>
                    {!settings.graphName.toLowerCase().includes('mcp') && (
                        <div className={styles.warn}>
                            <WarningFilled /> A MCP-enabled graph must be selected for MCP settings to take effect.
                        </div>
                    )}
                </div>
            </div>
            <div className={styles.settingItem}>
                <div className={styles.label}>MCP API Key</div>
                <Input
                    className={`${styles.input} dark`}
                    disabled={agentConnected}
                    value={settings.mcpApiKey}
                    placeholder="API key for MCP server"
                    onChange={e => dispatch({ type: 'SET_GENERAL', payload: { mcpApiKey: e.target.value } })}
                    style={{ flex: 1 }}
                    type="password"
                />
            </div>
            <div className={styles.settingItem}>
                <div className={styles.label}>MCP Server</div>
                <div className={styles.desc}>
                    <InfoCircleOutlined className={styles.infoIcon} /> URL of your MCP service, should be accessible from the Astra Agent server.
                </div>
                <div style={{ display: 'flex' }}>
                    <Input
                        className={`${styles.input} dark`}
                        disabled={agentConnected}
                        value={settings.mcpApiBase}
                        placeholder="http://localhost:7002"
                        onChange={e => dispatch({ type: 'SET_GENERAL', payload: { mcpApiBase: e.target.value } })}
                        style={{ flex: 1 }}
                    />
                    <Button
                        type={settings.mcpConnected ? "default" : "primary"}
                        disabled={agentConnected}
                        loading={mcpLoading}
                        style={{ marginLeft: '8px' }}
                        onClick={onConnectMcp}
                    >
                        {settings.mcpConnected ? "Refresh" : "Connect"}
                    </Button>
                </div>

                {settings.mcpConnected && settings.mcpModels.length > 0 && (
                    <div className={styles.settingItem} style={{ marginTop: '16px' }}>
                        <div className={styles.label}>MODEL</div>
                        <Select
                            disabled={agentConnected}
                            className={`${styles.select} dark`}
                            value={settings.mcpSelectedModel}
                            placeholder="Select a model"
                            options={settings.mcpModels.map(model => ({
                                label: model.model_name,
                                value: model.model_id
                            }))}
                            onChange={v => dispatch({ type: 'SET_GENERAL', payload: { mcpSelectedModel: v } })}
                        />
                    </div>
                )}

                {settings.mcpConnected && settings.mcpServers.length > 0 && (
                    <div className={styles.settingItem} style={{ marginTop: '16px' }}>
                        <div className={styles.label}>MCP SERVERS</div>
                        <div className={styles.serverList}>
                            {settings.mcpServers.map(server => (
                                <div key={server.server_id} className={styles.serverItem}>
                                    <Checkbox
                                        disabled={agentConnected}
                                        className={`${styles.checkbox} dark`}
                                        checked={settings.mcpSelectedServers.includes(server.server_id)}
                                        onChange={() => dispatch({ type: 'TOGGLE_MCP_SERVER', payload: server.server_id })}
                                    >
                                        {server.server_name}
                                    </Checkbox>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </div>
    )
}

export default McpSettings
